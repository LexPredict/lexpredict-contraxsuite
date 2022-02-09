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

from django.db.models import Q
from django.utils.timezone import now

from apps.task.models import Task, User
from apps.websocket import channel_message_types as message_types
from apps.websocket.channel_message import ChannelMessage
from apps.websocket.websockets import Websockets

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def notify_similarity_task_completed(project_id, user_id, task_id, task_name, run_id, item_id, task_status):
    """
    Notify users about completed DocumentSimilarityByFeatures/TextUnitSimilarityByFeatures task
    """
    data = {'project_id': project_id,
            'task_id': task_id,
            'task_name': task_name,
            'task_status': task_status,
            'run_id': run_id,
            'item_id': item_id}
    message = ChannelMessage(message_types.CHANNEL_MSG_TYPE_DETECT_SIMILARITY_COMPLETED, data)
    Websockets().send_to_user(user_id, message_obj=message)
    # set parent task status/progress/date_done as FE renews task grid and parent task should be actual
    Task.objects.filter(pk=task_id).update(status=task_status, progress=100, date_done=now())


def notify_delete_similarity_completed(task, task_status):
    """
    Notify users about completed DeleteDocumentSimilarityResults/DeleteTextUnitSimilarityResults task
    """
    project_id = task.kwargs['project_id']
    data = {'project_id': project_id,
            'run_id': task.kwargs.get('run_id'),
            'task_id': task.id,
            'task_name': task.name,
            'task_status': task_status}
    task_qs = Task.objects.filter(name=task.name)
    task_qs = task_qs.filter(Q(kwargs__project=int(project_id)) |
                             Q(kwargs__project=str(project_id)) |
                             Q(project_id=project_id))
    user_ids = task_qs.values_list('user_id', flat=True)
    user_qs = User.objects.filter(id__in=user_ids)

    message = ChannelMessage(message_types.CHANNEL_MSG_TYPE_DELETE_SIMILARITY_COMPLETED, data)
    Websockets().send_to_users(user_qs, message_obj=message)
