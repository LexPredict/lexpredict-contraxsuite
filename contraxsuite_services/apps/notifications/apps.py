from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = 'apps.notifications'
    verbose_name = "Notifications"

    def ready(self):
        # noinspection PyUnresolvedReferences
        import apps.notifications.signals
        super().ready()

