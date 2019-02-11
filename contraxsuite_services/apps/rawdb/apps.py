from django.apps import AppConfig
from django.conf import settings


class RawdbConfig(AppConfig):
    name = 'apps.rawdb'
    verbose_name = "Rawdb"

    def ready(self):
        from apps.document.events import events
        from apps.document.models import DocumentField, DocumentType, Document
        from apps.common.log_utils import ProcessLogger

        def reindex_on_doc_type_change(document_type: DocumentType):
            from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
            if APP_VAR_DISABLE_RAW_DB_CACHING.val:
                return

            from apps.rawdb.tasks import auto_reindex_not_tracked
            from apps.task.tasks import call_task_func
            call_task_func(auto_reindex_not_tracked, (document_type.code,), None, queue=settings.CELERY_QUEUE_SERIAL)

        def reindex_on_field_change(document_field: DocumentField):
            from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
            if APP_VAR_DISABLE_RAW_DB_CACHING.val:
                return

            from apps.rawdb.tasks import auto_reindex_not_tracked
            from apps.task.tasks import call_task_func
            from apps.document.models import DocumentField

            try:
                if document_field.document_type:
                    call_task_func(auto_reindex_not_tracked, (document_field.document_type.code,),
                                   None, queue=settings.CELERY_QUEUE_SERIAL)
            except DocumentField.DoesNotExist:
                pass

        def document_change_listener(event: events.DocumentChangedEvent):
            from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
            if APP_VAR_DISABLE_RAW_DB_CACHING.val:
                return
            from apps.rawdb.field_value_tables import cache_document_fields
            log = event.log or ProcessLogger()
            cache_document_fields(log=log,
                                  document=event.document,
                                  cache_generic_fields=event.generic_fields_changed,
                                  cache_user_fields=event.user_fields_changed,
                                  pre_detected_field_codes_to_suggested_values=event.pre_detected_field_values)

        def document_delete_listener(obj: Document):
            from apps.rawdb.app_vars import APP_VAR_DISABLE_RAW_DB_CACHING
            if APP_VAR_DISABLE_RAW_DB_CACHING.val:
                return
            from apps.rawdb.field_value_tables import delete_document_from_cache
            delete_document_from_cache(obj.pk)

        def document_field_change_listener(obj: DocumentField):
            reindex_on_field_change(obj)

        def document_field_delete_listener(obj: DocumentField):
            reindex_on_field_change(obj)

        def document_type_change_listener(obj: DocumentType):
            reindex_on_doc_type_change(obj)

        def document_type_delete_listener(_obj: DocumentType):
            pass

        events.on_document_change.add_listener(document_change_listener)
        events.on_document_deleted.add_listener(document_delete_listener)
        events.on_document_field_updated.add_listener(document_field_change_listener)
        events.on_document_field_deleted.add_listener(document_field_delete_listener)
        events.on_document_type_updated.add_listener(document_type_change_listener)
        events.on_document_type_deleted.add_listener(document_type_delete_listener)
