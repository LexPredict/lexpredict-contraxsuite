from django.core.management import BaseCommand

from allauth.account.models import EmailAddress
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.3/LICENSE"
__version__ = "1.0.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Command(BaseCommand):
    help = "Create superuser --username USER --password PWD --email it@email.com"

    def add_arguments(self, parser):
        parser.add_argument('--username',
                            help='Username')

        parser.add_argument('--password',
                            help='Password')

        parser.add_argument('--email',
                            help='Email')

    def handle(self, *args, **options):
        user, created = User.objects.update_or_create(
            username=options['username'],
            is_superuser=True,
            is_staff=True,
            defaults=dict(
                email=options['email'],
                role='technical_admin',
                is_active=True))
        user.set_password(options['password'])
        user.save()

        if created:
            EmailAddress.objects.create(
                user=user,
                email=user.email,
                verified=True,
                primary=True)
