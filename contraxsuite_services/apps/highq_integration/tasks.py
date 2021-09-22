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

# standard imports
import pathlib
import uuid
from cgi import parse_header
from decimal import Decimal
from requests.exceptions import HTTPError
from requests.models import Response

# third-party libraries
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from celery.states import UNREADY_STATES
from psycopg2 import InterfaceError, OperationalError

# django
from django.db.models import F, QuerySet, DateTimeField, DurationField, ExpressionWrapper
from django.utils import timezone

# ContraxSuite
import task_names
from contraxsuite_logging import CausedException
from apps.celery import app
from apps.common.file_storage import get_file_storage
from apps.common.file_storage.file_storage import ContraxsuiteFileStorage
from apps.common.streaming_utils import buffer_contents_into_temp_file
from apps.document.field_type_registry import init_field_type_registry
from apps.highq_integration.dto import *
from apps.highq_integration.models import (
    HighQDocument,
    HighQConfiguration,
    HighQiSheetColumnIDMapping,
    HighQiSheetColumnAssociation,
    HighQiSheetColumnChoiceMapping)
from apps.highq_integration.utils import HighQ_API_Client, format_token_fields, \
    highq_datetime_to_py_datetime
from apps.rawdb.field_value_tables import *
from apps.task.models import Task
from apps.task.tasks import ExtendedTask, LoadDocuments, call_task_func, call_task
from apps.users.user_utils import get_main_admin_user
from apps.deployment.models import Deployment
from django.conf import settings

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


_DEPLOYMENT_INSTALLATION_ID: Optional[str] = None


def get_deployment_installation_id() -> str:
    global _DEPLOYMENT_INSTALLATION_ID
    if _DEPLOYMENT_INSTALLATION_ID is None:
        _DEPLOYMENT_INSTALLATION_ID = str(Deployment.objects.first().installation_id)
    return _DEPLOYMENT_INSTALLATION_ID


class NullField(CausedException):
    def __init__(self, message: str, cause: Optional[Exception] = None):
        self._explanation = f'Exception caught while syncing with HighQ.'
        super().__init__(message, cause)


@shared_task(
    base=ExtendedTask,
    name=task_names.TASK_NAME_HIGHQ_GET_DOCUMENT,
    bind=True,
    soft_time_limit=600,
    default_retry_delay=10,
    retry_backoff=True,
    autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
    max_retries=0)
