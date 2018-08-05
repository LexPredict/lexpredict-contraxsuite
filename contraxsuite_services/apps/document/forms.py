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

from django import forms

from apps.document.models import DocumentType
from apps.document.tasks import MODULE_NAME

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.2/LICENSE"
__version__ = "1.1.2"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DetectFieldValuesForm(forms.Form):
    header = 'Detect Field Values'

    document_type = forms.ModelChoiceField(queryset=DocumentType.objects.all(), required=False)

    document_name = forms.CharField(strip=True, required=False)

    do_not_write = forms.BooleanField(label='Do not write detected values to DB (only log)',
                                      required=False)

    drop_classifier_model = forms.BooleanField(
        label='Drop classifier and detect initial values with regexps', required=False)

    def _post_clean(self):
        super()._post_clean()
        self.cleaned_data['module_name'] = MODULE_NAME


class TrainDocumentFieldDetectorModelForm(forms.Form):
    header = 'Train Document Field Detector Model'

    document_type = forms.ModelChoiceField(queryset=DocumentType.objects.all(), required=False)

    def _post_clean(self):
        super()._post_clean()
        self.cleaned_data['module_name'] = MODULE_NAME
