from django.apps import AppConfig


class DumpConfig(AppConfig):
    name = 'apps.dump'
    verbose_name = "Dump"

    def ready(self):
        super().ready()
