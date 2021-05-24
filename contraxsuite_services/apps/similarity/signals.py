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

from django.db import transaction
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from apps.document.models import Document
from apps.document.signals import document_deleted, doc_full_delete, doc_soft_delete
from apps.project.models import Project
from apps.project.signals import project_soft_deleted

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


@receiver(document_deleted)
def catch_document_deleted(sender, user, document: Document, **kwargs):
    transaction.on_commit(lambda: cancel_similarity_task(document.project_id, user))


# TODO: include user in signal
@receiver(doc_soft_delete)
def catch_doc_soft_delete(sender, document_ids, delete_pending: bool, **kwargs):
    if delete_pending:
        project_ids = list(Document.objects.filter(id__in=document_ids).values_list('project_id', flat=True))
        for project_id in project_ids:
            cancel_similarity_task(project_id)


@receiver(doc_full_delete)
def catch_doc_full_delete(sender, user, document_type_code, document_ids, **kwargs):
    project_ids = list(Document.objects.filter(id__in=document_ids).values_list('project_id', flat=True))
    for project_id in project_ids:
        cancel_similarity_task(project_id, user)


# TODO: catch user in signal
@receiver(pre_delete, sender=Document)
def catch_document_post_delete(sender, instance: Document, **kwargs):
    transaction.on_commit(lambda: cancel_similarity_task(instance.project_id))


@receiver(project_soft_deleted)
def catch_project_soft_deleted(sender, instance, user, **kwargs):
    transaction.on_commit(lambda: cancel_similarity_task(instance.id, user))


def cancel_similarity_task(project_id, user=None):
    from apps.similarity.tasks import DeleteDocumentSimilarityResults, DeleteTextUnitSimilarityResults, _call_task
    for task in (DeleteDocumentSimilarityResults, DeleteTextUnitSimilarityResults):
        _call_task(task, project_id=project_id, user_id=user.pk if user else None)
