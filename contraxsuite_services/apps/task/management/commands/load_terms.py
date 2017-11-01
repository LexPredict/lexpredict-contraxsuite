from django.core.management import BaseCommand

from apps.task.tasks import call_task

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.3/LICENSE"
__version__ = "1.0.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Command(BaseCommand):
    help = "Load Legal Entities from a dictionary sample"

    def add_arguments(self, parser):
        parser.add_argument('dictionary_path')

        parser.add_argument('--delete',
                            action='store_true',
                            dest='delete',
                            default=False,
                            help='Delete values first')

    def handle(self, *args, **options):
        call_task('Load Terms', **options)
