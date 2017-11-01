# -*- coding: utf-8 -*-

# Future imports
from __future__ import absolute_import

# Standard imports
import os

# Celery imports
from celery import Celery

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.3/LICENSE"
__version__ = "1.0.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# Set celery environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')  # pragma: no cover
app = Celery('apps')

# Auto-configure
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


# Bind debug task
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))  # pragma: no cover
