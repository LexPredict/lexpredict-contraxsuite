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

from guardian.shortcuts import get_users_with_perms

from apps.project.models import Project
from apps.websocket import channel_message_types as message_types
from apps.websocket.channel_message import ChannelMessage
from apps.websocket.websockets import Websockets

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def notify_build_vectors_completed(project_ids, task, task_status):
    """
    Notify users about completed BuildDocumentVectorsTask/BuildTextUnitVectorsTask
    """
    for project in Project.objects.filter(pk__in=project_ids).only('pk'):
        users_to_notify = get_users_with_perms(project, only_with_perms_in=['project.change_project'])
        data = {'project_ids': project_ids,
                'project_id': project_ids[0] if project_ids and len(project_ids) == 1 else project_ids,
                'task_id': task.id,
                'task_name': task.name,
                'task_status': task_status}
        message = ChannelMessage(message_types.CHANNEL_MSG_TYPE_CREATE_VECTORS_COMPLETED, data)
        Websockets().send_to_users(qs_users=users_to_notify, message_obj=message)
