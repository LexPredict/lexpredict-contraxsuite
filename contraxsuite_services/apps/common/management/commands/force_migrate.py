# -*- coding: utf-8 -*-
# Imports
from django.core.management import call_command, BaseCommand

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0/LICENSE.pdf"
__version__ = "1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@lexpredict.com"


class Command(BaseCommand):
    help = "Run migration without system checks"
    requires_system_checks = False

    def handle(self, *args, **options):
        call_command('migrate')
