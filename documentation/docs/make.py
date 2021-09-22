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
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# parsing
import yaml
import argparse
from pathlib import Path

# typing
from typing import Generator, Iterable
from types import ModuleType

# calling
import subprocess
from pkgutil import iter_modules
from importlib import import_module

# setup
import os
import sys
sys.path.append('../../contraxsuite_services')
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# license stripping
from settings import BASE_DIR
sys.path.append(os.path.abspath(f'{BASE_DIR}/documentation/'))
from docs.utils.strip_license import remove_licenses

# logging
import logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


# -----------------------------------------------------------------------------
# FUNCTIONS
# -----------------------------------------------------------------------------
def format_header(module: str) -> str:
    return f'{module}\n{"=" * len(module)}\n\n'


def format_automodule(module: str) -> str:
    return f'.. automodule:: {module}\n'


def yield_directive_option_line(
    directive_options: Iterable
) -> Generator[str, None, None]:
    for option in directive_options:
        if isinstance(option, str):
            yield f'\t:{option}:\n'
        elif isinstance(option, tuple):
            yield f'\t:{option[0]}: {option[1]}\n'
        else:
            raise TypeError


def get_package_module_paths(key, value) -> Generator[str, None, None]:
    for child in value:
        if isinstance(child, dict):
            for k, v in child.items():
                yield from get_package_module_paths(key=f'{key}/{k}', value=v)
        elif isinstance(child, str):
            yield f'{key}/{child}'


def get_submodule_names(module: ModuleType) -> Generator[str, None, None]:
    for submodule in iter_modules(module.__path__):
        if submodule.ispkg == True:
            subpackage = import_module(f'{module.__name__}.{submodule.name}')
            yield from get_submodule_names(subpackage)
        yield f'{module.__name__}.{submodule.name}'


def get_package_modules(key: str, value: list) -> Generator[str, None, None]:
    def _handle_str(_key, _value):
        if len(_value) == 0:
            try:
                module = import_module(_key)
            except ModuleNotFoundError:
                return
            yield from get_submodule_names(module)
        else:
            yield f'{_key}.{_value}'

    if isinstance(value, str):
        yield from _handle_str(key, value)
    elif isinstance(value, list):
        for child in value:
            if isinstance(child, dict):
                for k, v in child.items():
                    yield from get_package_modules(f'{key}.{k}', v)
            elif isinstance(child, str):
                yield from _handle_str(key, child)
            else:
                raise ValueError(f'{type(child)} is not supported.')
    elif value is None:
        try:
            module = import_module(key)
        except ModuleNotFoundError:
            return
        yield from get_submodule_names(module)
    else:
        raise ValueError(f'{type(value)} is not supported. key={key}, value={value}')


def write_rst_files(
    rst_configuration: os.PathLike =
        Path(BASE_DIR, 'documentation/docs/source/developer_documentation_schema.yaml'),
    output_directory: os.PathLike =
        Path(BASE_DIR, 'documentation/docs/source/api/contraxsuite_orm/'),
) -> Generator[Path, None, None]:
    output_directory: Path = Path(output_directory)
    output_directory.mkdir(exist_ok=True, parents=True)

    with open(rst_configuration) as yaml_file:
        y = yaml.load(yaml_file, Loader=yaml.SafeLoader)

    for app, modules in y.items():
        path_file = output_directory / f'{app}.rst'
        with open(path_file, 'w') as rst_file:
            rst_file.write(format_header(app))
            modules = get_package_modules(f'apps.{app}', modules)
            for module in modules:
                rst_file.write(format_automodule(module))
                for line in yield_directive_option_line(('members',)):
                    rst_file.write(f'{line}\n')
        yield path_file.absolute()


# -----------------------------------------------------------------------------
# USAGE
#   python make.py --generate_rst source/developer_documentation_schema.yaml --all
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        '--cpus',
        type=int,
        nargs='+',
        default=0,
        help='Number of CPUs to use for compilation.'
    )
    parser.add_argument(
        '--generate_rst',
        type=str,
        nargs='+',
        help='Rebuild ContraxSuite ORM .rst source files based on a YAML schema.'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Write all files (default: only write new and changed files)'
    )
    parser.add_argument(
        '--build',
        type=str,
        nargs='+',
        default='html',
        help='Builder to use (default: html)'
    )
    args = parser.parse_args()

    max_cpus: int = len(os.sched_getaffinity(0))
    if args.cpus == 0 or args.cpus > max_cpus:
        cpus = max_cpus
    else:
        cpus = args.cpus

    logging.info(f'Using {cpus} CPUs.')

    rst_configuration = args.generate_rst
    if rst_configuration:
        file_paths = write_rst_files(rst_configuration=rst_configuration[0])
        for file_path in file_paths:
            logging.info(f'Generated .rst: {file_path}')

    if args.all:
        subprocess.run(
            args='make clean'.split(' '),
            universal_newlines=True,
        )

    command: str = \
        f'sphinx-build' \
        f' -b {args.build}' \
        f' source build/html' \
        f' -j {cpus}' \
        f'{" -a" if args.all else ""}' \

    logging.info(f'Running Sphinx command: {command}')

    command_results: subprocess.CompletedProcess = \
        subprocess.run(
            args=command.split(' '),
            universal_newlines=True,
        )

    remove_licenses(
        html_directory=Path(
            BASE_DIR,
            'documentation/docs/build/html/api/contraxsuite_orm/',
        ),
        cpus=cpus
    )

    logging.info('Removed GNU licenses from generated HTML files.')
    logging.info('Done.')
