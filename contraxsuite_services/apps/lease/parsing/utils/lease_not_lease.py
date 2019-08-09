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

import os
import shutil

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


"""
    Arranges output of prepare_contracts_db.py to two folders: "lease" and "not_lease" depending on
    the category name.
"""


if __name__ == '__main__':
    src = os.path.expanduser('~/lexpredict/misc/contracts_by_category')

    dst_lease = os.path.expanduser('~/lexpredict/misc/lease/lease')
    dst_not_lease = os.path.expanduser('~/lexpredict/misc/lease/not_lease')

    os.makedirs(dst_lease, exist_ok=True)
    os.makedirs(dst_not_lease, exist_ok=True)


    def process_dir(dir_path: str, dst_lease: str, dst_not_lease: str):
        for dir_path, dir_names, file_names in os.walk(dir_path):
            print('Dir: ' + dir_path)

            for fn in file_names:
                print(dir_path + '/' + fn)
                if 'leas' in dir_path:
                    shutil.copy(src=os.path.join(dir_path, fn), dst=os.path.join(dst_lease, fn))
                else:
                    shutil.copy(src=os.path.join(dir_path, fn), dst=os.path.join(dst_not_lease, fn))


    process_dir(src, dst_lease, dst_not_lease)
