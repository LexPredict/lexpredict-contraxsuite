# -*- coding: utf-8 -*-
__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.3/LICENSE"
__version__ = "1.0.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# Django imports
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings


class CustomEmailBackend(EmailBackend):

    def send_messages(self, email_messages):
        for message in email_messages:
            if 'Reply-To' not in message.extra_headers:
                message.extra_headers['Reply-To'] = settings.DEFAULT_REPLY_TO
        return super(CustomEmailBackend, self).send_messages(email_messages)
