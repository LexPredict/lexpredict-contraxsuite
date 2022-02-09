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

# Django imports
from rest_framework import routers, viewsets, serializers, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Project imports
from apps.common.mixins import APILoggingMixin, JqListAPIMixin
from apps.common.schemas import ObjectResponseSchema
from apps.notifications.models import WebNotification, WebNotificationMessage, WebNotificationTypes
from apps.notifications.schemas import MarkForSeenWebNotificationSchema, \
    MarkForSeenWebNotificationRequestSerializer

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class WebNotificationMessageDetailSerializer(serializers.ModelSerializer):
    message_template = serializers.SerializerMethodField()

    class Meta:
        model = WebNotificationMessage
        fields = ['id', 'message_data', 'message_template', 'created_date', 'notification_type',
                  'redirect_link']

    def get_message_template(self, obj):
        return obj.get_notification_message_template()

    get_message_template.output_field = serializers.CharField(allow_null=True)


class WebNotificationDetailSerializer(serializers.ModelSerializer):
    notification = WebNotificationMessageDetailSerializer(many=False, read_only=True)

    class Meta:
        model = WebNotification
        fields = ['is_seen', 'notification']


class WebNotificationViewSet(APILoggingMixin,
                             JqListAPIMixin,
                             mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    """
    list: Web Notification List
    """
    queryset = WebNotification.objects.all()
    schema = ObjectResponseSchema()
    permission_classes = [IsAuthenticated]
    track_view_actions = ['mark_seen', 'unmark_seen']

    def get_queryset(self):
        return super().get_queryset().filter(
            recipient=self.request.user).select_related('notification').order_by(
            '-notification__created_date')

    def get_extra_data(self, qs, initial_qs):
        data = super().get_extra_data(qs, initial_qs)
        data['count_of_filtered_items'] = qs.count()
        data['count_of_items'] = WebNotification.objects.filter(recipient=self.request.user).count()
        return data

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'GET':
            return WebNotificationDetailSerializer
        return MarkForSeenWebNotificationRequestSerializer

    @action(detail=False, methods=['post'], schema=MarkForSeenWebNotificationSchema())
    def mark_seen(self, request, **kwargs):
        """
        Method marks a number of web notifications for updating as seen/not seen.
        :param request: provide a list of web notification message ids here:
        notification_ids: [...], provide a boolean value whether notification was seen
        by user: is_seen: True/False
        :param kwargs:
        :return: OK or 404
        """
        ids = request.data.get('notification_ids', [])
        is_seen = request.data.get('is_seen', True)
        if not ids:
            count_processed = self.get_queryset().update(is_seen=is_seen)
        else:
            count_processed = self.get_queryset().filter(notification__id__in=ids).update(
                is_seen=is_seen)
        return Response({"count_processed": count_processed},
                        status=200 if count_processed else 404)


main_router = routers.DefaultRouter()
main_router.register(r'web-notifications', WebNotificationViewSet, 'web-notification')

api_routers = [main_router]
