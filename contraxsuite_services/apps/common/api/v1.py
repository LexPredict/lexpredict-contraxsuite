"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""
# -*- coding: utf-8 -*-

import os

# Third-party imports
from typing import Any, List, Dict
import magic
from rest_framework import serializers, routers, viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions, AllowAny
from rest_framework.views import APIView

# Django imports
from django.conf.urls import url
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound

# Project imports
from apps.common.file_storage import get_filebrowser_site
from apps.common.mixins import JqListAPIMixin, JqListAPIView, APIFormFieldsMixin, SimpleRelationSerializer
from apps.common.models import Action, AppVar, ReviewStatusGroup, ReviewStatus, MenuGroup, MenuItem, \
    AppVarStorage, ProjectAppVar

from apps.common.permissions import SuperuserRequiredPermission
from apps.common.schemas import CustomAutoSchema, ObjectResponseSchema, JqFiltersListViewSchema, \
    ObjectToItemResponseMixin, string_content, binary_string_schema

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# WARN: Webdav may have long call listdir to bit directories, set simple_listdir=True in this case
file_storage = get_filebrowser_site(url_as_download=False).storage

python_magic = magic.Magic(mime=True)


# --------------------------------------------------------
# AppVar View - get system app var mapping (dict)
# --------------------------------------------------------


class ReadOnlyNonAdminPermission(IsAuthenticated, DjangoModelPermissions):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        return super().has_permission(request, view)    # should work for superusers only


class SystemAppVarAPIViewSchema(ObjectResponseSchema):
    get_parameters = [
        {'name': 'name',
         'in': 'query',
         'required': False,
         'description': 'App var name',
         'schema': {
             'type': 'string'}
         },
    ]

    def get_operation(self, path, method):
        op = super().get_operation(path, method)
        if method == 'GET':
            op['parameters'].extend(self.get_parameters)
        return op

    def get_responses(self, path, method):
        resp = super().get_responses(path, method)
        if method in ['POST']:
            resp = {
                '200': {
                    'content': {
                        'application/json': {
                            'schema': {'type': 'string'}}}}}
        return resp


class SystemAppVarDictAPIView(APIView):
    """
    Project-wide app vars as dict
    """
    schema = SystemAppVarAPIViewSchema()
    permission_classes = [AllowAny]
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        """
        Retrieve App Variable(s)\n
            Params:
                - name: str - retrieve specific variable
        """
        var_name = request.GET.get('name')
        name_contains = request.GET.get('name_contains')
        qs = AppVar.objects.filter(project_id=None)

        # deliver "Common" app-vars to unauth users, f.e. into login page, see users.authentication
        if not bool(request.user and request.user.is_authenticated):
            qs = qs.filter(access_type='all')
        elif not request.user.is_superuser:
            qs = qs.exclude(access_type='admin')

        if var_name:
            qs = qs.filter(name=var_name)
            if not qs.exists():
                return Response(status=404)
        if name_contains:
            qs = qs.filter(name__contains=name_contains)
            if not qs.exists():
                return Response(status=404)
        result = {i['name']: i['value'] for i in qs.values('name', 'value')}
        return Response(result)


# --------------------------------------------------------
# AppVar View - get system app var list
# --------------------------------------------------------

class AppVarSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppVar
        fields = ['category', 'name', 'value']


class SystemAppVarListAPIView(JqListAPIView):
    permission_classes = [AllowAny]
    queryset = AppVar.objects.filter(project_id=None).order_by('category', 'name')
    serializer_class = AppVarSerializer
    http_method_names = ['get']

    def get_queryset(self):
        qs = super().get_queryset()
        if not bool(self.request.user and self.request.user.is_authenticated):
            qs = qs.filter(access_type='all')
        elif not self.request.user.is_superuser:
            qs = qs.exclude(access_type='admin')
        return qs


# --------------------------------------------------------
# Project AppVar Views
# --------------------------------------------------------


class ProjectAppVarSerializer(serializers.Serializer):
    category = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    value = serializers.JSONField()
    access_type = serializers.CharField()
    use_system = serializers.BooleanField()
    system_value = serializers.JSONField()

    @classmethod
    def deserialize(cls, data: List[Dict[str, Any]]) -> List[ProjectAppVar]:
        """
        data is something like this:
        [{'category': 'Extract', 'name': 'simple_locator_tokenization', 'description': '...',
         'value': False, 'use_system': False, 'system_value': True}, ]
        """
        p_vars = []
        for raw in data:
            p_var = ProjectAppVar(category=raw.get('category'),
                                  name=raw.get('name'),
                                  access_type=raw.get('access_type', 'auth'),
                                  description=raw.get('description'),
                                  value=raw.get('value'),
                                  use_system=raw.get('use_system'),
                                  system_value=raw.get('system_value'))
            p_vars.append(p_var)
        return p_vars


