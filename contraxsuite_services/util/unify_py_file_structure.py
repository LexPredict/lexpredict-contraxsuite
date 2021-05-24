"""
    Unify project files structure, including:
    - header block (copyright info)
    - custom docstring block describing file function
    - coding block
    - imports block
    - author block (include version, licence, copyright, maintainer and email as well)
    - code block
"""

import datetime
import os
import re
import sys


header = '''
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
'''

coding = '''# -*- coding: utf-8 -*-'''

author = '''
__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-0000, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/0.0.0/LICENSE"
__version__ = "0.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"
'''


header_ptn = re.escape(header.strip())
coding_ptn = re.escape(coding.strip())
author_ptn = re.escape(author.strip()).replace("0\.0\.0", "\d\.\d\.\d+").replace('0000', '\d{4}')

py_file_struc_ptn = f'(?P<header>{header_ptn}){{,1}}\n*' \
                    f'(?P<docstr>(?:\'\'\'.+?\'\'\'|""".+?""")){{,1}}\n*' \
                    f'(?P<coding>{coding_ptn}){{,1}}\n*' \
                    f'(?P<imports>(?:^(?:#|import|from|\s{{4,}})[^\n]+\n+)+){{,1}}\n*' \
                    f'(?P<author>{author_ptn}){{,1}}\n*' \
                    f'(?P<code>.*)'
py_file_struc_re = re.compile(py_file_struc_ptn, re.M | re.S)

release_version_re = re.compile(r'\d\.\d\.\d+')

exclude_paths = ['settings.py', 'local_settings.py', 'manage.py']


def unify_file_structure(release_number):
    base_dir = os.path.normpath(os.path.join(os.path.abspath(__file__), '../..'))
    path = os.path.join(base_dir, 'apps')

    files = sorted([os.path.join(a, i)
                    for a, _, b in os.walk(path)
                    for i in b
                    if i.endswith('.py') and '/migrations' not in a])
    files = files + [os.path.join(base_dir, i) for i in os.listdir(base_dir)
                     if i.endswith('.py') and i not in exclude_paths]

    global author
    author = release_version_re.sub(release_number, author).replace('0000', str(datetime.datetime.now().year))

    for a_file in files:
        with open(a_file, 'r') as f:
            file_content_str = f.read()

        match = py_file_struc_re.fullmatch(file_content_str)

        if match:
            current_structure = match.groupdict()

            docstr = (current_structure['docstr'] or '').strip()
            imports = (current_structure['imports'] or '').strip()
            code = (current_structure['code'] or '').strip()
        else:
            imports = code = docstr = ''

        new_file_content = ''.join([
            header.strip(),
            '\n',
            coding.strip(),
            '\n' * 2,
            imports,
            '\n' * 2 if imports else '\n',
            author.strip(),
            '\n' * 3 if code else '',
            docstr.strip(), '\n' * 3 if docstr else '',
            code,
            '\n'
        ])

        # search problems
        if new_file_content.count('__author__') > 1:
            print(f'>>> WARN!!! Duplicated author block: {a_file}')
            # continue

        if new_file_content.count(header.strip()) > 1:
            print(f'>>> WARN!!! Duplicated copyright block: {a_file}')
            # continue

        with open(a_file, 'w') as f:
            f.write(new_file_content)
        print(f'Done: {a_file}')


if __name__ == '__main__':
    release_version = None
    args = sys.argv
    if len(args) == 1:
        print('Provide release number in format "1.2.3"')
        exit(1)
    if len(args) == 2:
        release_version = args[1]
        if not release_version_re.fullmatch(release_version):
            print(f'Wrong release number format "{release_version}"')
            exit(1)
    unify_file_structure(release_version)
