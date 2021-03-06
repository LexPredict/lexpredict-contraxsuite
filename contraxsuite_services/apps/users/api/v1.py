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

from django.conf import settings
from django.conf.urls import url
from django.db.models import Count, F, Q, Case, When, DecimalField
from django.contrib.postgres.aggregates import StringAgg

# Third-party imports
import coreapi
import coreschema
from guardian.shortcuts import get_objects_for_user
from rest_framework import routers, viewsets, serializers, views, schemas
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions, AllowAny
from rest_framework.response import Response

# Project imports
from apps.common.mixins import JqListAPIMixin, SimpleRelationSerializer, APIFormFieldsMixin
from apps.common.schemas import CustomAutoSchema, ObjectToItemResponseMixin, string_schema
from apps.users.models import User, Role

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# --------------------------------------------------------
# Role View
# --------------------------------------------------------

class RoleSerializer(SimpleRelationSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'abbr', 'order',
                  'is_admin', 'is_top_manager', 'is_manager', 'is_reviewer']


class RoleViewSet(JqListAPIMixin, viewsets.ModelViewSet):
    """
    list: Role List
    create: Create Role
    retrieve: Retrieve Role
    update: Update Role
    partial_update: Partial Update Role
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    http_method_names = ['get', 'post', 'put', 'patch']
    permission_classes = [DjangoModelPermissions]


# --------------------------------------------------------
# User View
# --------------------------------------------------------

class UserSerializer(SimpleRelationSerializer):
    role_data = RoleSerializer(source='role', many=False, required=False)
    photo = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name',
                  'email', 'is_superuser', 'is_staff', 'is_active',
                  'name', 'role', 'role_data', 'organization', 'photo', 'permissions', 'groups']

    def get_photo(self, obj):
        return obj.photo.url if obj.photo else None

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_permissions(self, obj):
        view_documenttype_stats = obj.has_perm('document.view_documenttype_stats')
        view_documentfield_stats = obj.has_perm('document.view_documentfield_stats')
        view_project_stats = obj.has_perm('project.view_project_stats')
        view_user_stats = obj.has_perm('users.view_user_stats')
        view_stats = any([view_documenttype_stats, view_documentfield_stats,
                          view_project_stats, view_user_stats])

        return {
            'add_project': obj.has_perm('project.add_project'),

            'add_documenttype': obj.has_perm('document.add_documenttype'),
            'import_documenttype': obj.has_perm('document.import_documenttype'),
            'view_documenttype': get_objects_for_user(obj, 'document.view_documenttype').exists(),

            'view_documenttype_stats': view_documenttype_stats,
            'view_documentfield_stats': view_documentfield_stats,
            'view_project_stats': view_project_stats,
            'view_user_stats': view_user_stats,
            'view_stats': view_stats,

            'view_explorer': obj.has_perm('users.view_explorer'),
        }
    get_permissions.output_field = serializers.DictField(child=serializers.BooleanField())


class UserProfileSerializer(UserSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['groups'].read_only = True
        self.fields['username'].label = 'Login'

    class Meta:
        model = User
        fields = ['username', 'last_name', 'first_name', 'name',
                  'email', 'organization', 'groups']
        read_only_fields = ('username', 'email')


class UserStatsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_name = serializers.CharField()
    role_name = serializers.CharField(allow_null=True)
    group_name = serializers.CharField(allow_null=True)
    total_projects = serializers.IntegerField()
    documents_assigned = serializers.IntegerField()
    documents_completed = serializers.IntegerField()
    documents_todo = serializers.IntegerField()
    documents_completed_pcnt = serializers.FloatField()
    documents_todo_pcnt = serializers.FloatField()
    clauses_assigned = serializers.IntegerField()
    clauses_completed = serializers.IntegerField()
    clauses_todo = serializers.IntegerField()
    clauses_completed_pcnt = serializers.FloatField()
    clauses_todo_pcnt = serializers.FloatField()


class UserStatsSchema(ObjectToItemResponseMixin, CustomAutoSchema):
    response_serializer = UserStatsSerializer()


class UserViewSetPermission(DjangoModelPermissions):
    """
    Gives access ещ user API
    """
    def has_permission(self, request, view):
        if view.action in ['retrieve', 'update', 'partial_update']:
            return True
        if view.action == 'user_stats':
            return request.user.has_perm('users.view_user_stats')
        return super().has_permission(request, view)


class UserViewSet(JqListAPIMixin, APIFormFieldsMixin, viewsets.ModelViewSet):
    """
    list: User List
    create: Create User
    retrieve: Retrieve User
    update: Update User
    partial_update: Partial Update User
    """
    queryset = User.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch']
    permission_classes = [UserViewSetPermission]
    options_serializer = UserProfileSerializer

    def get_serializer_class(self):
        if self.action == 'user_stats':
            return UserStatsSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return UserProfileSerializer
        return UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.exclude(id=User.get_anonymous().id).prefetch_related('groups')

    @action(detail=False, methods=['get'], schema=UserStatsSchema())
    def user_stats(self, request, **kwargs):
        """
        User stats: projects, document types, tasks
        """
        # TODO: being splitted, this QS takes low time to run, otherwise it hangs on large DB
        # pros: time;
        # cons: we cannot use server-side filtering/sorting/pagination
        # tried Subquery on FieldAnnotations, but it slows down query in 3-5 times
        qs = self.get_queryset()
        qs1 = qs.annotate(
            user_name=F('name'),
            role_name=F('role__name'),
            group_name=StringAgg('groups__name', delimiter=', ', distinct=True),
            total_projects=Count('project_junior_reviewers', distinct=True) +
                           Count('project_reviewers', distinct=True) +
                           Count('project_owners', distinct=True),

            documents_assigned=Count('document', distinct=True),
            documents_completed=Count('document',
                                      filter=Q(document__status__is_active=False),
                                      distinct=True),
            documents_todo=F('documents_assigned') - F('documents_completed'),

            documents_completed_pcnt=Case(
                When(documents_assigned=0, then=0),
                default=100.0 * F('documents_completed') / F('documents_assigned'),
                output_field=DecimalField(max_digits=5, decimal_places=2)),
            documents_todo_pcnt=Case(
                When(Q(documents_assigned=0), then=0),
                default=100.0 * F('documents_todo') / F('documents_assigned'),
                output_field=DecimalField(max_digits=5, decimal_places=2)),
        ).values('id', 'user_name', 'role_name', 'group_name', 'total_projects',
                 'documents_assigned', 'documents_completed', 'documents_todo',
                 'documents_completed_pcnt', 'documents_todo_pcnt')

        qs2 = qs.annotate(
                clauses_assigned=Count('field_annotations', distinct=True) +
                                 Count('annotation_false_matches', distinct=True),
                clauses_todo=Count('field_annotations',
                                   filter=Q(field_annotations__status__code='unreviewed'),
                                   distinct=True),
                clauses_completed=F('clauses_assigned') - F('clauses_todo'),

                clauses_completed_pcnt=Case(
                    When(Q(clauses_assigned=0), then=0),
                    default=100.0 * F('clauses_completed') / F('clauses_assigned'),
                    output_field=DecimalField(max_digits=5, decimal_places=2)),
                clauses_todo_pcnt=Case(
                    When(Q(clauses_assigned=0), then=0),
                    default=100.0 * F('clauses_todo') / F('clauses_assigned'),
                    output_field=DecimalField(max_digits=5, decimal_places=2)),
        ).values('id', 'clauses_assigned', 'clauses_todo',  'clauses_completed',
                 'clauses_completed_pcnt', 'clauses_todo_pcnt')

        qs = {i['id']: i for i in qs1}
        for i in qs2:
            qs[i['id']].update(i)

        return Response(list(qs.values()))


# --------------------------------------------------------
# VerifyAuthToken View
# --------------------------------------------------------

class VerifyAuthTokenAPIViewSchema(CustomAutoSchema):

    class VerifyAuthTokenRequestSerializer(serializers.Serializer):
        auth_token = serializers.CharField(max_length=40, required=True)

    class VerifyAuthTokenResponseSerializer(serializers.Serializer):
        key = serializers.CharField()
        user_name = serializers.CharField()
        release_version = serializers.CharField()
        user = UserSerializer()

    request_serializer = VerifyAuthTokenRequestSerializer()
    response_serializer = VerifyAuthTokenResponseSerializer()

    def get_responses(self, path, method):
        resp = super().get_responses(path, method)
        resp['403'] = string_schema
        return resp


class VerifyAuthTokenAPIView(views.APIView):

    authentication_classes = []
    permission_classes = [AllowAny]
    http_method_names = ['post']
    schema = VerifyAuthTokenAPIViewSchema()

    @property
    def coreapi_schema(self):
        fields = [
            coreapi.Field(
                "auth_token",
                required=True,
                location="form",
                schema=coreschema.String(max_length=40),
            )]
        return schemas.ManualSchema(fields=fields)

    def post(self, request, *args, **kwargs):
        """
        Get user data for provided auth_token.
        """
        auth_token = request.POST.get('auth_token') or request.data.get('auth_token') \
            or request.META.get('HTTP_AUTH_TOKEN')
        if not auth_token and request.COOKIES:
            auth_token = request.COOKIES.get('auth_token').replace('Token ', '')
        from apps.users.authentication import CookieAuthentication

        try:
            tok_usr, _tok = CookieAuthentication().authenticate_credentials(auth_token)
        except Exception as e:
            raise e

        if tok_usr:
            resp_data = {
                'key': auth_token,
                'user_name': tok_usr.username,
                'user': UserSerializer(tok_usr).data,
                'release_version': settings.VERSION_NUMBER }
            return Response(resp_data)
        return Response()


router = routers.DefaultRouter()
router.register('users', UserViewSet, 'user')
router.register('roles', RoleViewSet, 'role')


urlpatterns = [
    url('verify-token/', VerifyAuthTokenAPIView.as_view(), name='verify-token'),
]