class ProjectAppVarViewSchema(CustomAutoSchema):

    response_serializer = ProjectAppVarSerializer()
    request_serializer = ProjectAppVarSerializer()

    def get_operation(self, path, method):
        op = super().get_operation(path, method)
        if method == 'PUT':
            op['requestBody'] = self.get_request_body(path, method)
        return op

    def get_request_body(self, path, method):
        req = super().get_request_body(path, method)
        if method == 'PUT':
            return {
                'content': {
                    ct: {
                        'schema': {
                            'type': 'array',
                            'items': req['content'][ct]['schema']}
                    } for ct in self.request_media_types
                },
                'description': ''
            }
        return req

    def get_responses(self, path, method):
        if method == 'PUT':
            return {'200': string_content}
        return super().get_responses(path, method)


class ProjectAppVarPermission(IsAuthenticated):

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        project_id = view.kwargs.get('project_id')
        if project_id:
            from apps.project.models import Project
            project = Project.objects.get(pk=project_id)
            return request.user.has_perm('project.change_project', project)


class ProjectAppVarAPIView(APIView):
    """
    Based on custom AppVar model storage
    """
    permission_classes = [ProjectAppVarPermission]
    schema = ProjectAppVarViewSchema()
    http_method_names = ['get', 'put']
    serializer_class = ProjectAppVarSerializer
    action = 'list'    # need to make right schema - see rest_framework.schemas.utils.is_list_view

    def get(self, request, *args, **kwargs):
        project_id = kwargs['project_id']
        app_vars = AppVarStorage.get_project_app_vars(project_id, request.user)
        return Response(ProjectAppVarSerializer(app_vars, many=True).data)

    def put(self, request, *args, **kwargs):
        """
        Granular Create or Update Project App Variables
        Creates or Updates only passed project app vars
        Request data: [{'name': ..., 'category': ..., 'value': ...}, ... ]
        """
        project_id = kwargs['project_id']
        user_id = request.user.pk if request.user else None
        app_var_list = ProjectAppVarSerializer.deserialize(request.data)
        AppVarStorage.apply_project_app_vars(project_id, app_var_list, user_id)
        return Response('OK', status=status.HTTP_200_OK)


# --------------------------------------------------------
# ReviewStatusGroup Views
# --------------------------------------------------------

class ReviewStatusGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewStatusGroup
        fields = ['pk', 'name', 'code', 'order', 'is_active']


