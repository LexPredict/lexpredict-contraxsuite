import sys
from typing import List


def run_detect_field_values_for_document(document_id: int):
    from urls import custom_apps
    from apps.task.tasks import call_task_func
    for app_name in custom_apps:
        module_str = 'apps.%s.tasks' % app_name
        task_module = sys.modules.get(module_str)
        detector_task = getattr(task_module, 'DetectFieldValues', None)
        if detector_task and hasattr(detector_task, 'detect_field_values_for_document'):
            task_func = getattr(detector_task, 'detect_field_values_for_document')
            call_task_func(task_func, (document_id, False), None, visible=False)


def run_detect_field_values_as_sub_tasks(parent: 'ExtendedTask', document_ids: List[str], do_not_write: bool = False):
    from urls import custom_apps
    task_funcs = []
    for app_name in custom_apps:
        module_str = 'apps.%s.tasks' % app_name
        task_module = sys.modules.get(module_str)
        detector_task = getattr(task_module, 'DetectFieldValues', None)
        if detector_task and hasattr(detector_task, 'detect_field_values_for_document'):
            task_funcs.append((app_name, getattr(detector_task, 'detect_field_values_for_document')))

    if task_funcs:
        for app_name, task_func in task_funcs:
            args = []
            for document_id in document_ids:
                args.append((document_id, do_not_write))
                parent.run_sub_tasks('Detect Field Values: {0}'.format(app_name), task_func, args)
