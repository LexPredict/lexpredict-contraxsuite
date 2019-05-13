from django.apps import AppConfig


class RawdbConfig(AppConfig):
    name = 'apps.rawdb'
    verbose_name = "Rawdb"

    def ready(self):
        # noinspection PyUnresolvedReferences
        import apps.rawdb.signals
        super().ready()
