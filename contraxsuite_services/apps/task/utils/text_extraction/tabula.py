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

import io
import json
import os
import subprocess

import pandas as pd
from django.conf import settings
from tabula import wrapper


# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def read_pdf(input_path,
             output_format='dataframe',
             encoding='utf-8',
             java_options=None,
             pandas_options=None,
             multiple_tables=False, **kwargs):
    '''Read tables in PDF.

    Args:
        input_path (str):
            File path of tareget PDF file.
        output_format (str, optional):
            Output format of this function (dataframe or json)
        encoding (str, optional):
            Encoding type for pandas. Default is 'utf-8'
        java_options (list, optional):
            Set java options like `-Xmx256m`.
        pandas_options (dict, optional):
            Set pandas options like {'header': None}.
        multiple_tables (bool, optional):
            This is experimental option. It enables to handle multple tables within a page.
            Note: If `multiple_tables` option is enabled, tabula-py uses not `pd.read_csv()`,
             but `pd.DataFrame()`. Make sure to pass appropreate `pandas_options`.
        kwargs (dict):
            Dictionary of option for tabula-java. Details are shown in `build_options()`

    Returns:
        Extracted pandas DataFrame or list.
    '''

    if output_format == 'dataframe':
        kwargs.pop('format', None)

    elif output_format == 'json':
        kwargs['format'] = 'JSON'

    if multiple_tables:
        kwargs['format'] = 'JSON'

    if java_options is None:
        java_options = []

    elif isinstance(java_options, str):
        java_options = [java_options]

    options = wrapper.build_options(kwargs)

    path, is_url = wrapper.localize_file(input_path)

    jars = [os.path.join(settings.JAR_BASE_PATH, jar) for jar in settings.JAI_JARS + [wrapper.JAR_PATH]]
    main_class = 'technology.tabula.CommandLineApp'
    java_options.append('-Dsun.java2d.cmm=sun.java2d.cmm.kcms.KcmsServiceProvider')

    args = ["java"] + java_options + ['-cp', ':'.join(jars)] + [main_class] + options + [path]

    try:
        output = subprocess.check_output(args)

    except FileNotFoundError as e:
        print("Error: {}".format(e))
        print("Error: {}".format(wrapper.JAVA_NOT_FOUND_ERROR))
        raise

    except subprocess.CalledProcessError as e:
        print("Error: {}".format(e.output.decode(encoding)))
        raise

    finally:
        if is_url:
            os.unlink(path)

    if len(output) == 0:
        return

    if pandas_options is None:
        pandas_options = {}

    fmt = kwargs.get('format')
    if fmt == 'JSON':
        if multiple_tables:
            return wrapper.extract_from(json.loads(output.decode(encoding)), pandas_options)

        else:
            return json.loads(output.decode(encoding))

    else:
        pandas_options['encoding'] = pandas_options.get('encoding', encoding)

        return pd.read_csv(io.BytesIO(output), **pandas_options)
