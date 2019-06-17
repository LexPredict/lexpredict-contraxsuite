import importlib
import pkgutil
import sys
import traceback
from typing import Any, Dict

from django.conf import settings


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
        raise SyntaxError('Classifier init script contains "__" string. This may be unsafe for python eval.')
    try:
        eval_locals_full = dict()
        eval_locals_full.update(settings.SCRIPTS_BASE_EVAL_LOCALS)
        if eval_locals:
            eval_locals_full.update(eval_locals)
        return eval(script_code, {}, eval_locals_full)
    except:
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
