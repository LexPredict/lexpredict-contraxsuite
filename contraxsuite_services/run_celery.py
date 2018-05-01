import subprocess
import time
from celery.task.control import inspect
from apps.celery import app


attempts = 5
tasks = 30


def start():
    print('Start celery')
    cmd = 'celery multi start worker -A apps -l INFO -B --concurrency=2'
    subprocess.Popen(cmd.split())
    time.sleep(10)
    # argv = [
    #     'worker',
    #     '--app=apps',
    #     '--concurrency=2',
    #     '--loglevel=INFO',
    #     '-B',
    # ]
    # app.worker_main(argv)


def stop():
    print('Stop celery')
    cmd = 'celery multi stop worker -A apps'
    subprocess.Popen(cmd.split())
    time.sleep(5)


for attempt in range(attempts):
    print('Attempt #{}'.format(attempt))
    start()
    i = inspect()
    registered_tasks = i.registered_tasks()
    if not registered_tasks:
        stop()
        continue
    registered_tasks_len = len(list(i.registered_tasks().items())[0][1])
    if registered_tasks_len != tasks:
        stop()
        continue
    else:
        break
