from enum import Enum
from typing import Dict, Tuple, Any, Optional, Set

from apps.common.event_utils import EventManager, ObjectChangedEvent, ObjectDeletedEvent
from apps.common.log_utils import ProcessLogger
from apps.document.models import Document, DocumentField, DocumentType


class DocSysField(Enum):
    DOCUMENT_TYPE = 'document_type'
    PROJECT = 'project'
    ASSIGNEE = 'assignee'
    STATUS = 'status'


class DocumentChangedEvent:
    def __init__(self,
                 log: ProcessLogger,
                 document: Document,
                 system_fields_changed: bool = True,
                 generic_fields_changed: bool = True,
                 user_fields_changed: bool = True,
                 pre_detected_field_values: Optional[Dict[str, Any]] = None
                 ) -> None:
        super().__init__()
        self.log = log
        self.document = document
        self.system_fields_changed = system_fields_changed
        self.generic_fields_changed = generic_fields_changed
        self.user_fields_changed = user_fields_changed
        self.pre_detected_field_values = pre_detected_field_values


on_document_change = EventManager(DocumentChangedEvent)
on_document_deleted = EventManager(Document)

# Fired when a DocumentField has been updated/deleted via admin app
on_document_field_updated = EventManager(DocumentField)
on_document_field_deleted = EventManager(DocumentField)

# Fired when a DocumentType has been updated/deleted via admin app
on_document_type_updated = EventManager(DocumentType)
on_document_type_deleted = EventManager(DocumentType)


def fire_documents_changed(log: ProcessLogger, doc_qr):
    for doc in doc_qr.select_related('document_type', 'project', 'status'):  # type: Document
        on_document_change.fire(
            DocumentChangedEvent(log=log,
                                 document=doc,
                                 system_fields_changed=True,
                                 user_fields_changed=False))
