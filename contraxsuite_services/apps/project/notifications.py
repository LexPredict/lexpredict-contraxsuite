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

from typing import List

from django.db.models import Q, F
from celery.states import READY_STATES

from apps.users.models import User
from apps.project.models import UploadSession
from apps.websocket import channel_message_types as message_types
from apps.websocket.channel_message import ChannelMessage
from apps.websocket.websockets import Websockets

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def notify_active_upload_sessions(sessions: List[UploadSession]):
    """
    Notify users about active upload sessions to show/track progress
    """
    data = []
    for session in sessions:
        progress = session.document_tasks_progress_total
        document_progress_details = session.document_tasks_progress()
        all_documents = len(document_progress_details)
        processed_documents = sum([1 for k, v in document_progress_details.items() if v.get('tasks_overall_status') in READY_STATES])
        unprocessed_documents = all_documents - processed_documents

        session_data = {'session_id': session.pk,
                        'project_id': session.project.pk,
                        'user_id': session.created_by.pk if session.created_by else None,
                        'user_name': session.created_by.get_full_name() if session.created_by else None,
                        'progress': progress,
                        'processed_documents': processed_documents,
                        'unprocessed_documents': unprocessed_documents,
                        'completed': bool(session.completed),
                        'created_date': session.created_date}
        from apps.project.tasks import LoadArchive
        session_archive_tasks = session.task_set.filter(name=LoadArchive.name,
                                                        progress=100,
                                                        metadata__progress_sent=False)
        if session_archive_tasks.exists():
            archive_tasks_progress_data = list()
            for task in session_archive_tasks.all():
                archive_tasks_progress_data.append(
                    dict(archive_name=task.metadata.get('file_name'),
                         arhive_progress=task.metadata.get('progress')))
            session_data['archive_data'] = archive_tasks_progress_data
            for task in session_archive_tasks:
                task.metadata['progress_sent'] = True
                task.save()
        data.append(session_data)

    message = ChannelMessage(message_types.CHANNEL_MSG_TYPE_ACTIVE_UPLOAD_SESSIONS, data)

    admins_and_managers = User.objects.qs_admins_and_managers()
    Websockets().send_to_users(qs_users=admins_and_managers, message_obj=message)

    for reviewer in User.objects.filter(role__is_admin=False, role__is_manager=False):
        _data = [i for i in data
                 if User.objects.filter(pk=reviewer.pk).filter(
                Q(project_owners__pk=i['project_id']) |
                Q(project_reviewers__pk=i['project_id']) |
                Q(project_super_reviewers__pk=i['project_id'])).exists()]
        if _data:
            message = ChannelMessage(message_types.CHANNEL_MSG_TYPE_ACTIVE_UPLOAD_SESSIONS, _data)
            Websockets().send_to_user(user_id=reviewer.pk, message_obj=message)


def notify_cancelled_upload_session(session, user_id):
    """
    Notify users about cancelled upload session
    """
    cancelled_by_user = User.objects.get(pk=user_id)

    data = {'session_id': session.pk,
            'project_id': session.project_id,
            'cancelled_by_user_id': cancelled_by_user.pk if cancelled_by_user else None,
            'cancelled_by_user_name': cancelled_by_user.get_full_name() if cancelled_by_user else None}

    message = ChannelMessage(message_types.CHANNEL_MSG_TYPE_CANCELLED_UPLOAD_SESSION, data)

    admins_and_managers = User.objects.qs_admins_and_managers()
    Websockets().send_to_users(qs_users=admins_and_managers, message_obj=message)

    non_admins = User.objects \
        .filter(role__is_admin=False, role__is_manager=False) \
        .filter(Q(project_owners__pk=session.project_id) |
                Q(project_reviewers__pk=session.project_id) |
                Q(project_super_reviewers__pk=session.project_id))
    Websockets().send_to_users(qs_users=non_admins, message_obj=message)


def notify_failed_load_document(file_name, session_id, directory_path):
    """
    Notify users about failed LoadDocument tasks
    """
    from apps.project.models import UploadSession
    project_id = UploadSession.objects.get(pk=session_id).project_id

    data = dict(
        file_name=file_name,
        project_id=project_id,
        upload_session_id=session_id,
        directory_path=directory_path
    )
    message = ChannelMessage(message_types.CHANNEL_MSG_TYPE_FAILED_LOAD_DOCUMENT, data)

    admins_and_managers = User.objects.qs_admins_and_managers()
    Websockets().send_to_users(qs_users=admins_and_managers, message_obj=message)

    non_admins = User.objects \
        .filter(role__is_admin=False, role__is_manager=False) \
        .filter(Q(project_owners__pk=project_id) |
                Q(project_reviewers__pk=project_id) |
                Q(project_super_reviewers__pk=project_id))
    Websockets().send_to_users(qs_users=non_admins, message_obj=message)


def notify_active_pdf2pdfa_tasks(data):
    """
    Notify users about active upload sessions to show/track progress
    """
    user_ids = set([i['user_id'] for i in data])
    for user_id in user_ids:
        user_data = [i for i in data if i['user_id'] == user_id]
        message = ChannelMessage(message_types.CHANNEL_MSG_TYPE_ACTIVE_PDF2PDFA_TASKS, user_data)
        Websockets().send_to_user(user_id=user_id, message_obj=message)
