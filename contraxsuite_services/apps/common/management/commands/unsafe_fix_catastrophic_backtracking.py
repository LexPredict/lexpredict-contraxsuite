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

import inspect
from argparse import RawTextHelpFormatter

from django.core.management.base import BaseCommand

from apps.document.models import DocumentFieldDetector

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def fix_regexp(r: str):
    return r.replace('.*', '.{0,1000}').replace('.+', '.{1,1000}').replace('{0,16000}', '{0,1000}') if r else r


class Command(BaseCommand):
    help = "This command will try to fix catastrophic backtracking in field detector regexps by doing the " \
           "following transformation:\n\n{0}\n\n" \
           "WARNING! This is unsafe! It can break complicated regexps. Please check them manually in Django Admin " \
           "after executing this command!".format(inspect.getsource(fix_regexp))
    requires_system_checks = False

    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            help='Do not ask confirmation',
        )
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def handle(self, *args, **options):
        i = 0
        print(self.help)
        if not options['force'] and input('Are you sure you want to continue? (y/n)') != 'y':
            return

        for fd in DocumentFieldDetector.objects.all():
            include_regexps = fix_regexp(fd.include_regexps)
            exclude_regexps = fix_regexp(fd.exclude_regexps)
            if include_regexps != fd.include_regexps or exclude_regexps != fd.exclude_regexps:
                msg = 'Field detector {0}:\n'.format(fd)
                if include_regexps != fd.include_regexps:
                    fd.include_regexps = include_regexps
                    msg += 'Replacing include regexps with:\n{0}\n'.format(include_regexps)
                if exclude_regexps != fd.exclude_regexps:
                    fd.exclude_regexps = exclude_regexps
                    msg += 'Replacing exclude regexps with:\n{0}\n'.format(exclude_regexps)
                fd.save()
                print(msg)
                i += 1
        print('Changed {0} field detectors'.format(i))
