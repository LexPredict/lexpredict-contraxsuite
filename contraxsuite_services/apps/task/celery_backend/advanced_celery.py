from celery import Celery

from apps.common.utils import fast_uuid
from apps.task.models import Task


class AdvancedCelery(Celery):
    def send_task(self, name, args=None, kwargs=None, countdown=None, eta=None, task_id=None,
                  producer=None, connection=None, router=None, result_cls=None, expires=None,
                  publisher=None, link=None, link_error=None, add_to_parent=True, group_id=None,
                  retries=0, chord=None, reply_to=None, time_limit=None, soft_time_limit=None,
                  root_id=None, parent_id=None, route_name=None, shadow=None, chain=None,
                  task_type=None, **options):
        task_id = task_id or str(fast_uuid())

        if options.get('as_main_task', False):
            root_id = None

        Task.objects.init_task(task_id, name, root_id,
                               'Args: {0}\nKwargs: {1}'.format(str(args),
                                                               str(kwargs)))  # type: Task
        return super().send_task(name, args, kwargs, countdown, eta, task_id, producer, connection,
                                 router, result_cls, expires, publisher, link, link_error,
                                 add_to_parent, group_id, retries, chord, reply_to, time_limit,
                                 soft_time_limit, root_id, parent_id, route_name, shadow, chain,
                                 task_type, **options)
