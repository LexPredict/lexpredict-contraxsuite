import regex as re
from threading import Lock
from django.apps import apps
from apps.common.singleton import Singleton


model_class_dictionary_lock = Lock()


@Singleton
class ModelClassDictionary:
    DEPRECATED_CLASS_NAMES = re.compile(r'^SoftDelete')

    def __init__(self) -> None:
        super().__init__()
        with model_class_dictionary_lock:
            self.models = []
            self.table_by_model = {}
            self.model_by_table = {}
            self.read_models()
            self.reg_name_parts = re.compile(r"[A-Z_]+[a-z0-9]+")

    def read_models(self) -> None:
        self.models = apps.get_models(include_auto_created=True, include_swapped=True)
        for model in self.models:
            if self.DEPRECATED_CLASS_NAMES.match(model.__name__):
                continue
            self.table_by_model[model] = model._meta.db_table
            self.model_by_table[self.table_by_model[model]] = model
        return

    def get_model_class_name(self, table_name: str) -> str:
        return self.model_by_table[table_name].__name__

    def get_model_class_name_hr(self, table_name: str) -> str:
        name = self.get_model_class_name(table_name)
        matches = [i.group(0) for i in self.reg_name_parts.finditer(name)]
        return ' '.join(matches)
