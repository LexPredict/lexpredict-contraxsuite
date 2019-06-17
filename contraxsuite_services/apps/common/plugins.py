import importlib
from typing import Dict, Any

from django.conf import settings


def collect_plugins_in_apps(module_name: str, module_attr: str) -> Dict[str, Any]:
    """
    Searches for [module_name].py in each app. If there is such module and it has
    [module_attr] attribute in it then add it to the resulting dictionary with key = application name.

    This way we can provide a pluggable architecture for various subsystems.
    For example:
        Documents app searches for "python_coded_fields.py" in each available app.
        It takes PYTHON_CODED_FIELDS list from each found module and puts fields from it in the
        big field registry.
    """
    res = dict()
    custom_apps = [i for i in settings.INSTALLED_APPS if i.startswith('apps.')]
    for app_name in custom_apps:
        module_str = '{0}.{1}'.format(app_name, module_name)
        try:
            app_module = importlib.import_module(module_str)
            if hasattr(app_module, module_attr):
                plugin = getattr(app_module, module_attr)
                res[app_name] = plugin
        except ImportError:
            continue

    return res
