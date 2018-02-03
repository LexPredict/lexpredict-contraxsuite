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

# Third-party imports
from rest_framework import routers, serializers, viewsets

# Django imports
from django.core.urlresolvers import reverse

# Project imports
from apps.task.models import Task


# Serializers define the API representation.
class TaskSerializer(serializers.HyperlinkedModelSerializer):
    user__username = serializers.CharField(
        source='user.username',
        read_only=True)
    url = serializers.SerializerMethodField()
    purge_url = serializers.SerializerMethodField()
    result_links = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['pk', 'name', 'date_start', 'user__username',
                  'date_done', 'progress', 'time', 'status', 'has_error',
                  'url', 'purge_url', 'result_links', 'description']

    def get_url(self, obj):
        return reverse('task:task-detail', args=[obj.pk])

    def get_purge_url(self, obj):
        return reverse('task:purge-task') + '?task_pk={}'.format(obj.pk)

    def get_result_links(self, obj):
        result = []
        if obj.metadata:
            result_links = obj.metadata.get('result_links', [])
            for link_data in result_links:
                link_data['link'] = reverse(link_data['link'])
            result = result_links
        return result

    def get_description(self, obj):
        result = None
        if obj.metadata:
            result = obj.metadata.get('description')
        return result


class TaskViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list: Task List
    retrieve: Retrieve Task
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


router = routers.DefaultRouter()
router.register(r'list', TaskViewSet, 'task')
