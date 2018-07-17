import sys
from django.db import close_old_connections, connections


def is_celery_worker():
    for arg in sys.argv:
        if arg == 'worker':
            return True
    return False


class TaskUtils:
    __is_celery_worker = is_celery_worker()
    __connection_initialization_finished = False

    @staticmethod
    def is_celery_worker():
        return TaskUtils.__is_celery_worker

    @staticmethod
    def prepare_task_execution():
        """

        Clearing of old database connections for CONN_MAX_AGE option (database connection settings)

        """
        if not TaskUtils.is_celery_worker():
            return

        try:
            if TaskUtils.__connection_initialization_finished:
                close_old_connections()
            else:
                for conn in connections.all():
                    conn.close()
                    TaskUtils.__connection_initialization_finished = True
        except Exception:
            pass
