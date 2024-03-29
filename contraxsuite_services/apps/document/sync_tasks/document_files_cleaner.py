"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""
# -*- coding: utf-8 -*-

from typing import List, Any, Callable

from apps.common.file_storage import get_file_storage
from apps.common.logger import CsLogger

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DocumentFilesCleaner:
    logger = CsLogger.get_django_logger()

    @staticmethod
    def delete_document_files(paths: List[str], logger: Callable = None) -> None:
        stor = get_file_storage()
        for path in paths:
            try:
                stor.delete_document(path)
            except Exception as e:
                msg = f'Unable to delete file "{path}" in {type(stor).__name__}'
                DocumentFilesCleaner.log_error(msg, e, logger)

    @staticmethod
    def log_error(msg: str, e: Any = None, logger: Callable = None) -> None:
        if logger:
            logger(msg, e)
            return
        task_logger = DocumentFilesCleaner.logger
        task_logger.error(msg, e)