class ReviewStatusGroupViewSet(JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: ReviewStatusGroup List
    retrieve: Retrieve ReviewStatusGroup
    create: Create ReviewStatusGroup
    update: Update ReviewStatusGroup
    partial_update: Partial Update ReviewStatusGroup
    delete: Delete ReviewStatusGroup
    """
    queryset = ReviewStatusGroup.objects.all()
    serializer_class = ReviewStatusGroupSerializer
    permission_classes = [ReadOnlyNonAdminPermission]


# --------------------------------------------------------
# ReviewStatus Views
# --------------------------------------------------------

class ReviewStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReviewStatus
        fields = '__all__'


class ReviewStatusDetailSerializer(serializers.ModelSerializer):
    group_data = ReviewStatusGroupSerializer(source='group', many=False)

    class Meta:
        model = ReviewStatus
        fields = ['pk', 'name', 'code', 'order', 'group', 'group_data', 'is_active']


class ReviewStatusViewSet(JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: ReviewStatus List
    retrieve: Retrieve ReviewStatus
    create: Create ReviewStatus
    update: Update ReviewStatus
    partial_update: Partial Update ReviewStatus
    delete: Delete ReviewStatus
    """
    queryset = ReviewStatus.objects.select_related('group')
    serializer_class = ReviewStatusSerializer
    permission_classes = [ReadOnlyNonAdminPermission]

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ['retrieve', 'list']:
            return ReviewStatusDetailSerializer
        return ReviewStatusSerializer


# --------------------------------------------------------
# Action Views
# --------------------------------------------------------

class ActionSerializer(SimpleRelationSerializer):
    user_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Action
        fields = ['id', 'name', 'message', 'view_action',
                  'object_pk', 'model_name',
                  # 'content_type', 'object_str', 'app_label',
                  'date', 'user__name', 'user__initials', 'user_photo_url', 'request_data']

    def get_user_photo_url(self, obj):
        return obj.user.photo.url if obj.user and obj.user.photo else None
    get_user_photo_url.output_field = serializers.CharField()


class ActionViewSchema(JqFiltersListViewSchema):
    data = ActionSerializer(many=True)
    count_of_items = serializers.IntegerField()
    count_of_filtered_items = serializers.IntegerField()

    parameters = [
        {'name': 'project_id',
         'in': 'query',
         'required': False,
         'description': 'Project ID',
         'schema': {
             'type': 'integer'}
         },
        {'name': 'document_id',
         'in': 'query',
         'required': False,
         'description': 'Document ID',
         'schema': {
             'type': 'integer'}
         },
        {'name': 'view_actions',
         'in': 'query',
         'required': False,
         'description': 'Action names',
         'schema': {
             'type': 'array',
             'items': {'type': 'string'}}
         },
    ]


class ActionViewSet(JqListAPIMixin, viewsets.ReadOnlyModelViewSet):
    """
    list: Action List
    retrieve: Retrieve Action
    """
    queryset = Action.objects.select_related('user', 'content_type')
    serializer_class = ActionSerializer
    schema = ActionViewSchema()
    permission_classes = [IsAuthenticated, DjangoModelPermissions]    # should work for superusers only

    def get_queryset(self):
        qs = super().get_queryset()
        self.kwargs.update(self.request.GET.dict())
        if 'project_id' in self.kwargs:
            from apps.document.models import Document
            filter_cond = Q(object_pk=self.kwargs['project_id'], model_name='Project')
            if self.kwargs.get('get_document_actions', False):
                # Filter project documents actions too
                related_documents_id = list(map(str, Document.objects.filter(
                    project_id=self.kwargs['project_id']).values_list('id', flat=True)))
                if related_documents_id:
                    filter_cond |= Q(object_pk__in=related_documents_id, model_name='Document')
            qs = qs.filter(filter_cond)
        elif 'document_id' in self.kwargs:
            qs = qs.filter(object_pk=self.kwargs['document_id'], model_name='Document')
        if 'view_actions' in self.kwargs:
            qs = qs.filter(view_action__in=self.kwargs['view_actions'])
        return qs.order_by('-date')

    def get_extra_data(self, queryset, initial_queryset):
        data = super().get_extra_data(queryset, initial_queryset)
        data['count_of_filtered_items'] = queryset.count()
        data['count_of_items'] = initial_queryset.count()
        return data

    # def get_extra_data(self, queryset, initial_queryset):
    #     init_action_name = self.kwargs.get('init_action')
    #     if init_action_name is not None:
    #         init_action = initial_queryset.filter(view_action=init_action_name).last()
    #     else:
    #         init_action = initial_queryset.last()
    #     init_action = ActionSerializer(init_action).data if init_action else None
    #     last_action = initial_queryset.first()
    #     last_action = ActionSerializer(last_action).data if last_action else None
    #     return {'init_action': init_action, 'last_action': last_action}


# --------------------------------------------------------
# MenuGroup Views
# --------------------------------------------------------

class MenuItemPermissions(IsAuthenticated, DjangoModelPermissions):

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if not request.user.is_superuser:
            return obj.user == request.user and not obj.public
        return True


class MenuGroupSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = MenuGroup
        fields = ['pk', 'name', 'public', 'order', 'user']

    def validate_public(self, value):
        if not self.context['request'].user.is_superuser and value is True:
            raise ValidationError('Non-admin users cannot create public link groups.')
        return value


class MenuGroupViewSet(APIFormFieldsMixin, viewsets.ModelViewSet):
    """
    list: MenuGroup List
    retrieve: Retrieve MenuGroup
    create: Create MenuGroup
    update: Update MenuGroup
    partial_update: Partial Update MenuGroup
    delete: Delete MenuGroup
    """
    permission_classes = [MenuItemPermissions]
    serializer_class = MenuGroupSerializer

    def get_queryset(self):
        qs = MenuGroup.objects.all()
        if not self.request.user.is_superuser:
            qs = qs.filter(Q(public=False, user=self.request.user) |
                           Q(public=True))
        return qs


# --------------------------------------------------------
# MenuItem Views
# --------------------------------------------------------

class MenuItemSerializer(MenuGroupSerializer):

    class Meta:
        model = MenuItem
        fields = ['pk', 'name', 'url', 'group', 'public', 'order', 'user']


class MenuItemViewSet(MenuGroupViewSet):
    """
    list: MenuItem List
    retrieve: Retrieve MenuItem
    create: Create MenuItem
    update: Update MenuItem
    partial_update: Partial Update MenuItem
    delete: Delete MenuItem
    """
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        qs = MenuItem.objects.select_related('group')
        if not self.request.user.is_superuser:
            qs = qs.filter(Q(public=False, user=self.request.user) |
                           Q(public=True)) \
                .filter(Q(group__public=False, group__user=self.request.user) |
                        Q(group__public=True) |
                        Q(group__isnull=True))
        return qs


class MediaFilesAPIViewSchema(ObjectResponseSchema):
    get_parameters = [
        {'name': 'action',
         'in': 'query',
         'required': False,
         'description': 'Action name',
         'schema': {
             'type': 'string',
             "enum": [
                 "info",
                 "download"
             ],
             'default': 'download'},
         }
    ]

    def get_operation(self, path, method):
        op = super().get_operation(path, method)
        if method == 'GET':
            op['parameters'].extend(self.get_parameters)
        return op

    def get_responses(self, path, method):
        res = super().get_responses(path, method)
        # response = {
        #     '200': {
        #         'content': {
        #             'application/json': {
        #                 'schema': ObjectResponseSchema.object_schema
        #             }
        #         }
        #     }
        # }
        res['200']['content']['*/*'] = binary_string_schema
        return res


class MediaFilesPermission(SuperuserRequiredPermission):
    """
    Allows access only to superusers except user photos
    """
    def has_permission(self, request, view):
        try:
            path = view.kwargs['path']
            media_dir = os.path.normpath(path).lstrip(os.path.sep).split(os.path.sep)[1]
            if media_dir in view.free_media_folders:
                return True
        except:
            pass
        return request.user and request.user.is_superuser


class MediaFilesAPIView(APIView):
    permission_classes = [MediaFilesPermission]
    http_method_names = ['get']
    schema = MediaFilesAPIViewSchema()
    free_media_folders = ['photo', 'logo']

    def get(self, request, path):
        """
        If directory:
          action: None: - list directory
          action: download - list directory (TODO - download directory)
          action: info: - dict(info about directory)
        If file:
          action: None: - show file
          action: download - download file
          action: info: - dict(info about directory)

        :param request:
        :param path: str - relative path in /media directory

        :query param action: optional str ["download", "info"]
        :return:
        """
        action = request.GET.get('action', '')

        if not file_storage.exists(path):
            return HttpResponseNotFound()

        is_dir = file_storage.isdir(path)
        if action == 'info':
            return self.info(path, is_dir)

        if is_dir:
            return Response(file_storage.listdir(path))

        as_attachment = action == 'download'
        return self.download(path, as_attachment=as_attachment)

    @staticmethod
    def download(path, as_attachment=False):
        file_name = os.path.basename(path)
        content = file_storage.open(path).read()
        mimetype = python_magic.from_buffer(content)
        response = HttpResponse(content_type=mimetype)
        disposition_type = 'attachment' if as_attachment else 'inline'
        response['Content-Disposition'] = '{}; filename="{}"'.format(disposition_type, file_name)
        response.write(content)
        return response

    @staticmethod
    def info(path, is_dir):
        data = {
            'name': os.path.basename(path),
            'path': path,
            'url': file_storage.url(path),
            'type': 'directory' if is_dir else 'file',
            'size': file_storage.size(path),
            'created': file_storage.get_created_time(path),
            'modified': file_storage.get_modified_time(path)}
        return Response(data)


class LogoAPIView(MediaFilesAPIView):
    permission_classes = [AllowAny]
    http_method_names = ['get']
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        from apps.common.app_vars import CUSTOM_LOGO_URL
        path = CUSTOM_LOGO_URL.val()

        if not path or not file_storage.exists(path) or file_storage.isdir(path):
            return HttpResponseNotFound()

        return self.download(path, as_attachment=False)


router = routers.DefaultRouter()
router.register(r'actions', ActionViewSet, 'actions')
router.register(r'review-status-groups', ReviewStatusGroupViewSet, 'review-status-group')
router.register(r'review-statuses', ReviewStatusViewSet, 'review-status')
router.register(r'menu-groups', MenuGroupViewSet, 'menu-group')
router.register(r'menu-items', MenuItemViewSet, 'menu-item')

urlpatterns = [
    url(
        r'^app-variables/$',
        SystemAppVarDictAPIView.as_view(),
        name='app-variables'
    ),
    url(
        r'^app-variables/list/$',
        SystemAppVarListAPIView.as_view(),
        name='app-variables-list'
    ),
    url(
        r'^app-variables/project/(?P<project_id>\d+)/$',
        ProjectAppVarAPIView.as_view(),
        name='project-app-variables'
    ),
    url(
        r'^media/(?P<path>.+)/$',
        MediaFilesAPIView.as_view(),
        name='media'
    ),
    url(
        r'^logo/$',
        LogoAPIView.as_view(),
        name='logo'
    ),

]
