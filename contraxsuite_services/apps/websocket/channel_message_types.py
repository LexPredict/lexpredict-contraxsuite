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


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


"""
For CHANNEL_FIELDS channel:
"""
CHANNEL_MSG_TYPE_FIELDS_UPDATED = 'fields_updated'
CHANNEL_MSG_TYPE_FIELD_VALUE_SAVED = 'field_value_saved'
CHANNEL_MSG_TYPE_FIELD_ANNOTATION_SAVED = 'field_annotation_saved'
CHANNEL_MSG_TYPE_FIELD_ANNOTATION_DELETED = 'field_annotation_deleted'
CHANNEL_MSG_TYPE_ACTIVE_UPLOAD_SESSIONS = 'active_upload_sessions'
CHANNEL_MSG_TYPE_CANCELLED_UPLOAD_SESSION = 'cancelled_upload_session'
CHANNEL_MSG_TYPE_FAILED_LOAD_DOCUMENT = 'failed_load_document'
CHANNEL_MSG_TYPE_PROJECT_DOCUMENT_FIELDS_UPDATED = 'project_document_fields_updated'
CHANNEL_MSG_TYPE_PROJECT_ANNOTATIONS_STATUS_UPDATED = 'project_annotations_status_updated'
CHANNEL_MSG_TYPE_DETECTION_FAILED = 'failed_detect_value'
CHANNEL_MSG_TYPE_CREATE_VECTORS_COMPLETED = 'create_vectors_completed'
CHANNEL_MSG_TYPE_DETECT_SIMILARITY_COMPLETED = 'detect_similarity_completed'
CHANNEL_MSG_TYPE_DELETE_SIMILARITY_COMPLETED = 'delete_similarity_completed'
CHANNEL_MSG_TYPE_TASK_COMPLETED = 'task_completed'
CHANNEL_MSG_TYPE_DOCUMENT_TYPE_EVENT = 'document_type_event'
CHANNEL_MSG_TYPE_FIELD_CATEGORY_EVENT = 'field_category_event'
CHANNEL_MSG_TYPE_WEB_NOTIFICATION_ADDED = 'web_notification_added'
CHANNEL_MSG_TYPE_LAST_WEB_NOTIFICATIONS = 'last_web_notifications'
