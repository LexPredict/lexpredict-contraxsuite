from apps.imanage_integration.forms import IManageSyncTaskForm
from apps.task.views import BaseAjaxTaskView


class IManageSyncTaskView(BaseAjaxTaskView):
    form_class = IManageSyncTaskForm
    html_form_class = 'popup-form imanage-sync'
