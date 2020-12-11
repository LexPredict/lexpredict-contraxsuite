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

# django
from django.conf import settings
from django.contrib.postgres.fields import HStoreField
from django.db import models
from django.db.models.deletion import CASCADE

# ContraxSuite
from apps.document import constants as document_constants
from apps.project.models import Project
from apps.users.models import User
from apps.document.models import Document, DocumentType, DocumentField


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class HighQiSheetColumnChoiceMapping(models.Model):
    """
    """
    class Meta:
        verbose_name: str = \
            ' iSheet Column Choice : ContraxSuite Field Choice Mapping'
        verbose_name_plural: str = \
            ' iSheet Column Choice : ContraxSuite Field Choice Mappings'

    name = models.CharField(
        max_length=50,
        blank=False,
        null=False,
    )

    isheet_column_id = models.PositiveIntegerField(
        verbose_name=' iSheet Column ID',
        blank=False,
        null=False,
    )

    contraxsuite_documentfield = models.ForeignKey(
        DocumentField,
        on_delete=CASCADE,
        verbose_name='ContraxSuite DocumentField',
        blank=False,
        null=False,
    )

    # TODO: add choices somehow? Requires widget modifications
    choice_mapping: HStoreField = HStoreField()

    def __str__(self):
        return \
            f'{self.name} ' \
            f'({self.contraxsuite_documentfield} @ {self.isheet_column_id}, ' \
            f'#{self.id})'


class HighQiSheetColumnIDMapping(models.Model):
    """
    """
    class Meta:
        verbose_name = ' iSheet Column : ContraxSuite Field Mapping'
        verbose_name_plural = ' iSheet Column : ContraxSuite Field Mappings'

    name = models.CharField(
        max_length=50,
        blank=False,
        null=False,
    )

    isheet_id = models.PositiveIntegerField(
        verbose_name=' iSheet ID',
        blank=False,
        null=False,
        help_text='The iSheet ID must match the one defined in the '
                  'HighQ Integration Configuration. Save to apply.'
    )

    contraxsuite_documenttype = models.ForeignKey(
        DocumentType,
        on_delete=CASCADE,
        verbose_name='ContraxSuite DocumentType',
        blank=False,
        null=False,
        help_text='The ContraxSuite DocumentType must match the one defined in'
                  ' the HighQ Integration Configuration. Save to apply.'
    )

    def __str__(self):
        return \
            f'{self.name} ' \
            f'({self.contraxsuite_documenttype} @ {self.isheet_id}, ' \
            f'#{self.id})'


class HighQiSheetColumnAssociation(models.Model):
    """
    """
    class Meta:
        verbose_name = 'HighQ iSheet Column Association'
        verbose_name_plural = 'HighQ iSheet Column Associations'

    highq_isheet_column_id_mapping = models.ForeignKey(
        HighQiSheetColumnIDMapping,
        on_delete=CASCADE,
        verbose_name='HighQ iSheet Column ID Mapping',
        blank=True,
        null=True,
    )

    """
    RawDB column suffixes:
        '_amt', '_ann', '_cur', '_den', '_num', '_txt', '_text_search'
    Therefore, the max_length should be
        DOCUMENT_FIELD_CODE_MAX_LEN + length of the longest suffix
    In this case, '_text_search' is the longest column suffix, with length = 12
    """
    contraxsuite_field_code = models.CharField(
        max_length=document_constants.DOCUMENT_FIELD_CODE_MAX_LEN + 12,
        verbose_name='ContraxSuite Field Code',
        blank=False,
        null=False,
    )

    highq_isheet_column_id = models.PositiveIntegerField(
        verbose_name='HighQ iSheet Column ID',
        blank=False,
        null=False,
    )

    highq_isheet_column_choice_mapping = models.ForeignKey(
        HighQiSheetColumnChoiceMapping,
        on_delete=CASCADE,
        verbose_name='HighQ iSheet Column Choice Mapping',
        blank=True,
        null=True,
    )


