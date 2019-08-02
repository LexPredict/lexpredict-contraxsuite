from typing import List

from apps.common.file_storage import get_file_storage


class DocumentFilesCleaner:
    @staticmethod
    def delete_documents_files(paths: List[str]):
        stor = get_file_storage()
        for path in paths:
            # os.path.join() won't work here
            path = path if path.startswith('/') else '/' + path
            full_path = stor.documents_path + path
            try:
                stor.delete_file(full_path)
            except Exception as e:
                raise Exception(f'DocumentFilesCleaner: error deleting ' +
                                f'"{path}": {e}')
