"""
To-Do

* clean up OOP
* improve function names
* abstraction
* less hard-coding
* docstrings

NOTE:
    This is deprecated and will be removed soon.
"""

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------
import os
from typing import Iterable, Generator, TextIO


# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------
class RSTFileBuilder:

    @staticmethod
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

    @staticmethod
    def format_autoelement(
        autoelement: str,
        app: str,
        module: str,
    ) -> str:
        return f'.. {autoelement}:: apps.{app}.{module}\n'

    @staticmethod
    def format_header(module: str) -> str:
        return f'{module}\n{"=" * len(module)}\n\n'

    def make_file(
        self,
        app: str,
        path: str,
        directive_options: Iterable
    ) -> TextIO:
        file_name = f'{app}.rst'
        with open(os.path.join(path, file_name), 'w') as rst_file:
            rst_file.write(self.format_header(app))
            for module in ('models',):
                rst_file.write(self.format_autoelement('automodule', app, module))
                for line in self.yield_directive_option_line(directive_options):
                    rst_file.write(line)
            return rst_file


class Prepare:
    """
    """
    def __init__(
        self,
        path_modules: str = '../../contraxsuite_services/apps/',
        ignore: Iterable[str] = (
            'dump',
            # 'deployment',
            'logging',
            '__pycache__',
            # 'rawdb',
            'websocket',
            'employee',  # very outdated, not used
            'fields',    # very outdated, not used
            'lease'      # very outdated, not used
        ),
    ) -> None:
        self.path_modules: str = path_modules
        self.ignore: Iterable[str] = ignore

    def get_modules(self) -> Generator[str, None, None]:
        modules = next(os.walk(self.path_modules))[1]
        return (module for module in modules if module not in self.ignore)


def main():
    prep = Prepare()
    rst_file_builder = RSTFileBuilder()

    for module in prep.get_modules():
        rst_file_builder.make_file(
            app=module,
            path='./source/api/contraxsuite_orm/',
            directive_options=['members']
        )


if __name__ == "__main__":
    main()
