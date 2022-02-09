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

from django.contrib.auth.models import Permission
from guardian.shortcuts import QuerySet, get_identity, get_group_obj_perms_model, get_user_obj_perms_model

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def permissions_for(app_name, model_name, get_default_perms=True, as_dict=False):
    from django.apps import apps

    perms = {}
    model = apps.get_model(app_name, model_name)
    if get_default_perms:
        default_perm_prefixes = model._meta.default_permissions
        default_perms = {
            f'{p}_{model_name}': {
                'app_name': app_name,
                'model_name': model_name,
                'perm_name': f'{p}_{model_name}',
                'perm_full_name': f'{app_name}.{p}_{model_name}'}
            for p in default_perm_prefixes}
        perms.update(default_perms)
    model_specific_perms = {
        p: {
            'app_name': app_name,
            'model_name': model_name,
            'perm_name': p,
            'perm_full_name': f'{app_name}.{p}'}
        for p, _ in model._meta.permissions}
    perms.update(model_specific_perms)
    if as_dict:
        return perms
    return list(perms.values())


owner_project_permissions = (
    'project.view_project',
    'project.change_project',
    'project.delete_project',
    'project.detect_field_values',
    'project.view_documents',
    'project.recluster_project',
    'project.add_project_user',
    'project.add_project_document',
    'project.bulk_assign',
    'project.bulk_update_status',
    'project.individual_assign',
    'project.delete_documents',
    'project.change_document_field_values',
    'project.change_document_status',
)

junior_reviewer_project_permissions = (
    'project.view_project',
)

reviewer_project_permissions = junior_reviewer_project_permissions + (
    'project.view_documents',
    'project.individual_assign',
    'project.change_document_field_values',
    'project.change_document_status',
)

super_reviewer_project_permissions = reviewer_project_permissions + (
    'project.recluster_project',
    'project.add_project_document',
    'project.individual_assign',
    'project.bulk_assign',
    'project.bulk_update_status',
)

document_permissions = (
    'document.view_document',
    'document.change_document_field_values',
    'document.change_status',
)

document_type_manager_permissions = dict(
    document_type=(
        'document.view_documenttype',
        'document.change_documenttype',
    ),
    document_field=(
        'document.view_documentfield',
        'document.change_documentfield',
        'document.clone_documentfield',
    ),
)


def get_default_group_permissions():
    menuitem_perms_list = permissions_for('common', 'menuitem')
    menuitem_perms_dict = permissions_for('common', 'menuitem', as_dict=True)
    menugroup_perms_list = permissions_for('common', 'menugroup')
    menugroup_perms_dict = permissions_for('common', 'menugroup', as_dict=True)
    documenttype_perms = permissions_for('document', 'documenttype')
    documentfield_perms = permissions_for('document', 'documentfield')
    documentfieldfamily_perms = permissions_for('document', 'documentfieldfamily')
    documentfieldcategory_perms = permissions_for('document', 'documentfieldcategory')
    documentfielddetector_perms = permissions_for('document', 'documentfielddetector')
    task_perms = permissions_for('task', 'task')
    project_perms_list = permissions_for('project', 'project')
    project_perms_dict = permissions_for('project', 'project', as_dict=True)
    document_perms = permissions_for('document', 'document')
    user_perms_list = permissions_for('users', 'user', get_default_perms=True)
    user_perms_dict = permissions_for('users', 'user', as_dict=True)

    default_group_permissions = {
        "Reviewer": [
            menuitem_perms_dict['view_menuitem'],
            menugroup_perms_dict['view_menugroup'],
        ],
        "Project Creator":
            menuitem_perms_list +
            menugroup_perms_list + [
                project_perms_dict['add_project'],
                project_perms_dict['view_project_stats'],
                user_perms_dict['view_explorer']
            ],
        "Project and Document Type Creator":
            menuitem_perms_list +
            menugroup_perms_list +
            documenttype_perms +
            documentfield_perms +
            documentfieldfamily_perms +
            documentfieldcategory_perms +
            documentfielddetector_perms + [
                project_perms_dict['add_project'],
                project_perms_dict['view_project_stats'],
                user_perms_dict['view_explorer']
            ],
        "Technical Admin":
            menuitem_perms_list +
            menugroup_perms_list +
            documenttype_perms +
            documentfield_perms +
            documentfieldfamily_perms +
            documentfieldcategory_perms +
            documentfielddetector_perms +
            document_perms +
            project_perms_list +
            task_perms +
            user_perms_list
    }
    return default_group_permissions


def remove_perm(perm, user_or_group=None, obj=None):
    """
    Patched guardian.shortcuts.remove_perm to work with user_or_group as Queryset
    """
    user, group = get_identity(user_or_group)
    if obj is None:
        try:
            app_label, codename = perm.split('.', 1)
        except ValueError:
            raise ValueError("For global permissions, first argument must be in"
                             " format: 'app_label.codename' (is %r)" % perm)
        perm = Permission.objects.get(content_type__app_label=app_label,
                                      codename=codename)
        if user:
            user.user_permissions.remove(perm)
            return
        if group:
            group.permissions.remove(perm)
            return

    if not isinstance(perm, Permission):
        perm = perm.split('.')[-1]

    if isinstance(obj, QuerySet):
        if user:
            model = get_user_obj_perms_model(obj.model)
            return model.objects.bulk_remove_perm(perm, user, obj)
        if group:
            model = get_group_obj_perms_model(obj.model)
            return model.objects.bulk_remove_perm(perm, group, obj)

    if isinstance(user_or_group, (QuerySet, list)):
        if user:
            model = get_user_obj_perms_model(obj)
            return model.objects.bulk_remove_perm(perm, user, obj)
        if group:
            model = get_group_obj_perms_model(obj)
            return model.objects.bulk_remove_perm(perm, group, obj)

    if user:
        model = get_user_obj_perms_model(obj)
        return model.objects.remove_perm(perm, user, obj)

    if group:
        model = get_group_obj_perms_model(obj)
        return model.objects.remove_perm(perm, group, obj)
