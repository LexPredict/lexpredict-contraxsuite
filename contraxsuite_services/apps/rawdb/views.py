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

# Future imports
from __future__ import absolute_import, unicode_literals

from typing import Optional

import task_names
# Project imports
from apps.rawdb.forms import ReindexForm
from apps.rawdb.tasks import manual_reindex
from apps.task.tasks import call_task_func
from apps.task.views import BaseAjaxTaskView

# Standard imports
# Django imports

# Other lib imports

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class ReindexTaskView(BaseAjaxTaskView):
    form_class = ReindexForm
    html_form_class = 'popup-form reindex'
    task_name = task_names.TASK_NAME_MANUAL_REINDEX

    def disallow_start(self):
        return False

    def start_task(self, data):
        document_type = data.get('document_type', {})
        document_type_code = document_type.code if document_type else None
        force = data.get('recreate_tables') or False
        proj = data.get('project') or None
        proj_id = proj.pk if proj else None  # type:Optional[int]
        call_task_func(manual_reindex, (document_type_code, force, proj_id),
                       data['user_id'])
