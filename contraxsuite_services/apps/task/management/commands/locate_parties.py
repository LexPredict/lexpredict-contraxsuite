from django.core.management import BaseCommand

from apps.task.tasks import call_task


class Command(BaseCommand):
    help = "Locate parties in text units"

    def add_arguments(self, parser):

        parser.add_argument('--delete',
                            action='store_true',
                            dest='delete',
                            default=False,
                            help='Delete values first')

    def handle(self, *args, **options):
        call_task('Locate Parties', **options)
