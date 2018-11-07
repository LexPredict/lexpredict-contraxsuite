from typing import List, Optional

from django.db.models import Q

from apps.document.models import DocumentField, Document, DocumentFieldValue, DocumentType


def get_qs_active_modified_document_ids(document_type: DocumentType,
                                        field: DocumentField,
                                        project_ids: Optional[List[str]]):
    q = DocumentFieldValue.objects \
        .filter(Q(field=field)
                & Q(text_unit__isnull=False)
                & Q(document__document_type=document_type)
                & Q(document__status__is_active=True)
                & (Q(created_by__isnull=False) | Q(removed_by_user=True)))
    if project_ids:
        q = q.filter(document__project_id__in=project_ids)

    return q.values_list('document_id', flat=True)


def get_qs_finished_document_ids(document_type: DocumentType, project_ids: Optional[List[str]]):
    q = Document.objects \
        .filter(document_type=document_type, status__is_active=False)

    if project_ids:
        q = q.filter(project_id__in=project_ids)

    return q.values_list('pk', flat=True)


def get_approved_documents_number(document_type: DocumentType, field: DocumentField, project_ids: Optional[List[str]]):
    return get_qs_active_modified_document_ids(document_type, field, project_ids).count() \
           + get_qs_finished_document_ids(document_type, project_ids).count()
