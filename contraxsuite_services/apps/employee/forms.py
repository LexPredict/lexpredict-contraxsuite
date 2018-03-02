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
# Standard imports
from collections import OrderedDict

# Django imports
from django import forms
from django.utils.translation import ugettext_lazy as _

# Project imports
from apps.common.forms import checkbox_field
from apps.document.models import Document

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.6"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class LocateEmployeesForm(forms.Form):
    header = 'Locate Employees in existing documents.'
    no_detect = checkbox_field("All documents in DB are employment agreements (disable detection)")
    delete = checkbox_field(
        label=_("Delete existing Employees"),
        initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['document_type'] = forms.MultipleChoiceField(
            choices=[(t, t) for t in Document.objects
                .order_by().values_list('document_type', flat=True).distinct()],
            widget=forms.SelectMultiple(attrs={'class': 'chosen'}),
            required=False)
        self.fields = OrderedDict((k, self.fields[k]) for k in ['document_type', 'no_detect', 'delete'])
