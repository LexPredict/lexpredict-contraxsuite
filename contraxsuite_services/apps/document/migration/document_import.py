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


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import tempfile
from shutil import rmtree
from typing import Dict, Tuple, Set, Optional, Any, List
import pandas as pd
import os
import zipfile
import regex as re
from django.db import transaction

from apps.common.file_storage import get_file_storage
from apps.common.sql_commons import ModelLock
from apps.document.migration.table_export_map import TableExportMapCollection, TableExportMap
from apps.document.models import DocumentType, DocumentField, Document, DocumentMetadata, \
    DocumentText, FieldAnnotation, TextUnit, TextUnitText, FieldValue, DocumentNote, \
    DocumentRelation, DocumentTable, FieldAnnotationFalseMatch, \
    DocumentTag, TextUnitNote, TextUnitProperty, TextUnitTag, TextUnitRelation, \
    DocumentProperty, DocumentPage
from apps.project.models import Project
from apps.task.tasks import ExtendedTask
from apps.users.models import User


class DocumentImporter:
    def __init__(self, task: Optional[ExtendedTask]):
        self.source_path = ''
        self.task = task
        self.mappings = TableExportMapCollection()

        # source-to-dest ID dictionaries
        self.document_types = {}  # type: Dict[str, str]
        self.field_types = {}  # type: Dict[str, str]
        self.project_ids = {}  # type: Dict[int, int]
        self.document_ids = {}  # type: Dict[int, int]
        self.document_src_paths = {}  # type: Dict[int, str]
        self.text_unit_ids = {}  # type: Dict[int, int]
        self.field_value_ids = {}  # type: Dict[int, int]

        self.initially_loaded_docs = []  # type: List[int]
        self.updated_docs = []  # type: List[int]

        self.missing_doc_types = {}  # type: Dict[str, str]
        # { (src_doc_type_id, field_code,) : dst_field_id }
        self.missing_field_types = {}  # type: Dict[Tuple[str, str], str]
        self.project = None  # type: Optional[Project]
        self.target_user = None  # type: Optional[User]

    def log_info(self, msg: str):
        if self.task:
            self.task.log_info(msg)
        else:
            print(msg)

    def log_error(self, msg: str):
        if self.task:
            self.task.log_error(msg)
        else:
            print(msg)

    def import_documents(self,
                         source_path: str,
                         project: Optional[Project],
                         target_user_id: int,
                         import_files: bool):
        self.target_user = User.objects.get(pk=target_user_id)
        self.project = project
        self.unzip_files(source_path)
        if self.task:
            push_steps = 19 - 3 + 5 + 5 + 5
            if import_files:
                push_steps += 1
            self.task.set_push_steps(push_steps)
        try:
            self.map_doc_types()
            self.push()
            self.map_field_types()
            self.push()
            self.import_projects()
            self.push()
            self.import_docs()
            self.push()
            self.import_doc_metadatas()
            self.push(5)
            self.import_doc_texts()
            self.push()
            self.import_text_units()
            self.push(5)
            self.import_text_unit_texts()
            self.push(5)
            self.import_field_values()
            self.push()
            self.import_field_annotations()
            self.push()
            self.import_field_annotations_false_match()
            self.push()
            self.import_doc_notes()
            self.push()
            self.import_doc_properties()
            self.push()
            self.import_doc_relations()
            self.push()
            self.import_doc_tables()
            self.push()
            self.import_doc_pages()
            self.push()
            self.import_doc_tags()
            self.push()
            self.import_text_unit_notes()
            self.push()
            self.import_text_unit_tags()
            self.push()
            self.import_text_unit_relations()
            self.push()
            if import_files:
                self.import_doc_files()
                self.push()
        finally:
            rmtree(self.source_path)

    def push(self, push_steps=1):
        if self.task:
            for _ in range(push_steps):
                self.task.push()

    def unzip_files(self, source_path: str):
        self.source_path = tempfile.mkdtemp()
        with zipfile.ZipFile(source_path, 'r') as zip_ref:
            zip_ref.extractall(self.source_path)

    def map_doc_types(self):
        # read document and field type ids, set maps
        # between source and target records
        dst_id_by_code = {}  # type: Dict[str, str]
        for uid, code in DocumentType.objects.values_list('uid', 'code'):
            dst_id_by_code[code] = uid

        mapping, type_df = self.get_mapping_and_df('document_documenttype')
        for values in mapping.iterate_dataframe(type_df):
            src_id, src_code = str(values['uid']), values['code']
            if src_code not in dst_id_by_code:
                self.missing_doc_types[src_code] = src_id
            else:
                self.document_types[src_id] = dst_id_by_code[src_code]

    def map_field_types(self):
        # read document and field type ids, set maps
        # between source and target records
        dst_types = {}  # type: Dict[Tuple[str, str], str]
        for uid, code, doc_type_id in DocumentField.objects.all().values_list(
                'uid', 'code', 'document_type_id'):
            dst_types[(doc_type_id, code)] = uid

        mapping, type_df = self.get_mapping_and_df('document_documentfield')
        for values in mapping.iterate_dataframe(type_df):
            uid, code, doc_type_id = str(values['uid']), values['code'], str(values['document_type_id'])
            doc_code = (doc_type_id, code,)
            if doc_code in dst_types:
                self.field_types[uid] = dst_types[doc_code]
            else:
                self.missing_field_types[doc_code] = uid

    def import_projects(self):
        proj_names = []
        mapping, proj_df = self.get_mapping_and_df('project_project')
        for values in mapping.iterate_dataframe(proj_df):
            proj_names.append(values['name'])
        self.log_info(f'Importing {len(proj_names)} projects: ' +
                      ', '.join(proj_names))

        project_types = set()  # type: Set[str]
        for values in mapping.iterate_dataframe(proj_df):
            proj_id, proj_name, proj_type = values['id'], values['name'], str(values['type_id'])
            project_types.add(proj_type)
            if proj_type in self.missing_doc_types:
                raise Exception(f'Doc. type {self.missing_doc_types[proj_type]} ' +
                                f'was not found, project "{proj_name}"')
            if self.project:
                self.project_ids[proj_id] = self.project.pk
                continue

            proj_type = self.document_types[proj_type]
            # TRANSACTION starts here
            with transaction.atomic():
                with ModelLock(None, Project, ModelLock.LOCK_MODE_ACCESS_EXCLUSIVE):
                    existing_projects = list(Project.all_objects.filter(name=proj_name).
                                             values_list('pk', 'type_id'))
                    if not existing_projects:
                        # create project
                        self.log_info(f'Creating project "{proj_name}"')
                        new_proj = Project()
                        new_proj.name = proj_name
                        new_proj.type_id = proj_type
                        new_proj.status_id = values['status_id']
                        new_proj.send_email_notification = values['send_email_notification'] == 't'
                        new_proj.hide_clause_review = values['hide_clause_review'] == 't'
                        new_proj.save()
                        self.project_ids[proj_id] = new_proj.pk
                        continue

            # there might be more than one project with the same name
            # some of these projects might have the required type
            matching_projects = [p for p in existing_projects if p[1] == proj_type]
            if not matching_projects:
                raise Exception(f'''Importing document type ({proj_type})
                                    differs from the document type of the selected 
                                    project ({existing_projects[0][1]}).''')
            self.project_ids[proj_id] = matching_projects[0][0]

        if self.project:
            if project_types:
                if len(project_types) > 1:
                    raise Exception(f'Trying to import documents of {len(project_types)} types into one project')
                src_doc_type = list(project_types)[0]
                if self.project.type_id != src_doc_type:
                    raise Exception(f'''Importing document type "{src_doc_type}" 
                        differs from the document type of the selected project ("{self.project.type_id}")''')
            project_types = {self.project.type_id}
        self.check_project_doc_field_types(project_types)

    def check_project_doc_field_types(self, project_types: Set[str]):
        missing_fields = []
        for doc_type_id, f_code in self.missing_field_types:
            if doc_type_id in project_types:
                missing_fields.append(f'field "{f_code}", doc. type "{doc_type_id}"')
        if missing_fields:
            msg = ', '.join(missing_fields)
            raise Exception(f'Following fields are missing: {msg}')

    def import_docs(self):
        """
        'id', 'name', 'description', 'source',
        'source_type', 'source_path', 'paragraphs', 'sentences',
        'title', 'document_type_id', 'project_id', 'status_id',
        'language', 'file_size', 'assign_date', 'delete_pending',
        'processed', 'folder', 'document_class'],
        """
        mapping, doc_df = self.get_mapping_and_df('document_document')

        self.log_info(f'Importing {doc_df.shape[0]} documents')
        for values in mapping.iterate_dataframe(doc_df):
            doc_id, doc_name, doc_proj = values['id'], values['name'], values['project_id']
            doc_proj = self.project_ids[doc_proj]

            with transaction.atomic():
                ex_docs = list(Document.all_objects.filter(project_id=doc_proj, name=doc_name))
                if ex_docs:
                    ex_doc = ex_docs[0]  # type: Document
                    self.document_ids[doc_id] = ex_doc.pk
                    self.log_info(f'{doc_name} document is already imported')
                    self.updated_docs.append(self.document_ids[doc_id])
                    self.document_src_paths[ex_doc.pk] = ex_doc.source_path
                    continue
                # or else import document
                self.import_document(values)

    def import_doc_files(self):
        storage = get_file_storage()
        file_ptrn = re.compile(r'^\d+_.*')
        for name_only in os.listdir(self.source_path):
            if not file_ptrn.match(name_only):
                continue
            doc_id = int(name_only.split('_')[0])
            doc_id = self.document_ids.get(doc_id)
            if not doc_id:
                self.log_error(f'File "{name_only}" - migrated doc was not found')
                continue
            dest_file_path = self.document_src_paths.get(doc_id)
            if not dest_file_path:
                self.log_error(f'File "{name_only}", #{doc_id} - document source path was not found')
                continue

            if storage.document_exists(dest_file_path):
                self.log_info(f'Document "{dest_file_path}" already exists')
                continue

            src_file_path = os.path.join(self.source_path, name_only)
            with open(src_file_path, 'rb') as fr:
                content = fr.read()
            # ensure the subfolder exists
            doc_folder = os.path.dirname(dest_file_path)
            if doc_folder:
                try:
                    storage.mk_doc_dir(doc_folder)
                except:
                    # folder might be already created
                    pass
            try:
                storage.write_document(dest_file_path, content, len(content))
            except Exception as e:
                self.log_error(f'Error storing file "{dest_file_path}": {e}')
                raise

    def import_doc_metadatas(self):
        def build_metadata_record(values: Dict[str, Any]) -> Optional[DocumentMetadata]:
            doc_id, metadata = values['document_id'], values['metadata']
            doc_id = self.document_ids[doc_id]
            if DocumentMetadata.objects.filter(document_id=doc_id).count():
                return None
            record = DocumentMetadata()
            record.document_id = doc_id
            record.metadata = metadata
            return record

        mapping = self.mappings.mapping_by_table['document_documentmetadata']  # type: TableExportMap
        mapping.import_values_from_df(
            self.read_dataframe, self.log_info, build_metadata_record)

    def import_doc_pages(self):
        def build_doc_note_record(values: Dict[str, Any]) -> Optional[DocumentPage]:
            doc_id, location_start = values['document_id'], values['location_start']
            doc_id = self.document_ids[doc_id]
            if DocumentPage.objects.filter(document_id=doc_id,
                                           location_start=location_start).count():
                return None
            record = DocumentPage()
            record.document_id = doc_id
            record.number = values['number']
            record.location_start = values['location_start']
            record.location_end = values['location_end']
            return record

        mapping = self.mappings.mapping_by_table['document_documentpage']  # type: TableExportMap
        mapping.import_values_from_df(
            self.read_dataframe, self.log_info, build_doc_note_record)

    def import_doc_texts(self):
        def build_doc_text_record(values: Dict[str, Any]) -> Optional[DocumentText]:
            doc_id, full_text = values['document_id'], values['full_text']
            doc_id = self.document_ids[doc_id]
            if DocumentText.objects.filter(document_id=doc_id).count():
                return None
            record = DocumentText()
            record.document_id = doc_id
            record.full_text = full_text
            return record

        mapping = self.mappings.mapping_by_table['document_documenttext']  # type: TableExportMap
        mapping.import_values_from_df(
            self.read_dataframe, self.log_info, build_doc_text_record)

    def import_field_values(self):
        def build_field_value_record(values: Dict[str, Any]) -> Optional[FieldValue]:
            doc_id = self.document_ids[values['document_id']]
            field_id = self.field_types[str(values['field_id'])]
            if FieldValue.objects.filter(document_id=doc_id, field_id=field_id).count():
                return None
            record = FieldValue()
            record.document_id = doc_id
            record.field_id = field_id
            if not pd.isnull(values['modified_date']):
                record.modified_date = values['modified_date']
            record.value = values['value']
            if not pd.isnull(values['modified_by_id']):
                record.modified_by = self.target_user
            return record

        def on_field_val_saved(record, values):
            self.field_value_ids[values['id']] = record.pk

        mapping = self.mappings.mapping_by_table['document_fieldvalue']  # type: TableExportMap
        mapping.import_values_from_df(
            self.read_dataframe, self.log_info, build_field_value_record, on_field_val_saved)

    def import_field_annotations(self):
        def build_field_ant_record(values: Dict[str, Any]) -> Optional[FieldAnnotation]:
            doc_id = self.document_ids[values['document_id']]
            field_id = self.field_types[str(values['field_id'])]
            location_start = int(values['location_start'])
            location_end = int(values['location_end'])
            if FieldAnnotation.objects.filter(document_id=doc_id,
                                              field_id=field_id,
                                              location_start=location_start,
                                              location_end=location_end).count():
                return None
            record = FieldAnnotation()
            record.document_id = doc_id
            record.field_id = field_id
            if not pd.isnull(values['modified_date']):
                record.modified_date = values['modified_date']
            record.value = values['value']
            record.location_start = location_start
            record.location_end = location_end
            record.location_text = values['location_text']
            record.extraction_hint = values['extraction_hint']
            record.field_id = str(values['field_id'])
            # record.modified_by_id = values['modified_by_id']
            text_unit_id = self.get_pandas_nullable_int(values, 'text_unit_id')
            if text_unit_id:
                record.text_unit_id = self.text_unit_ids[text_unit_id]
            if not pd.isnull(values['assign_date']):
                record.assign_date = values['assign_date']
            if not pd.isnull(values['modified_by_id']):
                record.modified_by = self.target_user
            if not pd.isnull(values['assignee_id']):
                record.assignee = self.target_user
            # record.assignee_id = values['assignee_id']
            record.status_id = values['status_id']
            record.uid = str(values['uid'])
            return record

        mapping = self.mappings.mapping_by_table['document_fieldannotation']  # type: TableExportMap
        mapping.import_values_from_df(
            self.read_dataframe, self.log_info, build_field_ant_record)

    def import_field_annotations_false_match(self):
        def build_field_false_ant_record(values: Dict[str, Any]) -> Optional[FieldAnnotationFalseMatch]:
            doc_id = self.document_ids[values['document_id']]
            field_id = self.field_types[str(values['field_id'])]
            location_start = int(values['location_start'])
            location_end = int(values['location_end'])
            if FieldAnnotationFalseMatch.objects.filter(
                    document_id=doc_id,
                    field_id=field_id,
                    location_start=location_start,
                    location_end=location_end).count():
                return None
            record = FieldAnnotationFalseMatch()
            record.document_id = doc_id
            record.field_id = field_id
            record.value = values['value']
            record.location_start = location_start
            record.location_end = location_end
            record.location_text = values['location_text']
            record.field_id = str(values['field_id'])
            if not pd.isnull(values['assignee_id']):
                record.assignee = self.target_user
            # record.modified_by_id = values['modified_by_id']
            text_unit_id = self.get_pandas_nullable_int(values, 'text_unit_id')
            if text_unit_id:
                record.text_unit_id = self.text_unit_ids[text_unit_id]
            if not pd.isnull(values['assign_date']):
                record.assign_date = values['assign_date']
            # record.assignee_id = values['assignee_id']
            record.uid = str(values['uid'])
            return record

        mapping = self.mappings.mapping_by_table['document_fieldannotationfalsematch']  # type: TableExportMap
        mapping.import_values_from_df(
            self.read_dataframe, self.log_info, build_field_false_ant_record)

    def import_text_units(self):
        def build_text_unit_record(values: Dict[str, Any]) -> Optional[TextUnit]:
            doc_id = self.document_ids[values['document_id']]
            ex_unit_ids = list(TextUnit.objects.filter(
                document_id=doc_id,
                unit_type=values['unit_type'],
                location_start=values['location_start']).values_list('id', flat=True))
            if ex_unit_ids:
                self.text_unit_ids[values['id']] = ex_unit_ids[0]
                return None
            record = TextUnit()
            record.document_id = doc_id
            record.unit_type = values['unit_type']
            record.language = values['language']
            record.text_hash = values['text_hash']
            record.location_end = values['location_end']
            record.location_start = values['location_start']
            project_id = self.get_pandas_nullable_int(values, 'project_id')
            if project_id:
                project_id = self.project_ids.get(project_id)
                if project_id:
                    record.project_id = project_id
            return record

        def on_record_saved(record, values: Dict[str, Any]):
            self.text_unit_ids[values['id']] = record.pk

        mapping = self.mappings.mapping_by_table['document_textunit']  # type: TableExportMap
        mapping.import_values_from_df(
            self.read_dataframe, self.log_info, build_text_unit_record,
            on_record_saved)

    def import_text_unit_texts(self):
        def build_text_unittext_record(values: Dict[str, Any]) -> Optional[TextUnitText]:
            unit_id = self.text_unit_ids[values['text_unit_id']]
            if TextUnitText.objects.filter(text_unit_id=unit_id).count():
                return None
            record = TextUnitText()
            record.text_unit_id = unit_id
            record.text = values['text']
            record.text_tsvector = values['text_tsvector']
            return record

        mapping = self.mappings.mapping_by_table['document_textunittext']  # type: TableExportMap
        mapping.import_values_from_df(
            self.read_dataframe, self.log_info, build_text_unittext_record)

    def import_doc_notes(self):
        def build_doc_note_record(values: Dict[str, Any]) -> Optional[DocumentNote]:
            fval_id = self.field_value_ids.get(values['field_value_id'])
            loc_start, loc_end = self.get_pandas_nullable_int(values, 'location_start'), \
                                 self.get_pandas_nullable_int(values, 'location_end')
            document_id = self.document_ids[values['document_id']]
            note = values['note']

            if loc_start and loc_end:
                # field-level note
                if DocumentNote.objects.filter(document_id=document_id,
                                               location_start=loc_start,
                                               location_end=loc_end,
                                               note=note).count():
                    return None
            else:
                # document-level note
                if DocumentNote.objects.filter(document_id=document_id,
                                               note=note).count():
                    return None
            record = DocumentNote()
            record.field_value_id = fval_id
            if not pd.isnull(values['timestamp']):
                record.timestamp = values['timestamp']
            record.note = note
            record.document_id = document_id
            if values['field_id']:
                record.field_id = self.field_types[str(values['field_id'])]
            record.user = self.target_user
            record.username = values.get('username') or self.target_user.username
            record.location_start = loc_start
            record.location_end = loc_end
            return record

        mapping = self.mappings.mapping_by_table['document_documentnote']  # type: TableExportMap
        mapping.import_values_from_df(
            self.read_dataframe, self.log_info, build_doc_note_record)

    def import_doc_tags(self):
        def build_doc_tag_record(values: Dict[str, Any]) -> Optional[DocumentTag]:
            document_id = self.document_ids[values['document_id']]
            if DocumentTag.objects.filter(document_id=document_id).count():
                return None
            record = DocumentTag()
            if not pd.isnull(values['timestamp']):
                record.timestamp = values['timestamp']
            record.tag = values['tag']
            record.document_id = document_id
            if not pd.isnull(values['user_id']):
                record.user = self.target_user
            return record

        mapping = self.mappings.mapping_by_table['document_documenttag']  # type: TableExportMap
        mapping.import_values_from_df(
            self.read_dataframe, self.log_info, build_doc_tag_record)

    def import_doc_properties(self):
        def build_doc_props_record(values: Dict[str, Any]) -> Optional[DocumentProperty]:
            doc_id = self.document_ids[values['document_id']]
            if DocumentProperty.objects.filter(document_id=doc_id, key=values['key']).count():
                return None
            record = DocumentProperty()
            record.key = values['key']
            record.value = values['value']
            record.document_id = doc_id
            if not pd.isnull(values['created_date']):
                record.created_date = values['created_date']
            if not pd.isnull(values['modified_date']):
                record.modified_date = values['modified_date']
            return record

        mapping = self.mappings.mapping_by_table['document_documentproperty']  # type: TableExportMap
        mapping.import_values_from_df(
            self.read_dataframe, self.log_info, build_doc_props_record)

    def import_doc_relations(self):
        def build_doc_rels_record(values: Dict[str, Any]) -> Optional[DocumentRelation]:
            doc_a_id = self.document_ids[values['document_a_id']]
            doc_b_id = self.document_ids[values['document_b_id']]

            if DocumentRelation.objects.filter(document_a_id=doc_a_id,
                                               document_b_id=doc_b_id).count():
                return None
            record = DocumentRelation()
            record.relation_type = values['relation_type']
            record.document_a_id = doc_a_id
            record.document_b_id = doc_b_id
            return record

        mapping = self.mappings.mapping_by_table['document_documentrelation']  # type: TableExportMap
        mapping.import_values_from_df(
            self.read_dataframe, self.log_info, build_doc_rels_record)

    def import_doc_tables(self):
        def build_doc_table_record(values: Dict[str, Any]) -> Optional[DocumentTable]:
            doc_id = self.document_ids[values['document_id']]
            table_text = values['table']
            if DocumentTable.objects.filter(document_id=doc_id,
                                            table=table_text).count():
                return None
            record = DocumentTable()
            record.document_id = doc_id
            record.table = table_text
            return record

        mapping = self.mappings.mapping_by_table['document_documenttable']  # type: TableExportMap
        mapping.import_values_from_df(
            self.read_dataframe, self.log_info, build_doc_table_record)

    def import_text_unit_notes(self):
        def build_text_unit_note_record(values: Dict[str, Any]) -> Optional[TextUnitNote]:
            unit_id = self.text_unit_ids[values['text_unit_id']]
            if TextUnitNote.objects.filter(text_unit_id=unit_id,
                                           note=values['note']).count():
                return None
            record = TextUnitNote()
            record.text_unit_id = unit_id
            record.note = values['note']
            if not pd.isnull(values['timestamp']):
                record.timestamp = values['timestamp']
            if not pd.isnull(values['user_id']):
                record.user = self.target_user
                record.username = self.target_user.username
            return record

        mapping = self.mappings.mapping_by_table['document_textunitnote']  # type: TableExportMap
        mapping.import_values_from_df(
            self.read_dataframe, self.log_info, build_text_unit_note_record)

    def import_text_unit_props(self):
        def build_text_unit_props_record(values: Dict[str, Any]) -> Optional[TextUnitProperty]:
            unit_id = self.text_unit_ids[values['text_unit_id']]

            if TextUnitProperty.objects.filter(text_unit_id=unit_id, key=values['key']).count():
                return None
            record = TextUnitProperty()
            record.text_unit_id = unit_id
            record.key = values['key']
            record.value = values['value']
            if not pd.isnull(values['created_date']):
                record.created_date = values['created_date']
            if not pd.isnull(values['modified_date']):
                record.modified_date = values['modified_date']
            if not pd.isnull(values['created_by_id']):
                record.created_by = self.target_user
            if not pd.isnull(values['modified_by_id']):
                record.modified_by = self.target_user
            return record

        mapping = self.mappings.mapping_by_table['document_textunitproperty']  # type: TableExportMap
        mapping.import_values_from_df(
            self.read_dataframe, self.log_info, build_text_unit_props_record)

    def import_text_unit_tags(self):
        def build_text_unit_tag_record(values: Dict[str, Any]) -> Optional[TextUnitTag]:
            unit_id = self.text_unit_ids[values['text_unit_id']]

            if TextUnitTag.objects.filter(text_unit_id=unit_id).count():
                return None
            record = TextUnitTag()
            record.text_unit_id = unit_id
            record.tag = values['tag']
            if not pd.isnull(values['timestamp']):
                record.timestamp = values['timestamp']
            if not pd.isnull(values['user_id']):
                record.user = self.target_user
            return record

        mapping = self.mappings.mapping_by_table['document_textunittag']  # type: TableExportMap
        mapping.import_values_from_df(
            self.read_dataframe, self.log_info, build_text_unit_tag_record)

    def import_text_unit_relations(self):
        def build_text_unit_rels_record(values: Dict[str, Any]) -> Optional[TextUnitRelation]:
            unit_id_a = self.text_unit_ids[values['text_unit_a_id']]
            unit_id_b = self.text_unit_ids[values['text_unit_b_id']]

            if TextUnitRelation.objects.filter(text_unit_a_id=unit_id_a,
                                               text_unit_b_id=unit_id_b).count():
                return None
            record = TextUnitRelation()
            record.text_unit_a_id = unit_id_a
            record.text_unit_b_id = unit_id_b
            return record

        mapping = self.mappings.mapping_by_table['document_textunitrelation']  # type: TableExportMap
        mapping.import_values_from_df(
            self.read_dataframe, self.log_info, build_text_unit_rels_record)

    def import_document(self, values: Dict[str, Any]):
        doc = Document()
        doc.name = values['name']
        doc.description = values['description']
        doc.source = values['source']
        doc.source_type = values['source_type']
        doc.paragraphs = values['paragraphs']
        doc.sentences = values['sentences']
        doc.title = values['title']
        doc.document_type_id = self.document_types[str(values['document_type_id'])]
        doc.project_id = self.project_ids[values['project_id']]
        doc.status_id = str(values['status_id'])
        doc.language = values['language']
        doc.file_size = values['file_size']
        if not pd.isnull(values['assign_date']):
            doc.assign_date = values['assign_date']
        doc.delete_pending = values['delete_pending'] == 't'
        doc.processed = values['processed'] == 't'
        doc.folder = values['folder']
        doc.document_class = values['document_class']
        doc.document_contract_class = values.get('document_class', '')
        if not pd.isnull(values['assignee_id']):
            doc.assignee = self.target_user
        doc.source_path = values['source_path']
        doc.ocr_rating = values.get('ocr_rating') or values.get('ocr_grade') or 0
        doc.save()
        self.document_ids[values['id']] = doc.pk
        self.document_src_paths[doc.pk] = doc.source_path
        self.initially_loaded_docs.append(doc.pk)

    def read_dataframe(self, file_name: str):
        file_path = os.path.join(self.source_path, file_name)
        return pd.read_pickle(file_path)

    def get_mapping_and_df(self, table_name: str) -> Tuple[TableExportMap, pd.DataFrame]:
        df = self.read_dataframe(f'{table_name}.zip')
        mapping = self.mappings.mapping_by_table[table_name]
        return mapping, df

    @classmethod
    def get_pandas_nullable_int(cls, values: Dict[str, Any], key: str) -> Optional[int]:
        if key not in values:
            return None
        if pd.isnull(values[key]) or pd.isna(values[key]):
            return None
        return int(values[key])
