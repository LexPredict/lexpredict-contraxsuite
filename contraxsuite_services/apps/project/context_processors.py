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

# Django imports
from apps.project.models import Project, UserProjectsSavedFilter

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def user_projects(request):
    if not request.user.is_authenticated or request.is_ajax() or hasattr(request, 'versioning_scheme'):
        return {}

    qs = Project.objects.order_by('-pk').values('pk', 'name')
    if request.user.is_reviewer:
        qs = qs.filter(reviewers=request.user)

    saved_filter, _ = UserProjectsSavedFilter.objects.get_or_create(user=request.user)

    if qs.count() == 1:
        saved_filter.projects.add(qs.first()['pk'])

    user_projects_selected = saved_filter.projects.values_list('pk', flat=True)

    return {'user_projects': qs,
            'user_projects_selected': list(user_projects_selected)}
