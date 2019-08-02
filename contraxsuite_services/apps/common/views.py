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

# Standard imports
from collections import OrderedDict

# Third-party imports
from constance.admin import ConstanceForm, get_values

# Django imports
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
from django.utils.translation import ugettext_lazy as _

# Project imports
import apps.common.mixins

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class AppConfigView(apps.common.mixins.TechAdminRequiredMixin, FormView):
    form_class = ConstanceForm
    template_name = 'common/config_form.html'

    def get_form(self, form_class=None):
        initial = get_values()
        form = self.form_class(initial=initial)
        form.fields = OrderedDict(sorted(form.fields.items()))
        return form

    def post(self, request, *args, **kwargs):
        initial = get_values()
        form = self.form_class(data=request.POST, initial=initial)
        if form.is_valid():
            form.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                _('Application settings updated successfully.'),
            )
            return HttpResponseRedirect('.')
        return super().post(request, *args, **kwargs)


def test_500_view(request):
    raise RuntimeError('Test 500 error')
    # return
