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

import importlib
import pkgutil
import sys
import traceback
from typing import Any, Dict

from django.conf import settings

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def import_submodules(package, recursive: bool = True):
    """ Import all submodules of a module, recursively, including subpackages

    https://stackoverflow.com/questions/3365740/how-to-import-all-submodules

    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for _, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        try:
            results[full_name] = importlib.import_module(full_name)
            if recursive and is_pkg:
                results.update(import_submodules(full_name))
        except ModuleNotFoundError:
            pass
    return results


class ScriptError(RuntimeError):
    def __init__(self, script_title: str, script_code: str) -> None:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        self.base_error = exc_obj
        self.line_number = traceback.extract_tb(exc_tb)[-1].lineno
        self.script_title = script_title
        msg = 'Error occurred while executing {0}.\n' \
              'Error: {1}: {2}.\n' \
              'Script:' \
              '\n{3}\n' \
              'At line: {4}\n'.format(script_title, exc_type.__name__, str(exc_obj), script_code, self.line_number)
        super(RuntimeError, self).__init__(msg)


def eval_script(script_title: str, script_code: str, eval_locals: Dict[str, Any]) -> Any:
    if '__' in script_code:
        raise SyntaxError(f'Script "{script_title}"" contains "__" string. This may be unsafe for python eval.')
    try:
        eval_locals_full = dict()
        eval_locals_full.update(settings.SCRIPTS_BASE_EVAL_LOCALS)
        if eval_locals:
            eval_locals_full.update(eval_locals)
        return eval(script_code, {}, eval_locals_full)
    except Exception:
        raise ScriptError(script_title, script_code)


def exec_script(script_title: str, script_code: str, eval_locals: Dict[str, Any]) -> Any:
    if '__' in script_code:
        raise SyntaxError('Script contains "__" string. This may be unsafe for python eval.')
    try:
        eval_locals_full = dict()
        eval_locals_full.update(settings.SCRIPTS_BASE_EVAL_LOCALS)
        if eval_locals:
            eval_locals_full.update(eval_locals)
        eval_globals = {}
        exec(script_code, eval_globals, eval_locals)
        return eval_locals.get('result')
    except:
        raise ScriptError(script_title, script_code)
