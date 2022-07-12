import pickle
import time

from celery.states import READY_STATES, REVOKED
from django.core.management.base import BaseCommand
from gensim.models import Doc2Vec

from apps.analyze.models import MLModel
from apps.analyze.tasks import TrainDoc2VecModel
from apps.common.file_storage import get_file_storage
from apps.project.models import Project
from apps.task.models import Task
from apps.task.tasks import call_task


class Command(BaseCommand):
    help = 'Removes old Doc2Vec models that raise error in current gensim version'

    def is_successful_gensim_3_to_4_migration(self,
                                              doc2vec_model: Doc2Vec,
                                              model_name: str,
                                              model_path: str):
        try:
            vector_size = doc2vec_model.dv.vector_size
            return True
        except AttributeError:
            self.stdout.write(self.style.ERROR(f'Doc2Vec error for outdated {model_name} '
                                               f'({model_path}). Removing model ...'))
            return False

    def update_default_mlmodel(self, object_type, languages):
        for lang in languages:
            if MLModel.objects.filter(target_entity='transformer',
                                      apply_to=object_type,
                                      language=lang,
                                      default=False).exists() \
                    and not MLModel.objects.filter(target_entity='transformer',
                                                   apply_to=object_type,
                                                   language=lang,
                                                   default=True).exists():
                model = MLModel.objects.filter(target_entity='transformer', apply_to=object_type,
                                               language=lang).order_by('id').last()
                model.default = True
                model.save()

    def add_arguments(self, parser):
        parser.add_argument('-dt', "--train_documents_transformer", action='store_true',
                            help='train Doc2Vec model from Document queryset')
        parser.add_argument('-tut', "--train_text_units_transformer", action='store_true',
                            help='train Doc2Vec model from Text Unit queryset')
        parser.add_argument('-ids', "--project_ids", action='store', default='',
                            help='set Project ids for training Doc2Vec model from Document '
                                 'queryset (should be string of numbers, separated with space)')

    def handle(self, *args, **options):
        train_documents_transformer = options['train_documents_transformer']
        train_text_units_transformer = options['train_text_units_transformer']
        project_ids = [int(pid) for pid in options['project_ids'].split(' ') if pid]

        file_storage = get_file_storage()

        for model in MLModel.objects.filter(target_entity='transformer'):
            try:
                file_bytes = file_storage.read(model.model_path)
                doc2vec_model = pickle.loads(file_bytes)
            except Exception:
                self.stdout.write(self.style.ERROR(f'Doc2Vec model {model.name} was not loaded!'))
                continue
            if not doc2vec_model:
                self.stdout.write(self.style.ERROR(f'Doc2Vec model {model.name} is empty!'))
                continue

            if not self.is_successful_gensim_3_to_4_migration(doc2vec_model,
                                                              model.name, model.model_path):
                # Remove model files
                try:
                    file_storage.delete_file(model.model_path)
                except Exception:
                    self.stdout.write(self.style.ERROR(f'Doc2Vec model {model.name} with path '
                                                       f'{model.model_path} was not removed!'))

                # Remove model object
                model.delete()

        # Prepare data for transformers
        documents_training_data = {
            'source': 'document',
            'vector_size': 100,
            'window': 10,
            'min_count': 10,
            'dm': 1,
            'build_vectors': False,
        }
        if project_ids:
            documents_training_data['project_ids'] = project_ids
        text_unit_training_data = documents_training_data.copy()
        text_unit_training_data['source'] = 'text_unit'
        text_unit_training_data['project_ids'] = list(
            Project.objects.all().values_list('id', flat=True))

        # Call tasks to train models and get initial tasks statuses
        task_doc_id = call_task(TrainDoc2VecModel, **documents_training_data) \
            if train_documents_transformer else None
        try:
            task_doc_status = Task.objects.get(id=task_doc_id).status \
                if task_doc_id else REVOKED
        except Task.DoesNotExist:
            task_doc_status = REVOKED

        task_text_unit_id = call_task(TrainDoc2VecModel, **text_unit_training_data) \
            if train_text_units_transformer else None
        try:
            task_text_unit_status = Task.objects.get(id=task_text_unit_id).status \
                if task_text_unit_id else REVOKED
        except Task.DoesNotExist:
            task_text_unit_status = REVOKED

        is_update_default_document_transformer = False
        is_update_default_text_unit_transformer = False

        languages = set(MLModel.objects.filter(target_entity='transformer').values_list('language',
                                                                                        flat=True))
        # Wait for tasks to be finished
        self.stdout.write(self.style.NOTICE("Waiting for models to be retrained ..."))

        while task_doc_status not in READY_STATES or task_text_unit_status not in READY_STATES:
            # Update tasks statuses
            try:
                task_doc_status = Task.objects.get(id=task_doc_id).status \
                    if task_doc_id else REVOKED
            except Task.DoesNotExist:
                task_doc_status = REVOKED

            try:
                task_text_unit_status = Task.objects.get(id=task_text_unit_id).status \
                    if task_text_unit_id else REVOKED
            except Task.DoesNotExist:
                task_text_unit_status = REVOKED

            # Update default transformers
            if task_doc_status in READY_STATES \
                    and not is_update_default_document_transformer:
                self.update_default_mlmodel('document', languages)
                is_update_default_document_transformer = True
            if task_text_unit_status in READY_STATES \
                    and not is_update_default_text_unit_transformer:
                self.update_default_mlmodel('text_unit', languages)
                is_update_default_text_unit_transformer = True

            time.sleep(1)