def get_highq_document(
    task: ExtendedTask,
    highq_configuration_id: int,
    highq_file_id: int,
    highq_file_location: str
) -> None:
    """
    Downloads a file from HighQ, loads it into ContraxSuite, and creates a
        HighQ Document object.

    Args:
        task (ExtendedTask): The parent ExtendedTask.
        highq_configuration_id (int): The ID of a HighQ Configuration.
        highq_file_id (int): The ID of a HighQ file.
        highq_file_location (int): The HighQ file's source directory.
    """
    # -------------------------------------------------------------------------
    # Fetch a model instance, instantiate an API client, and make API calls
    #   in order to get data used throughout the remainder of this task.
    # -------------------------------------------------------------------------
    task.log_info(
        f'Getting HighQ file #{highq_file_id} from "{highq_file_location}"'
    )

    highq_configuration: HighQConfiguration = \
        HighQConfiguration.objects.get(id=highq_configuration_id)

    try:
        _: Project = highq_configuration.project
    except AttributeError as attribute_error:
        raise NullField(
            f'HighQ Configuration #{highq_configuration.id}'
            ' is not associated with a ContraxSuite project'
            ' (i.e. files downloaded from HighQ have nowhere to go).'
            ' This usually occurs when a previously-associated ContraxSuite'
            ' Project was deleted.',
            attribute_error
        ) from attribute_error

    highq_api_client: HighQ_API_Client = \
        HighQ_API_Client(highq_configuration=highq_configuration)

    try:
        r_highq_file: Response = highq_api_client.get_highq_file(
            fileid=highq_file_id,
            original=False
        )
        r_highq_file.raise_for_status()
    except HTTPError as http_error:
        raise Exception(
            'HTTP Error caught while getting file from HighQ.'
            f' HighQ Configuration #{highq_configuration.id}.'
            f' {http_error}'
        ) from http_error

    if not r_highq_file.ok:
        raise Exception(
            'HighQ API `get_file` response not OK.'
            f' HighQ Configuration: {highq_configuration.id}'
            f' | {r_highq_file}'
        )

    try:
        r_isheet_record_id: Response = \
            highq_api_client.get_isheet_record_id(fileid=highq_file_id)
        r_isheet_record_id.raise_for_status()
    except HTTPError as http_error:
        raise Exception(
            'HTTP Error caught while getting iSheet record ID from HighQ.'
            f' HighQ Configuration #{highq_configuration.id}.'
            f' {http_error}'
        ) from http_error

    if not r_isheet_record_id.ok:
        raise Exception(
            'HighQ API `get_isheet_record_id` response not OK.'
            f' HighQ Configuration: {highq_configuration.id}'
            f' | {r_isheet_record_id}'
        )

    # -------------------------------------------------------------------------
    # Get data which will be used in the next operations...
    # -------------------------------------------------------------------------
    try:
        isheet_column_id_file_link: int = \
            highq_configuration.isheet_column_mapping \
                .highqisheetcolumnassociation_set \
                .get(contraxsuite_field_code='document_id') \
                .highq_isheet_column_id
    except HighQiSheetColumnAssociation.DoesNotExist as dne:
        raise Exception(
            'No HighQiSheetColumnAssociation mapping a ContraxSuite '
            'document_id to a HighQ iSheet column of type `File link`. '
            'Unable to continue. Exiting.'
        ) from dne

    file_ids_isheet_item_id: Dict[int, int] = {
        d['highq_file_id']: d['highq_isheet_item_id'] for d in
        highq_api_client.fetch_item_ids_in_files_column(
            isheetid=highq_configuration.highq_isheet_id,
            files_columnid=isheet_column_id_file_link
        )
    }

    highq_isheet_item_id: int = file_ids_isheet_item_id.get(highq_file_id)

    content_disposition: Optional[str] = \
        r_highq_file.headers.get('content-disposition')

    content_disposition: Tuple[str, dict] = \
        parse_header(content_disposition)

    quasi_upload_session_id: str = str(uuid.uuid4())
    highq_file_name = content_disposition[1].get('filename')

    rel_file_path: pathlib.Path = pathlib.Path(
        quasi_upload_session_id,
        highq_file_name,
    )

    # -------------------------------------------------------------------------
    # Store the HighQ file in ContraxSuite's raw file storage, create a
    #   ContraxSuite Document, and a then create a HighQDocument.
    # -------------------------------------------------------------------------
    contraxsuite_file_storage: ContraxsuiteFileStorage = get_file_storage()
    with buffer_contents_into_temp_file(
            http_response=r_highq_file,
            file_suffix=rel_file_path.suffix
    ) as temp_filename:
        with open(temp_filename, 'rb') as temp_file:
            contraxsuite_file_storage.mk_doc_dir(
                rel_path=quasi_upload_session_id
            )
            contraxsuite_file_storage.write_document(
                rel_file_path=str(rel_file_path),
                contents_file_like_object=temp_file
            )

        try:
            assignee_id: Optional[int] = highq_configuration.assignee.id
        except AttributeError:
            assignee_id = None

        kwargs: Dict[str, Any] = {
            'document_type_id': highq_configuration.document_type.uid,
            'project_id': highq_configuration.project.id,
            'assignee_id': assignee_id,
            'user_id': get_main_admin_user().pk,
            'source_type': 'HighQ',
            'source': f'{highq_configuration.title}',
            'source_path': highq_configuration.highq_site_id,
            'folder': highq_file_location,
            'propagate_exception': True,
            'run_standard_locators': True,
            'do_not_check_exists': True,
            'metadata': {},
        }

        new_document_id: int = \
            LoadDocuments.create_document_local(
                task=task,
                file_path=temp_filename,
                file_name=str(rel_file_path),
                kwargs=kwargs,
                pre_defined_doc_fields_code_to_val=None,
            )

        exception_message: str = \
            f'Unable to create ContraxSuite Document' \
            f' for HighQ file #{highq_file_id}'

        if new_document_id:
            if not isinstance(new_document_id, int):
                raise Exception(
                    'Expected new_document_id to be of type `int`.'
                    f' Instead got type: {type(new_document_id)}.'
                    f'\n{exception_message}'
                )

            new_highq_document = HighQDocument.objects.create(
                highq_configuration=highq_configuration,
                highq_file_id=highq_file_id,
                highq_isheet_item_id=highq_isheet_item_id,
                document=Document.objects.get(pk=new_document_id),
            )
            task.log_info(
                f'Created {new_highq_document} '
                'representing HighQ file #'
                f'{new_highq_document.highq_file_id} '
                'and ContraxSuite Document #'
                f'{new_highq_document.document.pk} '
                f'("{new_highq_document.document}").'
            )
        else:
            raise Exception(
                'No document loaded.\n'
                f'{exception_message}'
            )


