from django.core.management import BaseCommand

from apps.task.tasks import call_task


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
