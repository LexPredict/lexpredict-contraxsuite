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
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# standard library imports
from pathlib import Path
from typing import List, Generator
from datetime import datetime

# django and ORM imports
from django.apps import apps
from settings import PROJECT_APPS
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help: str = 'Generate data model diagrams using the `graph_models` package.'

    def add_arguments(self, parser):
        """
        TODO: add arguments for additional flexibility
            - output file names
            - output file type (png, svg, etc.)
            - boolean: use date folder?
            - pass options to graph_models
            - specify which apps or combinations of apps
        """
        parser.add_argument(
            'destination_directory',
            nargs='?',
            type=str,
            help='An output directory for the `graph_models` files'
        )

        parser.add_argument(
            '--repository_permalinks',
            action='store_true',
            help="Attach HREFs to table titles with permalinks "
                 "to the codebase's source repository"
        )

    def handle(self, *args, **kwargs):
        """
        Raises:
            CommandError if the destination_directory argument
            is not a valid directory.
        """
        base_file_name: str = 'contraxsuite_data_model'
        path_destination_directory: Path = Path(kwargs['destination_directory'])
        if not path_destination_directory.is_dir():
            self.stdout.write(
                msg=self.style.NOTICE(
                    f'{path_destination_directory} is not a directory, '
                    f'but will be created.'
                )
            )

        project_apps: Generator[str, None, None] = \
            (app.split('.')[1] for app in PROJECT_APPS)
        project_apps: List[str] = [
            app for app in project_apps
            if next(apps.get_app_config(app).get_models(), None) is not None
        ]

        output_directory: Path = Path(
            path_destination_directory,
            datetime.today().strftime('%Y-%m-%d'),
        )

        try:
            output_directory.mkdir(parents=True, exist_ok=True)
            self.stdout.write(
                msg=self.style.SUCCESS(f'Created directory {output_directory}')
            )
        except:
            raise CommandError(
                f'Error encountered while creating directory {output_directory}'
            )

        theme: str = (
            'contraxsuite_with_repository_permalinks'
            if kwargs['repository_permalinks'] is True
            else 'contraxsuite'
        )

        # create an SVG with all Django apps
        output_file: Path = Path(output_directory, f'{base_file_name}.svg')
        call_command(
            'graph_models',
            '--group-models', *project_apps,
            '--output', output_file,
            '--arrow-shape', 'normal',
            '--theme', theme,
        )
        self.stdout.write(msg=self.style.SUCCESS(f'Created {output_file}'))

        # create an SVG for each Django app
        for app in project_apps:
            output_file: Path = Path(output_directory, f'{base_file_name}_{app}.svg')
            call_command(
                'graph_models',
                '--group-models', app,
                '--output', output_file,
                '--arrow-shape', 'normal',
                '--theme', theme,
            )
            self.stdout.write(self.style.SUCCESS(f'Created {output_file}'))
