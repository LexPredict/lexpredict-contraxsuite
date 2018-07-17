import logging

from celery._state import connect_on_app_finalize
from celery.signals import worker_init

import settings


# Workaround for eternal running of celery.unlock_chord task
# when sub-tasks of the completed main tasks are deleted.

@worker_init.connect
def limit_chord_unlock_tasks(sender, **kwargs):
    sender.app.tasks['celery.chord_unlock'] = sender.app.tasks['celery.chord_unlock_shim']


@connect_on_app_finalize
def add_unlock_chord_task_shim(app):
    """
    Override native unlock_chord to support configurable max_retries.
    Most of the code is taken from the Celery builtins module.
    Two changes:
    1. Added max retries support to workaround Celery bug
    (https://github.com/celery/celery/issues/1700).
    2. Added check for status of the main task - if main task is done - then run of this
    chord_unlock is probably a mistake and it should just exit.
    (problem appears because we delete sub-task records from results db after the main
    task is completed)
    """
    from celery.canvas import maybe_signature
    from celery.exceptions import ChordError
    from celery.result import allow_join_result, result_from_tuple
    from celery.states import READY_STATES
    from apps.task.celery_backend.utils import now

    logger = logging.getLogger(__name__)

    max_retries = settings.CELERY_CHORD_UNLOCK_MAX_RETRIES

    @app.task(name='celery.chord_unlock_shim', shared=False, default_retry_delay=1,
              ignore_result=True, lazy=False, bind=True,
              max_retries=max_retries)
    def unlock_chord(self, group_id, callback, interval=None,
                     max_retries=max_retries, result=None,
                     Result=app.AsyncResult, GroupResult=app.GroupResult,
                     result_from_tuple=result_from_tuple, **kwargs):
        if interval is None:
            interval = self.default_retry_delay

        # check if the task group is ready, and if so apply the callback.
        callback = maybe_signature(callback, app)

        main_task = None
        try:
            main_task = Task.objects.get(id=self.request.parent_id)
            Task.objects.filter(id=self.request.id).update(main_task_id=self.request.parent_id)
        except:
            pass

        deps = GroupResult(
            group_id,
            [result_from_tuple(r, app=app) for r in result],
            app=app,
        )
        j = deps.join_native if deps.supports_native_join else deps.join

        try:
            ready = main_task.status in READY_STATES if main_task else deps.ready()
        except Exception as exc:
            raise self.retry(
                exc=exc, countdown=interval, max_retries=max_retries,
            )
        else:
            if not ready:
                raise self.retry(countdown=interval, max_retries=max_retries)

        callback = maybe_signature(callback, app=app)
        try:
            with allow_join_result():
                ret = j(timeout=3.0, propagate=True)
        except Exception as exc:
            try:
                culprit = next(deps._failed_join_report())
                reason = 'Dependency {0.id} raised {1!r}'.format(
                    culprit, exc,
                )
            except StopIteration:
                reason = repr(exc)
            logger.error('Chord %r raised: %r', group_id, exc, exc_info=1)
            app.backend.chord_error_from_stack(callback,
                                               ChordError(reason))
        else:
            try:
                callback.delay(ret)
            except Exception as exc:
                logger.error('Chord %r raised: %r', group_id, exc, exc_info=1)
                app.backend.chord_error_from_stack(
                    callback,
                    exc=ChordError('Callback error: {0!r}'.format(exc)),
                )

    return unlock_chord


# This import should go after the above shim overriding celery builtin method.
from celery import Celery  # noqa
from apps.common.utils import fast_uuid  # noqa
from apps.task.models import Task  # noqa
from apps.task.utils.task_utils import TaskUtils  # noqa


class AdvancedCelery(Celery):
    def send_task(self, name, args=None, kwargs=None, countdown=None, eta=None, task_id=None,
                  producer=None, connection=None, router=None, result_cls=None, expires=None,
                  publisher=None, link=None, link_error=None, add_to_parent=True, group_id=None,
                  retries=0, chord=None, reply_to=None, time_limit=None, soft_time_limit=None,
                  root_id=None, parent_id=None, route_name=None, shadow=None, chain=None,
                  task_type=None, **options):
        task_id = task_id or str(fast_uuid())

        TaskUtils.prepare_task_execution()

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
