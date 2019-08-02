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

# Standard imports
from collections import OrderedDict

# Django imports
from django import forms

from apps.common.forms import checkbox_field
from apps.document.models import Document
from apps.lease.tasks import MODULE_NAME

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class ProcessLeaseDocumentsForm(forms.Form):
    header = 'Detect and Process Lease Documents'
    no_detect = checkbox_field("All documents in DB are lease agreements (disable detection)")
    delete = checkbox_field("Delete existing lease documents data")

    def _post_clean(self):
        super()._post_clean()
        self.cleaned_data['module_name'] = MODULE_NAME

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['document_type'] = forms.MultipleChoiceField(
            choices=[(t, t) for t in Document.objects
                .order_by().values_list('document_type', flat=True).distinct()],
            widget=forms.SelectMultiple(attrs={'class': 'chosen'}),
            required=False)
        self.fields = OrderedDict((k, self.fields[k])
                                  for k in ['document_type', 'no_detect', 'delete'])
