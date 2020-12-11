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

# Enhanced Django QuerySet printing using PrettyPrinter
# Example usage: dropped into and employed within an IPython notebook.

# --- PRETTYPRINT -------------------------------------------------------------
# A PrettyPrinter object contains a _dispatch dictionary.
# This lookup table contains (key, value) pairs wherein the key corresponds to
# an object's __repr__ method, and the value is a special _pprint_<OBJECT>
# method. The PrettyPrint method pprint() queries the dictionary to call the
# appropriate object printer.

# --- _pprint_queryset() ------------------------------------------------------
# This printing method is nearly identical to _pprint_list().
# It is added to the _dispatch dictionary as the QuerySet's __repr__ function.

# --- _pprint_qs() ------------------------------------------------------------
# A wrapper method allowing for easy slicing, stream selection, and simple
# statistical report printing. This method is optional.

# --- Resources ---------------------------------------------------------------
# Derived from: Martjin Pieters: https://stackoverflow.com/a/40828239/4189676
# pprint source: https://github.com/python/cpython/blob/master/Lib/pprint.py

import django
import pprint

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def _pprint_queryset(printer, object, stream, indent, allowance, context, level) -> None:
    stream.write('<QuerySet [\n ')
    printer._format_items(object, stream, indent, allowance, context, level)
    stream.write('\n]>')


pprint.PrettyPrinter._dispatch[django.db.models.query.QuerySet.__repr__] = _pprint_queryset


def pprint_qs(queryset: django.db.models.query.QuerySet, end: int = 10, start: int = 0,
              indent: int = 3, stream=None, stats: bool = False) -> None:
    pprint.pprint(queryset[start:end], indent=indent, stream=stream)
    if stats:
        count = queryset.count()
        if count:
            diff = abs(end - start)
            showing = diff if diff < count else count
            coverage = showing / count
            percent_coverage = round(coverage * 100, 3)
            report = f'showing: {showing} of {count} | {percent_coverage}%'
            print('-' * 119)
            print(report.rjust(119))
