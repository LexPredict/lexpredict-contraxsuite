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

# Project imports
from apps.document.models import DocumentNote, TextUnitNote, DocumentFieldValue
from apps.analyze.models import DocumentCluster, TextUnitCluster
from apps.extract.models import Party
from apps.task.models import Task
from apps.task.tasks import purge_task


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.5a/LICENSE"
__version__ = "1.1.5a"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def cleanup_document_relations(document):

    # delete history
    document.history.all().delete()
    DocumentNote.history.filter(document=document).delete()
    TextUnitNote.history.filter(text_unit__document=document).delete()
    DocumentFieldValue.history.filter(document=document).delete()

    # delete empty Parties
    Party.objects.filter(
        # partyusage__text_unit__document=document,
        partyusage__isnull=True).delete()

    # delete empty Clusters
    DocumentCluster.objects.filter(documents__isnull=True).delete()
    TextUnitCluster.objects.filter(text_units__isnull=True).delete()

    # delete Tasks, Task history, TaskResults, child tasks
    task_kwargs = dict(file_name=document.name)
    if document.upload_session_id:
        task_kwargs['session_id'] = str(document.upload_session_id)
    file_tasks = Task.objects.filter_metadata(**task_kwargs)
    for file_task in file_tasks:
        if file_task.metadata.get('file_name') == document.name:
            purge_task(file_task.id)
