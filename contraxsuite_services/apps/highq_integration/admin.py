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

from typing import Generator, List, Optional, Tuple

from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, OuterRef, Subquery, TextField, QuerySet
from django.db.models.functions import Cast
from django.forms import ModelForm, BaseInlineFormSet, Select
from django.shortcuts import HttpResponseRedirect
from django_admin_hstore_widget.forms import HStoreFormField

from apps.document.models import DocumentType, DocumentField
from apps.highq_integration.models import (
    HighQConfiguration,
    HighQiSheetColumnIDMapping,
    HighQiSheetColumnAssociation,
    HighQiSheetColumnChoiceMapping)
from apps.highq_integration.models import HighQDocument
from apps.highq_integration.utils import HighQ_API_Client, get_initial_access_code
from apps.rawdb.field_value_tables import query_documents
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class HighQConfigurationAdminForm(ModelForm):
    class Meta:
        model: Model = HighQConfiguration
        exclude: Tuple[str] = (
            'access_token',
            'refresh_token',
            'access_token_expiration',
            'last_sync_start',
        )


class HighQDocumentAdminForm(ModelForm):
    class Meta:
        model: Model = HighQConfiguration
        exclude: Tuple[str] = ()


class HighQiSheetColumnIDMappingAdminForm(ModelForm):
    class Meta:
        model: Model = HighQiSheetColumnIDMapping
        exclude: Tuple[str] = ()


class HighQiSheetColumnChoiceMappingAdminForm(ModelForm):
    choice_mapping = HStoreFormField()

    class Meta:
        model: Model = HighQiSheetColumnChoiceMapping
        exclude: Tuple[str] = ()


class HighQiSheetColumnAssociationFormSet(BaseInlineFormSet):
    def get_form_kwargs(self, index) -> dict:
        kwargs: dict = \
            super().get_form_kwargs(index)
        kwargs.update({'parent': self.instance})
        return kwargs


class HighQiSheetColumnAssociationForm(ModelForm):
    class Meta:
        model: Model = HighQiSheetColumnAssociation
        exclude: Tuple[str] = ()

    def __init__(self, *args, **kwargs):
        """
        Automatically populates the selection choices based on:
        - HighQConfiguration DocumentType
        - HighQConfiguration iSheet ID
        """
        parent = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)
        if parent is not None:
            if parent.contraxsuite_documenttype_id:
                document_type: DocumentType = \
                    DocumentType.objects.get(uid=parent.contraxsuite_documenttype_id)

                document_field_annotation_codes: Generator[str, None, None] = (
                    f'{document_field}_ann'
                    for document_field in
                    DocumentField.objects
                        .filter(document_type=document_type)
                        .values_list('code', flat=True)
                )

                column_codes: Tuple[str] = tuple(
                    query_documents(document_type=document_type).column_codes
                )

                choices_field_code: Tuple[Tuple[str, str], ...] = tuple(
                    (field_code, field_code)
                    for field_code in sorted((
                        *document_field_annotation_codes,
                        *column_codes
                    ))
                )

                self.fields['contraxsuite_field_code'].widget = \
                    Select(choices=choices_field_code)

            if parent.isheet_id:
                try:
                    highq_configuration: HighQConfiguration = \
                        parent.highqconfiguration_set.first()

                    highq_api_client: HighQ_API_Client = \
                        HighQ_API_Client(highq_configuration=highq_configuration)

                    isheet_columns: \
                        Tuple[Tuple[str, int, Optional[List[Tuple[str, int]]]]] = \
                        tuple(highq_api_client.fetch_column_ids_names_choices(
                            isheetid=parent.isheet_id
                        ))

                    choices_column_id: Tuple[Tuple[int, str]] = tuple(
                        (column[1], f'{column[0]} {{{column[1]}}}')
                        for column in isheet_columns
                    )

                    self.fields['highq_isheet_column_id'].widget = \
                        Select(choices=choices_column_id)
                except:
                    pass


@admin.register(HighQConfiguration)
class HighQConfigurationAdmin(admin.ModelAdmin):
    form: ModelForm = HighQConfigurationAdminForm
    list_display: Tuple[str] = (
        'pk',
        'title',
        'enabled',
        'update_existing_isheet_items',
        'get_highq_files_from_subfolders',
        'project',
        'sync_frequency_minutes',
        'highq_site_id',
        'highq_folder_id',
        'highq_isheet_id',
        'modified_date',
        'modified_by',
    )

    def get_queryset(self, request) -> QuerySet:
        highq_configuration_content_type: ContentType = \
            ContentType.objects.get_for_model(model=HighQConfiguration)

        qs_log_entries: QuerySet = LogEntry.objects \
            .filter(
            content_type=highq_configuration_content_type,
            object_id=Cast(OuterRef('pk'), TextField())
        ) \
            .order_by('-action_time')

        qs_log_entries_modified_date: QuerySet = \
            qs_log_entries.values('action_time')

        qs_log_entries_modified_by: QuerySet = \
            qs_log_entries.values('user_id')

        return super().get_queryset(request).annotate(
            _latest_log_entry_timestamp=Subquery(
                qs_log_entries_modified_date[:1]
            ),
            _latest_log_entry_user=Subquery(
                qs_log_entries_modified_by[:1]
            ),
        )

    def modified_date(self, obj):
        return obj._latest_log_entry_timestamp

    modified_date.short_description = 'Modified On'
    modified_date.admin_order_field = '_latest_log_entry_timestamp'

    def modified_by(self, obj):
        return User.objects.get(pk=obj._latest_log_entry_user)

    modified_by.short_description = 'Modified By'
    modified_by.admin_order_field = '_latest_log_entry_user'

    def response_add(
        self,
        request,
        obj,
        post_url_continue=None
    ) -> HttpResponseRedirect:
        """
        Override the default behavior by redirecting to an authentication page.
        """
        return get_initial_access_code(obj)

    def response_change(
        self,
        request,
        obj,
        post_url_continue=None
    ) -> HttpResponseRedirect:
        """
        Override the default behavior by redirecting to an authentication page.
        """
        return get_initial_access_code(obj)


@admin.register(HighQDocument)
class HighQDocumentAdmin(admin.ModelAdmin):
    form: ModelForm = HighQDocumentAdminForm
    readonly_fields: Tuple[str] = (
        'highq_configuration',
        'document',
        'highq_file_id',
        'highq_isheet_item_id',
        'in_highq_folder',
        'recorded_in_isheet',
        'removed_from_highq',
    )

    list_display: Tuple[str] = (
        'pk',
        'highq_configuration',
        'document',
        'highq_file_id',
        'highq_isheet_item_id',
        'in_highq_folder',
        'recorded_in_isheet',
        'removed_from_highq',
    )


class HighQiSheetColumnAssociationInline(admin.TabularInline):
    model = HighQiSheetColumnAssociation
    readonly_fields: Tuple[str] = ('highq_isheet_column_id_mapping',)
    extra: int = 0
    form = HighQiSheetColumnAssociationForm
    formset = HighQiSheetColumnAssociationFormSet


@admin.register(HighQiSheetColumnIDMapping)
class HighQiSheetColumnIDMappingAdmin(admin.ModelAdmin):
    form: ModelForm = HighQiSheetColumnIDMappingAdminForm
    inlines: Tuple[admin.TabularInline] = (HighQiSheetColumnAssociationInline,)


@admin.register(HighQiSheetColumnChoiceMapping)
class HighQiSheetColumnChoiceMappingAdmin(admin.ModelAdmin):
    form: ModelForm = HighQiSheetColumnChoiceMappingAdminForm
