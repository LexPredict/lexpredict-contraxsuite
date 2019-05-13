import os
from contextlib import contextmanager
from typing import Optional

from django.conf import settings


class FileAccessHandler:
    def list(self, rel_file_path: str = ''):
        pass

    @contextmanager
    def get_as_local_fn(self, rel_file_path: str):
        pass

    @contextmanager
    def get_document_as_local_fn(self, rel_file_path: str):
        p = os.path.join(settings.CELERY_FILE_ACCESS_DOCUMENTS_DIR, rel_file_path)

        with self.get_as_local_fn(p) as (fn, file_name):
            try:
                yield fn, rel_file_path
            finally:
                pass

    def list_documents(self, rel_file_path: str = ''):
        prefix = settings.CELERY_FILE_ACCESS_DOCUMENTS_DIR
        lst = self.list(prefix + rel_file_path)
        if not lst:
            return lst
        return [p[len(prefix):] for p in lst]

    def read(self, rel_file_path: str) -> Optional[bytes]:
        pass
