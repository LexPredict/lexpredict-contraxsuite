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

from typing import Dict, Optional
from django.dispatch import receiver
from apps.rawdb import signals
from apps.common.log_utils import ProcessLogger
from apps.rawdb.rawdb.rawdb_field_handlers import RawdbFieldHandler
from apps.users.models import User

# noinspection PyUnusedLocal

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def document_fields_change_listener_impl(_sender,
                                         signal,
                                         log: ProcessLogger,
                                         document_event: str,
                                         document_pk: int,
                                         field_handlers: Dict[str, RawdbFieldHandler],
                                         fields_before: Optional[Dict],
                                         fields_after: Optional[Dict],
                                         changed_by_user: User = None):
    from apps.notifications.tasks import process_notifications_on_document_change
    if not changed_by_user:
        # we ignore changes made by system at the moment
        return

    if not fields_before and not fields_after:
        log.error('Document fields changed event appeared with both "before" and "after" fields empty.')
        return

    from apps.notifications.app_vars import APP_VAR_DISABLE_EVENT_NOTIFICATIONS
    if APP_VAR_DISABLE_EVENT_NOTIFICATIONS.val():
        return

    process_notifications_on_document_change(
        log.info,
        document_event, document_pk, fields_before, fields_after,
        changed_by_user.pk)


@receiver(signals.document_fields_changed)
def document_fields_change_listener(sender, **kwargs):
    document_fields_change_listener_impl(sender, **kwargs)
