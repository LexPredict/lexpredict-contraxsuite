from apps.task.views import BaseAjaxTaskView
from .forms import IManageSyncTaskForm
from .tasks import IManageSynchronization


class IManageSyncTaskView(BaseAjaxTaskView):
    form_class = IManageSyncTaskForm
    html_form_class = 'popup-form imanage-sync'
    task_name = IManageSynchronization.name
