from typing import List


def run_detect_field_values_for_document(document_id: int):
    from apps.task.tasks import call_task_func
    from apps.document.tasks import DetectFieldValues
    call_task_func(DetectFieldValues.detect_field_values_for_document, (document_id, False, False), None, visible=False)


def run_detect_field_values_as_sub_tasks(parent: 'ExtendedTask', document_ids: List[str], do_not_write: bool = False):
    from apps.document.tasks import DetectFieldValues
    args = [(document_id, do_not_write, False) for document_id in document_ids]
    parent.run_sub_tasks('Detect Field Values', DetectFieldValues.detect_field_values_for_document, args)
