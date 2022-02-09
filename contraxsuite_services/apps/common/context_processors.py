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
from django.conf import settings
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def common(request):
    if request.is_ajax() or hasattr(request, 'versioning_scheme'):
        return {}

    from apps.extract.app_vars import STANDARD_LOCATORS, OPTIONAL_LOCATORS
    available_locators = set(STANDARD_LOCATORS.val()) | set(OPTIONAL_LOCATORS.val())

    custom_main_menu_item_templates = []
    custom_task_menu_item_templates = []
    custom_apps = [i.replace('apps.', '') for i in settings.INSTALLED_APPS if i.startswith('apps.')]
    for app_name in custom_apps:
        try:
            mmi_template = get_template('%s/templates/%s' % (app_name, 'main_menu_item.html'))
            custom_main_menu_item_templates.append(mmi_template.template.name)
        except TemplateDoesNotExist:
            pass
        try:
            tmi_template = get_template('%s/templates/%s' % (app_name, 'task_menu_item.html'))
            custom_task_menu_item_templates.append(tmi_template.template.name)
        except TemplateDoesNotExist:
            pass

    # TODO: define separate permission for this purpose?
    has_admin_permissions = request.user.has_perm('task.add_task')

    return {'settings': settings,
            'custom_main_menu_item_templates': sorted(custom_main_menu_item_templates),
            'custom_task_menu_item_templates': sorted(custom_task_menu_item_templates),
            'available_locators': available_locators,
            'has_admin_permissions': has_admin_permissions}