class HighQConfiguration(models.Model):
    """
    """

    class Meta:
        verbose_name = 'HighQ Integration Configuration'
        verbose_name_plural = 'HighQ Integration Configurations'

    title = models.CharField(
        max_length=128,
        blank=False,
        null=True,
        db_index=True,
        unique=True,
        help_text='A unique and descriptive name '
                  'for this HighQ Integration Configuration.',
    )

    enabled = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        help_text='Whether or not '
                  'this HighQ Integration Configuration is active.',
    )

    update_existing_isheet_items = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        verbose_name='Update Existing iSheet Items',
        help_text='Whether or not changes to document field values in'
                  ' ContraxSuite should update iSheet rows in HighQ.',
    )

    api_client_id = models.PositiveIntegerField(
        blank=False,
        null=False,
        verbose_name='API Client ID',
    )

    api_secret_key = models.CharField(
        max_length=32,
        blank=False,
        null=False,
        verbose_name='API Secret Key',
    )

    api_instance_url = models.URLField(
        blank=False,
        null=False,
        verbose_name='API Instance URL',
    )

    project = models.ForeignKey(
        Project,
        on_delete=CASCADE,
        blank=False,
        null=False,
        verbose_name='ContraxSuite Project',
        help_text='ContraxSuite will send HighQ files to this project.'
    )

    assignee = models.ForeignKey(
        User,
        on_delete=CASCADE,
        blank=True,
        null=True,
        help_text='ContraxSuite will assign HighQ Documents to this user.',
    )

    highq_site_id = models.PositiveIntegerField(
        null=False,
        blank=False,
        verbose_name='HighQ Site ID',
    )

    highq_folder_id = models.PositiveIntegerField(
        null=False,
        blank=False,
        verbose_name='HighQ Folder ID',
        help_text='ContraxSuite will pull documents from this source.'
    )

    highq_isheet_id = models.PositiveIntegerField(
        null=False,
        blank=False,
        verbose_name='HighQ iSheet ID',
        help_text='ContraxSuite will send information to this destination.'
    )

    refresh_token = models.CharField(
        null=True,
        blank=True,
        max_length=1024,
    )

    access_token = models.CharField(
        null=True,
        blank=True,
        max_length=1024,
    )

    access_token_expiration = models.DateTimeField(
        null=True,
        blank=True,
    )

    sync_frequency_minutes = \
        models.PositiveIntegerField(
            default=60,
            null=False,
            blank=False,
            verbose_name='Synchronization Frequency (minutes)',
            help_text='ContraxSuite will attempt synchronization '
                      'at fixed intervals of this many minutes.'
        )

    last_sync_start = models.DateTimeField(
        null=True,
        blank=True,
    )

    isheet_column_mapping = models.ForeignKey(
        HighQiSheetColumnIDMapping,
        on_delete=CASCADE,
        null=True,
        blank=True,
        verbose_name=' iSheet Column Mapping',
        help_text='Map ContraxSuite fields to iSheet columns. Save this HighQ '
                  'Integration Configuration before adding Column Associations.'
    )

    def __str__(self) -> str:
        return f'{self.__class__.__name__}: {self.title}'

    @property
    def api_base_url(self) -> str:
        """
        Get the API base url.

        Returns:
            (str) The API base URL
        """
        return f'{self.api_instance_url}' \
               f'api/'

    @property
    def api_authorization_url(self) -> str:
        """
        Get the API Authorization URL.

        Returns:
            (str) The API authorization URL
        """
        return f'{self.api_instance_url}' \
               f'authorize.action'

    @property
    def api_token_url(self) -> str:
        """
        Get the API Token URL.

        Returns:
            (str) The API token URL
        """
        return f'{self.api_instance_url}' \
               f'api/oauth2/token/'

    @property
    def api_callback_url(self):
        host_name: str = settings.HOST_NAME
        protocol: str = settings.API_URL_PROTOCOL
        return f'{protocol}://{host_name}/explorer/highq_integration/' \
               '{highq_configuration_id}/callback'

    @property
    def document_type(self) -> DocumentType:
        return self.project.type


class HighQDocument(models.Model):
    """
    TODO: find out if HighQ document IDs can collide between HighQ sites
    TODO: figure out the necessary field args
    """

    class Meta:
        verbose_name: str = 'HighQ Document'
        verbose_name_plural: str = 'HighQ Documents'
        constraints: list = [
            models.UniqueConstraint(
                fields=['highq_configuration', 'highq_file_id'],
                # TODO: better constraint name
                name='HighQConfiguration_HighQFileID'
            )
        ]

    highq_configuration = models.ForeignKey(
        HighQConfiguration,
        null=False,
        blank=False,
        on_delete=CASCADE,
        verbose_name='HighQ Configuration',
    )

    highq_file_id = models.PositiveIntegerField(
        null=False,
        blank=False,
        verbose_name='HighQ File ID',
    )

    highq_isheet_item_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='HighQ iSheet Item ("Record") ID'
    )

    document = models.ForeignKey(
        Document,
        null=False,
        blank=False,
        on_delete=CASCADE,
        verbose_name='ContraxSuite Document',
    )

    in_highq_folder = models.BooleanField(
        help_text='Is the corresponding HighQ file still in '
                  'its HighQ source directory?',
        verbose_name='In HighQ folder?',
        default=True,
        null=False,
        blank=False,
    )

    recorded_in_isheet = models.BooleanField(
        help_text='Does the corresponding HighQ file have an iSheet record?',
        verbose_name='Recorded in iSheet?',
        default=False,
        null=False,
        blank=False,
    )

    @property
    def highq_site_id(self) -> int:
        return self.highq_configuration.highq_site_id

    @property
    def highq_folder_id(self) -> int:
        return self.highq_configuration.highq_folder_id

    @property
    def highq_isheet_id(self) -> int:
        return self.highq_configuration.highq_isheet_id
