from typing import List

from apps.common.file_storage import get_file_storage

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DocumentFilesCleaner:
    @staticmethod
    def delete_document_files(paths: List[str]):
        stor = get_file_storage()
        for path in paths:
            try:
                stor.delete_document(path)

            except Exception as e:
                raise Exception(f'DocumentFilesCleaner: error deleting ' +
                                f'"{path}": {e}') from e