@shared_task(
    base=ExtendedTask,
    name=task_names.TASK_NAME_HIGHQ_WRITE_TO_ISHEET,
    bind=True,
    soft_time_limit=600,
    default_retry_delay=10,
    retry_backoff=True,
    autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
    max_retries=0)
def write_to_isheet(
    task: ExtendedTask,
    highq_document_id: int
) -> None:
    """
    Gets a document's RawDB field values, constructs the necessary data
        transfer objects for JSON-serialization for each respective field
        (iSheet column), and then sends the data to a pre-specified iSheet.

    Args:
        task (ExtendedTask): The parent ExtendedTask.
        highq_document_id (int): The ID of a HighQ Document object.

    Returns:
        None
    """
    highq_document: HighQDocument = \
        HighQDocument.objects.get(id=highq_document_id)

    # -------------------------------------------------------------------------
    # Get the ContraxSuite Document's field values from RawDB.
    #   Additionally, save the RawDB field code and its corresponding
    #   FieldValue type in a dict. This will be used for fieldtype-specific
    #   formatting, like date or multi-choice handling.
    # -------------------------------------------------------------------------
    document_query_results: DocumentQueryResults = query_documents(
        document_type=highq_document.document.document_type,
        column_filters=[('document_id', str(highq_document.document.id))],
    )

    column_types: Dict[str, str] = {}
    for column in document_query_results.columns:
        try:
            document_field: DocumentField = DocumentField.objects.get(
                code=column.field_code,
                document_type__code=highq_document.document.document_type.code,
            )
        except DocumentField.DoesNotExist:
            continue
        column_types[column.name]: str = document_field.type

    try:
        rawdb_document_field_values: \
            Dict[str, Optional[Union[int, str, bool, Decimal, datetime.datetime]]] = \
            document_query_results.documents.pop()
    except IndexError as ie:
        raise Exception('Caught IndexError while trying to load RawDB document field values') from ie

    # -------------------------------------------------------------------------
    # Fetch the model instances needed for the next operations. Likewise,
    #   instantiate an API client and a referential data structure.
    # -------------------------------------------------------------------------
    highq_configuration: HighQConfiguration = \
        HighQConfiguration.objects.get(
            id=highq_document.highq_configuration_id
        )

    column_mapping: HighQiSheetColumnIDMapping = \
        HighQiSheetColumnIDMapping.objects.get(
            id=highq_configuration.isheet_column_mapping.id
        )

    highq_api_client: HighQ_API_Client = \
        HighQ_API_Client(highq_configuration=highq_configuration)

    mapped_field_codes: Tuple[str] = tuple(
        column_mapping.highqisheetcolumnassociation_set.values_list(
            'contraxsuite_field_code', flat=True,
        )
    )

    # -------------------------------------------------------------------------
    # Build ColumnDTO objects based on the field type of each field.
    #   Finally, add the list of ColumnDTOs to a single ISheetDTO.
    #
    # Logic: FieldAnnotations ('_ann') and RawDB field values are examined.
    #   FieldAnnotations are joined and included in the RawDataDTO.
    #   RawDB field values are formatted according to their field type.
    # -------------------------------------------------------------------------
    column_dtos: List[ColumnDTO] = []
    for code in mapped_field_codes:

        field_value: \
            Optional[Union[int, str, bool, Decimal, datetime.datetime]] = \
            rawdb_document_field_values.get(code)

        if code.endswith('_ann') or field_value is not None:
            column_association: HighQiSheetColumnAssociation = \
                column_mapping.highqisheetcolumnassociation_set.get(
                    contraxsuite_field_code=code
                )

            attributecolumnid: int = \
                column_association.highq_isheet_column_id

            rawdata_attribute_kwargs: \
                Dict[str, Union[str, ChoicesDTO]] = {}
        else:
            task.log_warn(f'No iSheet data to be recorded for {code}')
            continue

        if code.endswith('_ann'):
            try:
                document_field: DocumentField = \
                    DocumentField.objects.get(
                        code=code.split('_ann')[0],
                        document_type=highq_document.document.document_type
                    )

                qs_field_annotations: QuerySet = \
                    FieldAnnotation.objects.filter(
                        field=document_field,
                        document=highq_document.document
                    )

                rawdata_attribute_kwargs['value']: str = '\n\n'.join(
                    qs_field_annotations.values_list(
                        'location_text',
                        flat=True
                    )
                )

            except DocumentField.DoesNotExist as dne:
                raise Exception(
                    'Could not find the DocumentField corresponding to '
                    f'{code}.'
                ) from dne

        elif field_value is not None:
            field_type: str = column_types.get(code)
            if field_type == 'date':
                dateformat: Optional[str] = \
                    highq_api_client.fetch_isheet_column_dateformat(
                        isheetid=highq_configuration.highq_isheet_id,
                        attributecolumnid=attributecolumnid
                    )

                if dateformat is not None:
                    rawdata_attribute_kwargs['date']: str = \
                        field_value.strftime(dateformat)
                else:
                    task.log_warn(
                        'Could not discern date format. '
                        f'HighQ Configuration #{highq_configuration.id} '
                        f'(attributecolumnid: {attributecolumnid}).'
                    )

            elif field_type in ('money', 'amount', 'float', 'int', 'percent', 'duration'):
                decimal_places: Optional[int] = \
                    highq_api_client.fetch_isheet_column_decimal_places(
                        isheetid=highq_configuration.highq_isheet_id,
                        attributecolumnid=attributecolumnid,
                    )
                if (
                    decimal_places is not None
                    and isinstance(field_value, (int, float, Decimal))
                ):
                    field_value: Decimal = \
                        Decimal(field_value).quantize(
                            Decimal(f'0.{"0" * decimal_places}')
                        )
                    rawdata_attribute_kwargs['value']: str = str(field_value)

            elif field_type == 'multi_choice':
                choice_mapping: HighQiSheetColumnChoiceMapping = \
                    column_association.highq_isheet_column_choice_mapping

                if choice_mapping is not None:
                    selected_choices: List[str] = field_value.split(', ')
                    choice_ids: List[Tuple[int, str]] = [
                        (
                            choice_mapping.choice_mapping[selected_choice],
                            selected_choice
                        )
                        for selected_choice in selected_choices
                    ]
                    rawdata_attribute_kwargs['choices'] = \
                        ChoicesDTO(choice=[
                            ChoiceDTO(id=choice_id, label=selected_choice)
                            for choice_id, selected_choice in choice_ids
                        ])
                else:
                    continue
            else:
                rawdata_attribute_kwargs['value']: str = str(field_value)

        if attributecolumnid and code != 'document_id':
            # do not update the file link column
            column_dtos.append(
                ColumnDTO(
                    attributecolumnid=attributecolumnid,
                    rawdata=RawDataDTO(**rawdata_attribute_kwargs)
                )
            )

    isheet_dto = ISheetDTO(
        data=DataDTO(
            item=[ItemDTO(
                itemid=highq_document.highq_isheet_item_id,
                externalid=f'{settings.HOST_NAME}'
                           f'_{get_deployment_installation_id()}'
                           f'_{highq_document.pk}',
                column=column_dtos,
            )]
        )
    )

    # -------------------------------------------------------------------------
    # Send ISheetDTO data to HighQ iSheet.
    # -------------------------------------------------------------------------
    highq_api_client: HighQ_API_Client = \
        HighQ_API_Client(highq_configuration=highq_configuration)

    r_put_items: Response = Response()
    try:
        r_put_items: Response = \
            highq_api_client.put_isheet_items(
                isheetid=highq_configuration.highq_isheet_id,
                itemid=highq_document.highq_isheet_item_id,
                isheet_dto=isheet_dto
            )
        r_put_items.raise_for_status()
        task.log_info('PUT to HighQ iSheet.')
        if r_put_items.ok:
            highq_document.recorded_in_isheet = True
            highq_document.save(update_fields=['recorded_in_isheet'])
    except HTTPError as http_error:
        raise Exception(
            'HTTP Error caught while PUTting to'
            f' iSheet #{highq_configuration.highq_isheet_id}.'
            f' {http_error}.'
            f' RESPONSE CONTENT: {r_put_items.content}'
        ) from http_error


