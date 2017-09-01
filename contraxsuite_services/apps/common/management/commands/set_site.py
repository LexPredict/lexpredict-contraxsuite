# -*- coding: utf-8 -*-

# Django imports
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management import BaseCommand

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.1/LICENSE"
__version__ = "1.0.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class Command(BaseCommand):
    help = "Set site's domain and name"

    def handle(self, *args, **options):
        Site.objects.update_or_create(
            id=settings.SITE_ID,
            defaults={
                'domain': settings.HOST_NAME,
                'name': settings.SITE_NAME
            }
        )
