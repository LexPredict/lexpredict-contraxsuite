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

from argparse import RawTextHelpFormatter
from django.core.management.commands.loaddata import *
from django.core.exceptions import ValidationError
from django.utils.encoding import force_text

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Command(Command):

    def create_parser(self, *args, **kwargs):
        parser = super().create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '-s', '--skip_if_exists', dest='skip_if_exists', action='store', default='one',
            help='Action - one of:\n'
                 'one - skip record if it exists\n'
                 'any - do not process if any record exists'
        )
        parser.add_argument(
            '-p', '--process_if_exists', dest='process_if_exists', action='store', default='replace',
            help='Action - one of:\n'
                 'replace - replace existing record (default for load_data behavior)\n'
                 'add_new - add object with new id if the same id exists, skip if non-unique'
        )

    def handle(self, *fixture_labels, **options):
        self.skip_if_exists = options['skip_if_exists']
        self.process_if_exists = options['process_if_exists']
        super().handle(*fixture_labels, **options)

    @functools.lru_cache(maxsize=None)
    def find_fixtures(self, fixture_label):
        try:
            res = super().find_fixtures(fixture_label)
        except CommandError as e:
            if 'No fixture named' in str(e):
                res = []
            else:
                raise e
        return res

    def load_label(self, fixture_label):
        """
        Loads fixtures files for a given label.
        BUT ONLY IF OBJECT WITH ID DOESN'T EXIST.
        Modified django.core.management.commands.loaddata.Command.load_label
        """
        show_progress = self.verbosity >= 3
        for fixture_file, fixture_dir, fixture_name in self.find_fixtures(fixture_label):
            _, ser_fmt, cmp_fmt = self.parse_name(os.path.basename(fixture_file))
            open_method, mode = self.compression_formats[cmp_fmt]
            fixture = open_method(fixture_file, mode)
            try:
                self.fixture_count += 1
                objects_in_fixture = 0
                loaded_objects_in_fixture = 0
                if self.verbosity >= 2:
                    self.stdout.write(
                        "Installing %s fixture '%s' from %s."
                        % (ser_fmt, fixture_name, humanize(fixture_dir))
                    )

                objects = serializers.deserialize(
                    ser_fmt, fixture, using=self.using, ignorenonexistent=self.ignore,
                )

                _initial = {}

                for obj in objects:

                    _model = obj.object._meta.model

                    if _initial.get(_model) is None:
                        _initial[_model] = _model.objects.exists()

                    if self.process_if_exists == 'add_new':
                        if _model.objects.filter(pk=obj.object.pk).exists():
                            obj.object.pk = None
                        try:
                            _ = obj.object.validate_unique()
                        except ValidationError:
                            continue

                    elif self.skip_if_exists == 'any':
                        if _initial.get(_model):
                            continue

                    elif self.skip_if_exists == 'one':
                        try:
                            _ = obj.object.validate_unique()
                        except ValidationError:
                            continue

                    objects_in_fixture += 1
                    if (obj.object._meta.app_config in self.excluded_apps or
                                type(obj.object) in self.excluded_models):
                        continue
                    if router.allow_migrate_model(self.using, obj.object.__class__):
                        loaded_objects_in_fixture += 1
                        self.models.add(obj.object.__class__)
                        try:
                            obj.save(using=self.using)
                            if show_progress:
                                self.stdout.write(
                                    '\rProcessed %i object(s).' % loaded_objects_in_fixture,
                                    ending=''
                                )
                        except (DatabaseError, IntegrityError) as e:
                            e.args = (
                            "Could not load %(app_label)s.%(object_name)s(pk=%(pk)s): %(error_msg)s" % {
                                'app_label': obj.object._meta.app_label,
                                'object_name': obj.object._meta.object_name,
                                'pk': obj.object.pk,
                                'error_msg': force_text(e)
                            },)
                            raise
                if objects and show_progress:
                    self.stdout.write('')  # add a newline after progress indicator
                self.loaded_object_count += loaded_objects_in_fixture
                self.fixture_object_count += objects_in_fixture
            except Exception as e:
                if not isinstance(e, CommandError):
                    e.args = ("Problem installing fixture '%s': %s" % (fixture_file, e),)
                raise
            finally:
                fixture.close()

            # Warn if the fixture we loaded contains 0 objects.
            if objects_in_fixture == 0:
                warnings.warn(
                    "No fixture data found for '%s'. (File format may be "
                    "invalid.)" % fixture_name,
                    RuntimeWarning
                )
