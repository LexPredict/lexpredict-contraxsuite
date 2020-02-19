"""
To-Do

* clean up OOP
* improve function names
* abstraction
* less hard-coding
* docstrings
"""

###############################################################################
# IMPORTS
###############################################################################
import os
from pathlib import Path
from typing import Iterable, Generator

###############################################################################
# CLASSES
###############################################################################
class RSTFileBuilder():

    def yield_directive_option_line(
        self,
        directive_options: Iterable
    ) -> Generator[str, None, None]:
        """
        """
        for option in directive_options:
            if isinstance(option, str):
                yield ''.join(['\t', ':', option, ':', '\n'])
            elif isinstance(option, tuple):
                yield ''.join(['\t', ':', option[0], ': ', option[1], '\n'])
            else:
                raise TypeError
    
    def format_autoelement(
        self,
        module: str,
        autoelement: str,
        directive_options: Iterable
    ) -> str:
        """
        """
        return ''.join(['.. ', autoelement, ':: apps.', module, '.models', '\n'])

    def format_header(
        self,
        module: str
    ) -> str:
        """
        """
        return ''.join([module, '\n', '=' * len(module), '\n\n'])

    
    def make_file(
        self,
        module: str,
        path: str,
        directive_options: Iterable
    ):
        """
        """
        file_name = ''.join([module, '.rst'])
        with open(os.path.join(path, file_name), 'w') as rst_file:
            rst_file.write(self.format_header(module))
            rst_file.write(self.format_autoelement(module, 'automodule', directive_options))
            for line in self.yield_directive_option_line(directive_options):
                rst_file.write(line)
            return rst_file


class Prepare:
    """
    """
    def __init__(
        self,
        path_modules: str = '../../contraxsuite_services/apps/',
        ignore: Iterable[str] = [
            'dump',
            'deployment',
            'logging',
            '__pycache__',
            'rawdb',
            'websocket',
            'employee',  # very outdated, not used
            'fields',    # very outdated, not used
            'lease'      # very outdated, not used
        ]):
        self.path_modules = path_modules
        self.ignore = ignore

    
    def get_modules(self):
        modules = next(os.walk(self.path_modules))[1]
        return [module for module in modules if module not in self.ignore]

def main():
    prep = Prepare()
    rst_file_builder = RSTFileBuilder()

    for module in prep.get_modules():
        rst_file_builder.make_file(module,'./source/api/contraxsuite_orm/', ['members'])


if __name__== "__main__":
    main()

###############################################################################
# OLD IMPLEMENTATION
###############################################################################

# path_apps = '../../contraxsuite_services/apps/'
# path_rst = '../../documentation/docs/source/api/contraxsuite_orm/'

# os.chdir(path_apps)
# modules = next(os.walk('.'))[1]
# os.chdir(path_rst)

# for module in modules:
#     if not module.startswith('_') or not module.endswith('_') or in ignored:
#         len_module_name = len(module)
#         file_name = ''.join([module, '.rst'])
#         directive_options = ['members']
#         with open(file_name, 'w') as f:
#             header = ''.join([module, '\n', '=' * len_module_name, '\n\n'])
#             f.write(header)
#             f.write(''.join(['.. automodule:: apps.', module, '.models', '\n']))
#             for line in directive_option_formatter(directive_options):
#                 f.write(line)
            
###############################################################################
# VERY OLD IMPLEMENTATION
###############################################################################

# import os
# import sys
# import django
# sys.path.append('../../contraxsuite_services')
# os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
# django.setup()
# from django.apps import apps
# models = apps.get_models()
# for model in models:
#     print(str(model))
#     print(model.__name__)
    # if str(model).startswith('apps'):
        # print(model)

        
    