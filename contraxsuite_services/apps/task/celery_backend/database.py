from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.backends.base import BaseDictBackend

from apps.task.models import Task
from apps.task.utils.task_utils import TaskUtils
from django.conf import settings

TASK_NAME_UPDATE_MAIN_TASK = 'advanced_celery.update_main_task'


class DatabaseBackend(BaseDictBackend):
    """The Django database backend, using models to store task state."""

    TaskModel = Task

    subpolling_interval = 0.5

    @staticmethod
    @shared_task(bind=True, name=TASK_NAME_UPDATE_MAIN_TASK)
    def update_main_task(self, main_task_id: str):
        TaskUtils.prepare_task_execution()

        if self.request.id != main_task_id:
            Task.objects.update_main_task(main_task_id)

    def plan_update_main_task(self, main_task_id: str):
        self.update_main_task.apply_async(args=(main_task_id,), queue='serial')

    def _store_result(self, task_id, result, status,
                      traceback=None, request=None):
        """Store return value and status of an executed task."""
        metadata = {
            'children': self.current_task_children(request),
        }

        task_name = None

        if request:
            if hasattr(request, 'name') and request.name:
                task_name = request.name
            elif hasattr(request, 'task') and request.task:
                if hasattr(request.task, 'name') and request.task.name:
                    task_name = request.task.name
                else:
                    task_name = str(request.task)
            else:
                task_name = str(request)

        if not task_name:
            task_name = 'Unrecognized Task'
            print('Was unable to recognize task: task_id={0}\n'
                  'result={1}\n'
                  'status={2}\n'
                  'request={3}'.format(task_id, result, status, request))

        self.TaskModel.objects.store_result(
            task_id,
            request.root_id if request else None,
            task_name,
            result,
            status,
            traceback=traceback,
            metadata=metadata,
        )

        if settings.CELERY_UPDATE_MAIN_TASK_ON_EACH_SUB_TASK \
                and getattr(request, 'root_id', None) != task_id \
                and task_name != TASK_NAME_UPDATE_MAIN_TASK:
            self.plan_update_main_task(request.root_id)

        return result

    @staticmethod
    def task_to_decoded(task: TaskModel):
        return {
            'task_id': task.id,
            'name': task.name,
            'status': task.own_status,
            'result': task.result,
            'date_start': task.date_start,
            'traceback': task.traceback,
            'metadata': task.celery_metadata,
        }

    def exception_to_python(self, exc):
        try:
            return super().exception_to_python(exc)
        except KeyError:
            return exc

    def _get_task_meta_for(self, task_id):
        """Get task metadata for a task by id."""
        obj = self.TaskModel.objects.get_task(task_id)
        res = self.task_to_decoded(obj)
        meta = res.get('metadata') or dict()
        res.update(meta,
                   result=res.get('result'))
        return self.meta_from_decoded(res)

    def _forget(self, task_id):
        try:
            self.TaskModel.objects.get(task_id=task_id).delete()
        except self.TaskModel.DoesNotExist:
            pass

    def cleanup(self):
        """Delete expired metadata."""
        self.TaskModel.objects.delete_expired(self.expires)
