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

import json
from typing import List

import settings
from apps.common.mixins import (JSONResponseView)
from apps.document.models import Document
from apps.fields.document_fields_repository import DOCUMENT_FIELDS
from apps.fields.forms import BuildFieldDetectorDatasetForm, TrainFieldDetectorModelForm
from apps.fields.models import DocumentAnnotation, DocumentAnnotationTag, DocumentField, \
    ClassifierModel
from apps.fields.tasks import BuildFieldDetectorDataset
from apps.task.views import BaseAjaxTaskView

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.3/LICENSE"
__version__ = "1.1.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def _to_dto(annotation_model: DocumentAnnotation):
    return {
        'id': annotation_model.pk,
        'document_id': annotation_model.document.pk,
        'ranges': [{
            'start': annotation_model.start,
            'end': annotation_model.end,
            'startOffset': annotation_model.start_offset,
            'endOffset': annotation_model.end_offset
        }],
        'quote': annotation_model.quote,
        'text': annotation_model.comment,
        'tags': [tag.pk for tag in annotation_model.tags.all()] if annotation_model.pk else None,
        'document_field': annotation_model.document_field.pk if annotation_model.document_field
        else None,
        'user_id': annotation_model.user.pk if annotation_model.user else None
    }


class DocumentAnnotationStorageSearchView(JSONResponseView):
    @staticmethod
    def annotate_by_model(document: Document, document_class_name: str, field: str, text: str) -> \
            List[DocumentAnnotation]:
        try:
            classifier_model = ClassifierModel.objects.get(
                kind=ClassifierModel.KIND_SENTENCES_RELATED_TO_FIELDS,
                document_class=document_class_name,
                document_field=None)
            sklearn_model = classifier_model.get_trained_model_obj()
            spans_by_fields = sklearn_model.annotate(text)

            print('Trainable model provided annotations for fields: {0}'.format(
                spans_by_fields.keys()))

            res = []
            fields = [field] if field else spans_by_fields.keys()

            for field in fields:
                spans = spans_by_fields.get(field)
                if not spans:
                    return []

                res.extend([
                    DocumentAnnotation.build_auto_annotation(document, field, span[0], span[1],
                                                             span[2]) for span in spans])
            return res

        except Exception as e:
            print('Exception caught while trying to auto-annotate a document: ' + str(e))
            return []

    def get_json_data(self, request, *args, **kwargs):
        document_class_name = request.GET.get('document_class')
        document_id = request.GET.get('document_id')
        document_field_id = request.GET.get('document_field')
        if 'All' == document_field_id:
            document_field_id = None

        if document_field_id:
            annotation_models = list(DocumentAnnotation
                                     .objects
                                     .filter(document__pk=document_id,
                                             document_field__pk=document_field_id)) \
                if document_field_id \
                else list(DocumentAnnotation
                          .objects
                          .filter(document__pk=document_id))
        else:
            annotation_models = list(DocumentAnnotation.objects.filter(document__pk=document_id))

        doc = Document.objects.get(pk=document_id)

        auto_annotations = DocumentAnnotationStorageSearchView \
            .annotate_by_model(doc, document_class_name, document_field_id, doc.full_text)
        annotation_models.extend(auto_annotations)

        return {'rows': [_to_dto(a) for a in annotation_models]}


