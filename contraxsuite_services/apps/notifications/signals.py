from typing import Dict, Optional

from django.dispatch import receiver
from apps.rawdb import signals

from apps.common.log_utils import ProcessLogger
from apps.document.models import Document
from apps.rawdb.rawdb.field_handlers import FieldHandler
from apps.users.models import User


# noinspection PyUnusedLocal
def document_fields_change_listener_impl(_sender,
                                         signal,
                                         log: ProcessLogger,
                                         document_event: str,
                                         document: Document,
                                         field_handlers: Dict[str, FieldHandler],
                                         fields_before: Optional[Dict],
                                         fields_after: Optional[Dict],
                                         changed_by_user: User = None):
    from apps.task.tasks import call_task_func
    from .tasks import process_notifications_on_document_change
    if not changed_by_user:
        # we ignore changes made by system at the moment
        return

    if not fields_before and not fields_after:
        log.error('Document fields changed event appeared with both "before" and "after" fields empty.')
        return

    from .app_vars import APP_VAR_DISABLE_EVENT_NOTIFICATIONS
    if APP_VAR_DISABLE_EVENT_NOTIFICATIONS.val:
        return
    call_task_func(process_notifications_on_document_change,
                   (document_event, document.pk, fields_before, fields_after, changed_by_user.pk),
                   changed_by_user.pk)


@receiver(signals.document_fields_changed)
def document_fields_change_listener(sender, **kwargs):
    document_fields_change_listener_impl(sender, **kwargs)
