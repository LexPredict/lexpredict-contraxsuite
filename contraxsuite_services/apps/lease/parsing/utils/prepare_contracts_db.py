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

import json
import os
from concurrent.futures import ThreadPoolExecutor
from subprocess import call

import html2text

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


"""
Prepares a dataset of examples of different types of contracts.
Input:
    Unpacked archive from https://www.lawinsider.com/education.
    Dir structure: Any dir tree with JSON + HTML files. Each JSON file contains "category" field - a category of
    the HTML file having the same name as the JSON file.

Output:
    Dir structure:
        category1:
            file11.txt
            ...
            file1N.txt
        ...
        categoryM:
            fileM1.txt
            ...
            fileMK.txt
The output dir structure is ready for loading via sklearn load_files() function.
"""


def escape_fn(filename):
    keep_characters = (' ', '.', '_')
    return ''.join(c if c.isalnum() or c in keep_characters else '_' for c in filename).rstrip()


def get_text(html_file):
    with open(html_file, 'r') as f:
        text = f.read()
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.unicode_snob = True
    h.body_width = 0
    h.style = 'compact'

    return h.handle(text)


def process_file(dir_path, fn, dst_root):
    print('File: ' + os.path.join(dir_path, fn))
    description = json.load(open(os.path.join(dir_path, fn)))
    category = description['category'] or 'misc'
    category = escape_fn(category)
    txt_dst = os.path.join(dst_root, category, os.path.splitext(fn)[0] + '.txt')
    if os.path.isfile(txt_dst):
        return
    os.makedirs(os.path.join(dst_root, category), exist_ok=True)
    html_fn = os.path.splitext(fn)[0] + '.html'
    html_src = os.path.join(dir_path, html_fn)
    txt_dst = os.path.join(dst_root, category, os.path.splitext(fn)[0] + '.txt')
    call(['/bin/sh', '-c', 'lynx -dump {0} > {1}'.format(html_src, txt_dst)])
    # text = get_text(html_src)
    # with open(txt_dst, 'w') as wf:
    #    wf.write(text)


def process_dir(dir_path: str, dst_root: str, executor: ThreadPoolExecutor):
    for dir_path, dir_names, file_names in os.walk(dir_path):
        print('Dir: ' + dir_path)
        for fn in file_names:
            if fn.endswith('.json'):
                executor.submit(process_file, dir_path, fn, dst_root)


if __name__ == '__main__':
    src_dir = os.path.expanduser('~/lexpredict/misc/contracts_2010')
    dst = os.path.expanduser('~/lexpredict/misc/contracts_by_category')
    with ThreadPoolExecutor(max_workers=8) as executor:
        process_dir(src_dir, dst, executor)
        executor.shutdown(wait=True)
