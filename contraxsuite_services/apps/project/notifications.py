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

from django.db.models import QuerySet

from apps.users.models import User
from apps.project.models import UploadSession, Project
from apps.websocket import channel_message_types as message_types
from apps.websocket.channel_message import ChannelMessage
from apps.websocket.websockets import Websockets

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def notify_active_upload_sessions(sessions: List[UploadSession]):
    """
    Notify users about active upload sessions to show/track progress
    """
    data = []
    for session in sessions:
        # calculate progress baed on stored entities
        session_data = get_session_data_by_document_query(session)
        data.append(session_data)

    from guardian.shortcuts import get_objects_for_user
    for user in User.objects.filter(is_active=True):
        user_project_ids = list(get_objects_for_user(user, 'project.add_project_document', Project)
                                .values_list('pk', flat=True))
        user_data = [i for i in data if i['project_id'] in user_project_ids]
        message = ChannelMessage(message_types.CHANNEL_MSG_TYPE_ACTIVE_UPLOAD_SESSIONS, user_data)
        Websockets().send_to_user(user_id=user.pk, message_obj=message)


def get_session_data_by_document_query(session: UploadSession):
    progress_detail = session.get_document_loading_progress()
    # "processed" documents may not be cached yet
    processed_documents = progress_detail['docs_cached']
    unprocessed_documents = progress_detail['task_count'] - processed_documents
    progress = progress_detail['progress']
    session_data = {'session_id': session.pk,
                    'project_id': session.project.pk,
                    'user_id': session.created_by.pk if session.created_by else None,
                    'user_name': session.created_by.name if session.created_by else None,
                    'progress': progress,
                    'processed_documents': processed_documents,
                    'unprocessed_documents': unprocessed_documents,
                    'completed': bool(session.completed),
                    'created_date': session.created_date}
    return session_data


def notify_cancelled_upload_session(session, user_id):
    """
    Notify users about cancelled upload session
    """
    cancelled_by_user = User.objects.get(pk=user_id)

    data = {'session_id': session.pk,
            'project_id': session.project_id,
            'cancelled_by_user_id': cancelled_by_user.pk if cancelled_by_user else None,
            'cancelled_by_user_name': cancelled_by_user.name if cancelled_by_user else None}

    message = ChannelMessage(message_types.CHANNEL_MSG_TYPE_CANCELLED_UPLOAD_SESSION, data)

    users = User.get_users_for_object(
        object_pk=session.project_id,
        object_model=Project,
        perm_name='add_project_document')

    Websockets().send_to_users(qs_users=users, message_obj=message)


def notify_failed_load_document(file_name, session_id, directory_path):
    """
    Notify users about failed LoadDocument tasks
    """
    project_id = UploadSession.objects.get(pk=session_id).project_id

    data = dict(
        file_name=file_name,
        project_id=project_id,
        upload_session_id=session_id,
        directory_path=directory_path
    )
    message = ChannelMessage(message_types.CHANNEL_MSG_TYPE_FAILED_LOAD_DOCUMENT, data)

    users = User.get_users_for_object(
        object_pk=project_id,
        object_model=Project,
        perm_name='add_project_document').values_list('pk', flat=True)

    Websockets().send_to_users(qs_users=users, message_obj=message)


def notify_active_pdf2pdfa_tasks(data):
    """
    Notify users about active upload sessions to show/track progress
    """
    user_ids = set([i['user_id'] for i in data])
    for user_id in user_ids:
        user_data = [i for i in data if i['user_id'] == user_id]
        message = ChannelMessage(message_types.CHANNEL_MSG_TYPE_ACTIVE_PDF2PDFA_TASKS, user_data)
        Websockets().send_to_user(user_id=user_id, message_obj=message)


def combine_querysets_and_send_message(q_sets: List[QuerySet], message: ChannelMessage):
    result_set = set()
    for q_set in q_sets:
        user_ids = set([id for id in q_set.values_list('pk', flat=True)])
        result_set.union(user_ids)
    Websockets().send_to_users_by_ids(user_ids=list(result_set), message_obj=message)
