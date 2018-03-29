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

import os

from apps.task.utils.text.segment import segment_paragraphs

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def is_parties_spec(txt: str) -> bool:
    return True


if __name__ == '__main__':
    src = os.path.expanduser('~/lexpredict/misc/lease/lease')

    dst_root = os.path.expanduser('~/lexpredict/misc/lease/party_spec/train')

    dst_parties_spec = os.path.join(dst_root, 'parties_spec')
    dst_not_parties_spec = os.path.join(dst_root, 'not_parties_spec')

    os.makedirs(dst_parties_spec, exist_ok=True)
    os.makedirs(dst_not_parties_spec, exist_ok=True)

    for dir_path, dir_name, files in os.walk(src):
        for f in files:
            with open(os.path.join(dir_path, f), 'r') as ff:
                text = ff.read()
            paragraphs = segment_paragraphs(text)

            i = 0
            for p in paragraphs:
                i = i + 1
                dst_dir = dst_parties_spec if is_parties_spec(p) else dst_not_parties_spec
                dst_file = os.path.join(dst_dir, '{0}_{1}.txt'.format(os.path.splitext(f)[0], i))
                with open(dst_file, 'w') as ff:
                    ff.write(p)
