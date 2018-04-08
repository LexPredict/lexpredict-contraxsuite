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

import json

# Third-party imports
from constance.admin import ConstanceForm, get_values
from rest_framework import serializers, routers, viewsets
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView

# Django imports
from django.conf.urls import url
from apps.common.models import AppVar, ReviewStatus
from apps.common.mixins import JqMixin

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.8/LICENSE"
__version__ = "1.0.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class AppConfigAPIView(APIView):

    def get(self, request, *args, **kwargs):
        """
        Retrieve App Config
        """
        initial = get_values()
        initial['data'] = json.loads(initial['data'])
        return Response(initial)

    def post(self, request, *args, **kwargs):
        """
        Update App Config\n
            Params:
                - auto_login: bool
                - standard_optional_locators: list[str], see settings.OPTIONAL_LOCATORS
                - data: json, - custom settings for project
        """
        initial = get_values()
        data = initial.copy()
        data.update(request.data)
        if 'data' in data:
            data['data'] = json.dumps(data['data'])
        form = ConstanceForm(data=data, initial=initial)
        form.data['version'] = initial.get('version')
        if form.is_valid():
            form.save()
            return Response('Application settings updated successfully.')
        else:
            return Response(form.errors, status=500)


class AppConfigDataAPIView(APIView):

    def get(self, request, *args, **kwargs):
        """
        Retrieve App Config data
        """
        initial = get_values()
        result = json.loads(initial['data'])
        param = request.GET.get('param')
        if param:
            result = {param: result.get(param)}
        return Response(result)

    def post(self, request, *args, **kwargs):
        """
        Update App Config data\n
            Params:
                dictionary {key1: val2, key2: val2, ...} - json, custom settings for project
        """
        initial_config = get_values()

        data = json.loads(initial_config['data'])
        data.update(request.data)

        updated_config = initial_config.copy()
        updated_config['data'] = json.dumps(data)

        form = ConstanceForm(data=updated_config, initial=initial_config)
        form.data['version'] = initial_config.get('version')
        if form.is_valid():
            form.save()
            return Response('Application settings updated successfully.')
        else:
            return Response(form.errors, status=500)

    def delete(self, request, *args, **kwargs):
        """
        Delete specific key from App Config data
        """
        initial_config = get_values()
        param = request.data.get('param')

        if not param:
            raise APIException('Provide key to delete')

        data = json.loads(initial_config['data'])
        data.pop(param, None)
        updated_config = initial_config.copy()
        updated_config['data'] = json.dumps(data)

        form = ConstanceForm(data=updated_config, initial=initial_config)
        form.data['version'] = initial_config.get('version')
        if form.is_valid():
            form.save()
            return Response('OK')
        else:
            return Response(form.errors, status=500)


class AppVarAPIView(APIView):

    def get(self, request, *args, **kwargs):
        """
        Retrieve App Variable(s)\n
            Params:
                - name: str - retrieve specific variable
        """
        var_name = request.GET.get('name')
        if var_name:
            result = AppVar.get(var_name)
            if not result:
                return Response(status=404)
        else:
            result = list(AppVar.objects.values('name', 'value'))
            result = {i['name']: i['value'] for i in result}
        return Response(result)

    def post(self, request, *args, **kwargs):
        """
        Create or update App Variables\n
            Params:
                key1: val1,
                key2: val2, etc
        """
        data = request.data
        for var_name, value in data.items():
            AppVar.set(var_name, value)
        return Response('Application settings updated successfully.')

    def delete(self, request, *args, **kwargs):
        """
        Delete specific App Variable by name
            Param:
                - name: str
        """
        var_name = request.data.get('name')

        if not var_name:
            raise APIException('Provide variable name to delete')

        AppVar.clear(var_name)
        return Response('OK')


# --------------------------------------------------------
# ReviewStatus Views
# --------------------------------------------------------

class ReviewStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewStatus
        fields = ['pk', 'name', 'code', 'order']


class ReviewStatusViewSet(JqMixin, viewsets.ModelViewSet):
    """
    list: ReviewStatus List\n
        GET params:
            - name: str
            - name_contains: str
            - code: str
            - code_contains: str
    retrieve: Retrieve ReviewStatus
    create: Create ReviewStatus
    update: Update ReviewStatus
    partial_update: Partial Update ReviewStatus
    delete: Delete ReviewStatus
    """
    queryset = ReviewStatus.objects.all()
    serializer_class = ReviewStatusSerializer

router = routers.DefaultRouter()
router.register(r'review-statuses', ReviewStatusViewSet, 'review-status')

urlpatterns = [
    url(r'^app-config/$', AppConfigAPIView.as_view(),
        name='app-config'),
    url(r'^app-config-data/$', AppConfigDataAPIView.as_view(),
        name='app-config-data'),
    url(r'^app-variables/$', AppVarAPIView.as_view(),
        name='app-variables'),
]