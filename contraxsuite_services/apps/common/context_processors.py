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

# Third-party imports
from constance import config

# Django imports
from django.conf import settings
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist

# Project imports
from apps.document.models import Document
from apps.project.models import Project, TaskQueue
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.1/LICENSE"
__version__ = "1.2.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def common(request):
    if request.is_ajax() or hasattr(request, 'versioning_scheme'):
        return {}

    available_locators = list(settings.REQUIRED_LOCATORS) + list(config.standard_optional_locators)
    available_locator_groups = [
        group_name for group_name, group_items in settings.LOCATOR_GROUPS.items()
        if any(set(group_items).intersection(available_locators))]

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

    return {'settings': settings,
            'custom_main_menu_item_templates': custom_main_menu_item_templates,
            'custom_task_menu_item_templates': custom_task_menu_item_templates,
            'available_locators': available_locators,
            'available_locator_groups': available_locator_groups,
            'documents_count': Document.objects.count(),
            'projects_count': Project.objects.count(),
            'task_queues_count': TaskQueue.objects.count(),
            'reviewers_count': User.objects.exclude(role__is_admin=True)
                .exclude(role__is_manager=True).count()}
