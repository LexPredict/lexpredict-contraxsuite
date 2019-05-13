from django.apps import AppConfig


class DocumentConfig(AppConfig):
    name = 'apps.document'
    verbose_name = "Document"

    def ready(self):
        # noinspection PyUnresolvedReferences
        import apps.document.signals
        super().ready()