class HighQiSheetSynchronization(ExtendedTask):
    """
    """
    name: str = task_names.TASK_NAME_HIGHQ_ISHEET_SYNC
    soft_time_limit: int = 6000
    default_retry_delay: int = 10
    retry_backoff: bool = True
    autoretry_for: tuple = \
        (SoftTimeLimitExceeded, InterfaceError, OperationalError,)
    max_retries: int = 3

    def process(self, **kwargs):
        """
        This main method checks if there are active synchronization tasks,
            and if not, begins the HighQ Configuration synchronization process.
        """
        highq_config = kwargs.get('highq_config')
        highq_config_id: int = (
            highq_config.get('pk')
            if highq_config is not None
            else kwargs.get('highq_config_id')
        )

        if highq_config_id is None:
            raise Exception('HighQ configuration id not specified.')

        # ---------------------------------------------------------------------
        # Check if there are any active synchronization tasks.
        # ---------------------------------------------------------------------
        if Task.objects \
                .filter(status__in=UNREADY_STATES,
                        name=HighQiSheetSynchronization.name,
                        kwargs__highq_config_id=highq_config_id) \
                .exclude(id=self.request.id) \
                .exists():
            self.log_info(
                'A previous HighQ iSheet Synchronization task'
                ' is still running. Exiting.'
            )
            return None

        self.sync_highq_configuration(HighQConfiguration.objects.get(pk=highq_config_id))

    def sync_highq_configuration(
        self,
        highq_configuration: HighQConfiguration
    ) -> None:
        """
        Mediates synchronization operations for a given HighQ Configuration.

        This method:
            1. Gets a set of all files from a HighQ folder.
            2. Gets all relevant HighQ Documents.
            3. Finds discrepancies between the two sets and performs respective
                operations (mark as removed or download to ContraxSuite).
            4. Adds missing records to an iSheet.
            5. Detects if iSheet records need to be updated with ContraxSuite's
                values, and if so, sends data to HighQ in JSON format.

        TODO: It may be wise to divide this method's responsibilities among
            several other functions or tasks, as it has grown to encompass
            (too) many synchronization steps.

        Args:
            highq_configuration (HighQConfiguration): The HighQConfiguration to
                synchronize.

        Returns:
              None
        """
        # ---------------------------------------------------------------------
        # Instantiate an API client and create lists to hold relevant data.
        # ---------------------------------------------------------------------
        highq_configuration.last_sync_start = timezone.now()
        highq_configuration.save(update_fields=['last_sync_start'])
        self.log_debug(
            'Updated `last_sync_start` for '
            f'HighQ Configuration #{highq_configuration.id}.'
        )

        highq_api_client: HighQ_API_Client = \
            HighQ_API_Client(highq_configuration=highq_configuration)

        highq_folder_ids: Set[int] = {highq_configuration.highq_folder_id}
        highq_files: List[Dict[str, Union[str, int, dict]]] = []
        highq_file_ids_to_sync: List[Tuple[int, int, str]] = []

        # ---------------------------------------------------------------------
        # Get HighQ folder, subfolder, and file information.
        # ---------------------------------------------------------------------
        if highq_configuration.get_highq_files_from_subfolders:
            for folder in highq_api_client.fetch_subfolders(
                folderid=highq_configuration.highq_folder_id
            ):
                highq_folder_ids.add(folder['id'])

        for highq_folder_id in highq_folder_ids:
            try:
                r_highq_files: Response = highq_api_client.get_files(
                    folderid=highq_folder_id,
                    offset=0,
                    limit=-1,
                    orderby='desc',
                    ordertype='lastModified',
                )
                r_highq_files.raise_for_status()
                if r_highq_files.ok:
                    highq_files.extend(r_highq_files.json()['file'])
                else:
                    raise Exception(
                        'HighQ `get_files` content response not OK.'
                        f' HighQ Configuration: {highq_configuration.id}'
                        f' | {r_highq_files}'
                    )
            except HTTPError as http_error:
                raise Exception(
                    f'HTTP Error caught while synchronizing'
                    f' HighQ Configuration #{highq_configuration.id}.'
                    f' {http_error}'
                ) from http_error

        # ---------------------------------------------------------------------
        # Find the differences between the HighQ file set and the
        #   ContraxSuite document set.
        # ---------------------------------------------------------------------
        qs_highq_documents: QuerySet = \
            HighQDocument.objects.filter(
                highq_configuration=highq_configuration,
            )

        highq_file_ids: Set[int] = set(
            highq_file['id'] for highq_file in highq_files
        )

        highq_document_ids: Set[int] = \
            set(qs_highq_documents.values_list('highq_file_id', flat=True))

        in_contraxsuite_not_in_highq: Set[int] = \
            highq_document_ids.difference(highq_file_ids)

        in_highq_not_in_contraxsuite: Set[int] = \
            highq_file_ids.difference(highq_document_ids)

        # ---------------------------------------------------------------------
        # Mark documents which have been removed from HighQ.
        # ---------------------------------------------------------------------
        if not in_contraxsuite_not_in_highq:
            self.log_info('No HighQ Documents to mark as removed.')
        else:
            qs_extra_highq_documents: QuerySet = qs_highq_documents \
                .filter(highq_file_id__in=in_contraxsuite_not_in_highq) \
                .update(removed_from_highq=True)

            self.log_info(
                'Marking HighQ Documents as removed: '
                f'{list(qs_extra_highq_documents.values_list("pk"))}'
            )
            qs_extra_highq_documents.update(removed_from_highq=True)

        # ---------------------------------------------------------------------
        # Download files from HighQ and load them into ContraxSuite.
        # ---------------------------------------------------------------------
        if not in_highq_not_in_contraxsuite:
            self.log_info('No file transfer operations to complete.')
        else:
            for file in filter(
                lambda f: f['id'] in in_highq_not_in_contraxsuite,
                highq_files
            ):
                highq_file_location: str = file.get('location', '')
                highq_file_id: int = file['id']
                highq_file_ids_to_sync.append(
                    (
                        highq_configuration.id,
                        highq_file_id,
                        highq_file_location,
                    )
                )

        len_highq_file_ids_to_sync: int = len(highq_file_ids_to_sync)
        if len_highq_file_ids_to_sync > 0:
            self.log_info(
                f'Found {len_highq_file_ids_to_sync} '
                'new HighQ documents (HighQ Configuration '
                f'#{highq_configuration.id}) '
                'not synced with ContraxSuite. '
                'Beginning synchronization task(s) now.'
            )
            self.run_sub_tasks(
                sub_tasks_group_title='Synchronize HighQ documents for HighQ Configuration'
                                      f' #{highq_configuration.id}',
                sub_task_function=get_highq_document,
                args_list=highq_file_ids_to_sync,
                source_data=None,
                countdown=None,
            )

        # ---------------------------------------------------------------------
        # Get data which will be used in the next two operations...
        # ---------------------------------------------------------------------
        try:
            isheet_column_id_file_link: int = \
                highq_configuration.isheet_column_mapping \
                    .highqisheetcolumnassociation_set \
                    .get(contraxsuite_field_code='document_id') \
                    .highq_isheet_column_id
        except HighQiSheetColumnAssociation.DoesNotExist as dne:
            raise Exception(
                'No HighQiSheetColumnAssociation mapping a ContraxSuite '
                'document_id to a HighQ iSheet column of type `File link`. '
                'Unable to continue. Exiting.'
            ) from dne

        highq_isheet_item_ids: Dict[int, int] = {
            d['highq_file_id']: d['highq_isheet_item_id']
            for d in highq_api_client.fetch_item_ids_in_files_column(
                isheetid=highq_configuration.highq_isheet_id,
                files_columnid=isheet_column_id_file_link
            )
        }

        # ---------------------------------------------------------------------
        # Add HighQ files as iSheet rows
        # TODO: consider moving this functionality into an independent task
        #   ("create_isheet_records" or something similar)
        # ---------------------------------------------------------------------
        document_dtos: List[int] = [
            highq_file['id']
            for highq_file in highq_files
            if not highq_isheet_item_ids or (
                    highq_file['id'] not in highq_isheet_item_ids
                    and highq_isheet_item_ids
            )
        ]

        if len(document_dtos) > 0:
            isheet_dto: ISheetDTO = ISheetDTO(
                data=DataDTO(
                    item=[
                        ItemDTO(
                            column=[
                                ColumnDTO(
                                    attributecolumnid=isheet_column_id_file_link,
                                    rawdata=RawDataDTO(
                                        documents=DocumentsDTO(
                                            document=[
                                                DocumentDTO(
                                                    docid=highq_file_id
                                                )
                                            ]
                                        )
                                    )
                                )
                            ]
                        )
                        for highq_file_id in document_dtos
                    ]
                )
            )

            try:
                r_post_items: Response = \
                    highq_api_client.post_isheet_items(
                        isheetid=highq_configuration.highq_isheet_id,
                        isheet_dto=isheet_dto
                    )
                r_post_items.raise_for_status()
                self.log_info(
                    f'Added HighQ files {document_dtos} to'
                    f' iSheet #{highq_configuration.highq_isheet_id}'
                    f' (column {isheet_column_id_file_link}).'
                    f' Response: {r_post_items.text}'
                )
            except HTTPError as http_error:
                raise Exception(
                    'HTTP Error caught while POSTing to'
                    f' iSheet #{highq_configuration.highq_isheet_id}.'
                    f' {http_error}'
                ) from http_error

        # ---------------------------------------------------------------------
        # Add highq_isheet_item_id to HighQ Document objects
        # ---------------------------------------------------------------------
        highq_documents_needing_isheet_item_ids: List[HighQDocument] = [
            highq_document
            for highq_document in qs_highq_documents
            if (
                highq_document.highq_isheet_item_id is None
                or highq_document.highq_isheet_item_id
                not in highq_isheet_item_ids.values()
            )
        ]

        for highq_document in highq_documents_needing_isheet_item_ids:
            highq_document.highq_isheet_item_id = \
                highq_isheet_item_ids.get(highq_document.highq_file_id)

        HighQDocument.objects.bulk_update(
            objs=highq_documents_needing_isheet_item_ids,
            fields=('highq_isheet_item_id',)
        )

        # ---------------------------------------------------------------------
        # Update iSheet column values if the HighQ iSheet file item's
        #   modification date is older than its corresponding ContraxSuite
        #   Document's youngest FieldValue modification date
        # ---------------------------------------------------------------------
        isheet_updates: List[Tuple[int]] = []

        highq_file_ids_and_their_modification_dates: \
            List[Tuple[int, datetime.datetime]] = [
                (
                    highq_file['id'],
                    highq_datetime_to_py_datetime(
                        highq_file['modifieddate']
                    )
                ) for highq_file in highq_files
            ]

        for highq_file_id, highq_file_modifieddate \
                in highq_file_ids_and_their_modification_dates:

            highq_document: HighQDocument = HighQDocument.objects.filter(
                highq_configuration=highq_configuration,
                highq_file_id=highq_file_id,
            ).first()

            if highq_document is not None:
                if highq_document.highq_isheet_item_id is not None:
                    qs_document_field_values: QuerySet = \
                        highq_document.document.field_values.get_queryset()
                    if qs_document_field_values.exists():
                        contraxsuite_document_modified_date: datetime.datetime = \
                            qs_document_field_values.latest('modified_date').modified_date
                        if highq_file_modifieddate < contraxsuite_document_modified_date:
                            if (
                                highq_configuration.update_existing_isheet_items is True
                                or highq_document.recorded_in_isheet is False
                            ):
                                isheet_updates.append((highq_document.id,))

        if len(isheet_updates) > 0:
            self.run_sub_tasks(
                sub_tasks_group_title='Send ContraxSuite FieldValues to'
                                      ' HighQ iSheet | HighQ Configuration'
                                      f' #{highq_configuration.id}',
                sub_task_function=write_to_isheet,
                args_list=isheet_updates,
                source_data=None,
                countdown=None,
            )


