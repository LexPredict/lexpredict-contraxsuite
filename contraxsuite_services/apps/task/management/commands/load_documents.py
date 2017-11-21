from django.core.management import BaseCommand

from apps.task.tasks import call_task

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.3/LICENSE"
__version__ = "1.0.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

class Command(BaseCommand):
    help = "Load Document, i.e. create Document and TextUnit objects" \
           "from uploaded document files in a given directory"

    def add_arguments(self, parser):
        parser.add_argument('source_path')

        parser.add_argument('--delete',
                            action='store_true',
                            dest='delete',
                            default=False,
                            help='Delete values first')

        parser.add_argument('--document_type',
                            default='agreement',
                            help='Document type')

        parser.add_argument('--source_type',
                            default='SEC data',
                            help='Source type')

    def handle(self, *args, **options):
        call_task('Load Documents', **options)