class DocumentAnnotationStorageView(JSONResponseView):
    @staticmethod
    def trigger_retraining_model(document_class, document_id):
        if settings.FIELDS_RETRAIN_MODEL_ON_ANNOTATIONS_CHANGE:
            BuildFieldDetectorDataset.build_dataset_on_document.apply_async(
                args=(None, document_class, document_id, True))

    @staticmethod
    def replace_annotation_suggested_by_system(request, data):
        doc = Document.objects.get(pk=data['document_id'])
        user = request.user
        document_field = DocumentField.objects.get_or_create(pk='')
        selection_range = data['ranges'][0]
        sel_start = selection_range['startOffset']
        sel_end = selection_range['endOffset']

        return DocumentAnnotation.objects.create(document=doc,
                                                 start=selection_range['start'],
                                                 end=selection_range['end'],
                                                 start_offset=sel_start,
                                                 end_offset=sel_end,
                                                 quote=data['quote'],
                                                 comment=None,
                                                 user=user,
                                                 document_field=document_field[0]
                                                 )

    def get_json_data(self, request, *args, **kwargs):

        if request.method == 'POST':
            data = json.loads(request.body.decode('utf-8'))
            doc = Document.objects.get(pk=data['document_id'])
            user = request.user
            selection_range = data['ranges'][0]

            document_field_id = data.get('document_field')
            document_field = None
            if document_field_id is not None:
                document_field, created = DocumentField.objects.get_or_create(pk=document_field_id)

            sel_start = selection_range['startOffset']
            sel_end = selection_range['endOffset']

            a = DocumentAnnotation.objects.create(document=doc,
                                                  start=selection_range['start'],
                                                  end=selection_range['end'],
                                                  start_offset=sel_start,
                                                  end_offset=sel_end,
                                                  quote=data['quote'],
                                                  comment=data.get('text'),
                                                  user=user,
                                                  document_field=document_field
                                                  )
            tags = data.get('tags')
            if tags:
                for tag in tags:
                    tag_obj = DocumentAnnotationTag.objects.get_or_create(pk=tag)[0]
                    a.tags.add(tag_obj)

            DocumentAnnotationStorageView.trigger_retraining_model(data['document_class'],
                                                                   data['document_id'])

            return _to_dto(a)
        elif request.method == 'PUT':
            data = json.loads(request.body.decode('utf-8'))

            suggested_by_system = data.get('user_id') is None

            if suggested_by_system:
                a = DocumentAnnotationStorageView.replace_annotation_suggested_by_system(request,
                                                                                         data)
            else:
                document_field_id = data.get('document_field')
                document_field = None
                if document_field_id is not None:
                    document_field, created = DocumentField.objects.get_or_create(
                        pk=document_field_id)

                a = DocumentAnnotation.objects.get(pk=data['id'])
                a.document = Document.objects.get(pk=data['document_id'])
                a.user = request.user
                selection_range = data['ranges'][0]
                a.start = selection_range['start']
                a.end = selection_range['end']
                a.start_offset = selection_range['startOffset']
                a.end_offset = selection_range['endOffset']
                a.quote = data['quote']
                a.comment = data['text']
                a.document_field = document_field
                a.save()

                existing_tags = list(a.tags.all())
                existing_tag_ids = [tag.pk for tag in existing_tags]
                new_tag_ids = data.get('tags') or []

                for tag in existing_tags:
                    if tag.pk not in new_tag_ids:
                        a.tags.remove(tag)

                for tag_id in new_tag_ids:
                    if tag_id not in existing_tag_ids:
                        a.tags.add(DocumentAnnotationTag
                                   .objects.get_or_create(pk=tag_id,
                                                          defaults={'id': tag_id})[0])
            DocumentAnnotationStorageView.trigger_retraining_model(data['document_class'],
                                                                   data['document_id'])

            return _to_dto(a)
        elif request.method == 'DELETE':
            data = json.loads(request.body.decode('utf-8'))
            suggested_by_system = data.get('user_id') is None

            if suggested_by_system:
                DocumentAnnotationStorageView.replace_annotation_suggested_by_system(request, data)
            else:
                a = DocumentAnnotation.objects.get(pk=data['id'])
                a.delete()
            DocumentAnnotationStorageView.trigger_retraining_model(data['document_class'],
                                                                   data['document_id'])
        return None


class FieldEditorBackendView(JSONResponseView):
    def get_json_data(self, request, *args, **kwargs):
        if request.method == 'PUT':
            data = json.loads(request.body.decode('utf-8'))
            field_code = data.get('field')
            if not field_code:
                return {
                    'error': None,
                    'value': data.get('value')
                }
            doc_class_name, field = field_code.split('__')
            value = data['value']

            doc_class_fields = DOCUMENT_FIELDS.get(doc_class_name)
            if not doc_class_fields:
                return {
                    'error': 'Unknown document class: {0}'.format(doc_class_name),
                    'value': None
                }
            field_config = doc_class_fields.get(field)

            if not field_config:
                return {
                    'error': 'Field {1} is not configured for document class: {0}'.format(
                        doc_class_name, field),
                    'value': None
                }

            doc_id = kwargs.get('document_id')
            doc_class = field_config.document_class

            doc = doc_class.objects.get(pk=doc_id)

            if field_config:
                val = field_config.set_value_from_selection(doc, value)
                doc.save()
                return {
                    'error': None,
                    'value': val
                }
            else:
                return {
                    'error': 'No such field: {0}'.format(field),
                    'value': None
                }

        return None


class DocumentFieldsView(JSONResponseView):
    def get_json_data(self, request, *args, **kwargs):
        doc_class_name = kwargs.get('document_class')
        doc_class_fields = DOCUMENT_FIELDS.get(doc_class_name)
        if not doc_class_fields:
            return []

        return sorted([{
            'code': f.field_code,
            'name': f.name,
            'type': f.field_type.value
        } for f_name, f in doc_class_fields.items()], key=lambda k: k['name'])


class BuildFieldDetectorDatasetTaskView(BaseAjaxTaskView):
    task_name = 'Build Field Detector Dataset'
    form_class = BuildFieldDetectorDatasetForm
    html_form_class = 'popup-form build-field-detector-dataset-form'
    metadata = dict(
        result_links=[{'name': 'View Lease Documents', 'link': 'lease:lease-dashboard'}])


class TrainFieldDetectorModelTaskView(BaseAjaxTaskView):
    task_name = 'Train Field Detector Model'
    form_class = TrainFieldDetectorModelForm
    html_form_class = 'popup-form train-field-detector-model-form'
    metadata = dict(
        result_links=[{'name': 'View Lease Documents', 'link': 'lease:lease-dashboard'}])
