import logging
from typing import Dict, List

from apps.common.plugins import collect_plugins_in_apps
from .field_types import FieldType

FIELD_TYPE_REGISTRY = dict()  # type: Dict[str, FieldType]


def init_field_type_registry():
    """
    Searches for module called 'python_coded_fields' in each app. If there is such module and it has
    'PYTHON_CODED_FIELDS' list attribute in it then try to add each field from this list to
    PYTHON_CODED_FIELDS_REGISTRY.
    Additionally updates choice values of DocumentField.python_coded_field model.
    :return:
    """
    logging.info('Going to register Python-coded document fields from all Django apps...')

    plugins = collect_plugins_in_apps('field_types',
                                      'FIELD_TYPES')  # type: Dict[str, List[FieldType]]
    for app_name, field_types in plugins.items():
        try:
            field_types = list(field_types)
        except TypeError:
            raise TypeError('{0}.field_types.FIELD_TYPES is not iterable'.format(app_name))

        i = -1
        for field_type in field_types:
            i += 1
            try:
                FIELD_TYPE_REGISTRY[field_type.code] = field_type
            except AttributeError:
                raise AttributeError('{0}.field_types.FIELD_TYPES[{1}] is something wrong'
                                     .format(app_name, i))
            print('Registered field type: {0} ({1})'.format(field_type.title, field_type.code))

    from apps.document.models import DocumentField
    for f in DocumentField._meta.fields:
        if f.name == 'type':
            f.choices = list((k, FIELD_TYPE_REGISTRY[k].title or k)
                             for k in sorted(FIELD_TYPE_REGISTRY))
            break