@shared_task(
    base=ExtendedTask,
    name=task_names.TASK_NAME_HIGHQ_TRIGGER_ISHEET_SYNC,
    autoretry_for=(SoftTimeLimitExceeded, InterfaceError, OperationalError),
    max_retries=0,
    soft_time_limit=600,
    default_retry_delay=10,
    retry_backoff=True,
    bind=True)
def trigger_highq_isheet_synchronization(_task: ExtendedTask) -> None:
    """
    Step 1: HighQ synchronization
        Determine if any HighQ Configurations are ready for synchronization.
        If yes, call one or more `HighQiSheetSynchronization` task(s).

    Step 2: HighQ API access token refresh
        Determine if any HighQ Configurations need a refreshed access token.
        If yes, call the `refresh_highq_access_token` task.
    """
    _task.log_info('In task: trigger_highq_isheet_synchronization')

    # -------------------------------------------------------------------------
    # Step 1.1: Get HighQConfigurations synchronized longer ago
    #   than their last_sync_start + sync_frequency.
    # -------------------------------------------------------------------------
    qs_highq_configurations_to_sync: QuerySet = HighQConfiguration.objects \
        .annotate(
            next_sync_start=ExpressionWrapper(
                output_field=DateTimeField(),
                expression=F('last_sync_start') + (
                    datetime.timedelta(minutes=1)
                    * F('sync_frequency_minutes')
                )
            )
        ) \
        .filter(
            Q(enabled=True)
            & ~Q(project=None)
            & (
                Q(last_sync_start__isnull=True)
                | Q(next_sync_start__lte=timezone.now())
            )
        )

    # -------------------------------------------------------------------------
    # Step 1.2: Plan multiple HighQ Synchronization tasks.
    # Note: instead of scheduling a singular task with multiple HighQ
    #   Configuration IDs, we use many individual tasks. This allows for proper
    #   error handling; if one task fails, then it will not bring down the others.
    #   It will be shown as failed in the task list and the other synchronization
    #   tasks will continue to work.
    # -------------------------------------------------------------------------
    for config_id in qs_highq_configurations_to_sync.values_list('pk', flat=True):
        qr_running_sync_tasks: QuerySet = Task.objects.filter(
            status__in=UNREADY_STATES,
            name=HighQiSheetSynchronization.name,
            kwargs__highq_config_id=config_id
        )
        if not qr_running_sync_tasks.exists():
            call_task(HighQiSheetSynchronization, highq_config_id=config_id)

    # -------------------------------------------------------------------------
    # Step 2.1: Get HighQConfigurations with already expired access tokens
    #   or access tokens expiring in less than ten minutes.
    # -------------------------------------------------------------------------
    qs_highq_configurations_to_refresh: QuerySet = HighQConfiguration.objects \
        .annotate(
            time_remaining=ExpressionWrapper(
                output_field=DurationField(),
                expression=(
                        F('access_token_expiration')
                        - timezone.now()
                )
            )
        ) \
        .filter(
            # set this refresh to a reasonable amount of time (10 mins)
            #   for debugging: 5 hour token, refresh every three mins
            #       18000 - (60*3) = 17820
            time_remaining__lte=datetime.timedelta(minutes=10)
        )

    # -------------------------------------------------------------------------
    # Step 2.2: If there is at least one HighQConfiguration
    #   needing a new access token, then call the refresh access token task.
    # -------------------------------------------------------------------------
    for highq_configuration in qs_highq_configurations_to_refresh:
        _task.log_debug(
            'Calling task <refresh_highq_access_token>'
            f' for HighQ Configuration #{highq_configuration.id}'
        )
        call_task_func(
            task_func=refresh_highq_access_token,
            task_args=(highq_configuration.id,),
            user_id=get_main_admin_user().pk
        )


