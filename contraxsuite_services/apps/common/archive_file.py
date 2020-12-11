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


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import tarfile
import zipfile
from typing import Any, Optional
import magic


python_magic = magic.Magic(mime=True)


class ArchiveFile:
    zip_exts = {
        '.zz', '.gz', '.tgz', '.mg', '.ta',
        '.ace', '.b6z', '.sit', '.ice', '.zpaq',
        '.sda', '.c0', '.qda', '.lha', '.xp3',
        '.afa', '.zoo', '.ucn', '.ha', '.ba',
        '.lzx', '.car', '.dgc', '.uc2', '.arc,',
        '.sqx', '.cfs', '.jar', '.war', '.alz',
        '.cpt', '.hki', '.sea', '.sitx', '.ur2',
        '.pim', '.tar.xz', '.cab', '.r.lz', '.pea',
        '.tar.bz2', '.paq6,', '.xar', '.sfx', '.uha',
        '.tar', '.ear', '.gca', '.zip,', '.ark',
        '.txz', '.zip', '.tbz2,', '.rk', '.dd',
        '.lzh,', '.yz1', '.bh', '.ue2', '.apk',
        '.7z', '.tar.Z', '.kgb', '.rar', '.shk',
        '.s7z', '.tlz', '.parti', '.arj', '.pak',
        '.uca', '.dmg', '.b1', '.cdx', '.wim',
        '.uc', '.u', '.sen', '.pa', '.paq8',
        '.dar', '.pit'
    }

    @staticmethod
    def check_file_is_archive(file_path: str, file_ext: str) -> bool:
        if file_ext in ArchiveFile.zip_exts or not file_ext:
            if tarfile.is_tarfile(file_path) or zipfile.is_zipfile(file_path):
                return True
        return False

    @staticmethod
    def guess_file_mime_type(file: Any) -> Optional[str]:
        try:
            mt = python_magic.from_buffer(file.read(1024))
            return mt
        except:
            return None
