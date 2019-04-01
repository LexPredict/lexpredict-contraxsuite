from apps.common.models import AppVar

APP_VAR_DISABLE_EVENT_NOTIFICATIONS = AppVar.set(
    'disable_event_notifications', False, '''Disables sending any notifications bound to document events.''')