@shared_task(
    base=ExtendedTask,
    name=task_names.TASK_NAME_HIGHQ_REFRESH_ACCESS_TOKEN,
    bind=True)
def refresh_highq_access_token(
    task: ExtendedTask,
    highq_configuration_id: int
) -> None:
    """
    HighQ uses the OAuth 2.0 Authentication Code workflow
        to authenticate API requests.

    The initial access token is set when a HighQ Configuration model is saved.
        New access tokens require user intervention via the user-agent
        (clicking "Allow" in a web browser).

    However, the API also provides a "refresh token," allowing for automatic
        access token fetching without the need for user intervention.

    This task simply calls the HighQ API Client's `refresh_access_token()`
        method and logs the outcome.

    Args:
        task (ExtendedTask): The parent task.
        highq_configuration_id (int): The ID of a HighQ Configuration.

    Returns:
        None
    """
    qs_highq_configuration: QuerySet = \
        HighQConfiguration.objects.filter(id=highq_configuration_id)

    highq_api_client: HighQ_API_Client = HighQ_API_Client(
        highq_configuration=qs_highq_configuration.first()
    )

    try:
        r_refresh: Response = highq_api_client.refresh_access_token()
        r_refresh.raise_for_status()
        if r_refresh.ok:
            if qs_highq_configuration.count() == 1:
                task.log_debug(
                    'Refreshing access token for HighQ'
                    f' Configuration #{highq_configuration_id}'
                )
                qs_highq_configuration.update(
                    **format_token_fields(r_refresh.json())
                )
                task.log_info(
                    'Refreshed access token for HighQ'
                    f' Configuration #{highq_configuration_id}'
                )
        else:
            task.log_warn(
                'Refresh token response not OK.'
                f' HighQ Configuration: {highq_configuration_id}'
                f' | {r_refresh}'
            )
    except HTTPError as http_error:
        task.log_error(
            'HTTP Error caught while refreshing access token'
            f' for HighQ Configuration #{highq_configuration_id}.'
            f' {http_error}'
        )


app.register_task(HighQiSheetSynchronization())
