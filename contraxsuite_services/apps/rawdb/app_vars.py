from apps.common.models import AppVar
from apps.rawdb.constants import APP_VAR_DISABLE_RAW_DB_CACHING_NAME

APP_VAR_DISABLE_RAW_DB_CACHING = AppVar.set(
    APP_VAR_DISABLE_RAW_DB_CACHING_NAME, False,
    'Disables automatic caching of documents into raw db tables '
    'when document type / document field structures are changed '
    'via the admin app or when a document is loaded / changed. '
    'Values: true / false (json)')
