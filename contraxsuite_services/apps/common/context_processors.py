# -*- coding: utf-8 -*-

# Django imports
from django.conf import settings

# Project imports
from apps.document.models import Document
from apps.project.models import Project, TaskQueue
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.1/LICENSE"
__version__ = "1.0.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def common(request):
    return {'settings': settings,
            'documents_count': Document.objects.count(),
            'projects_count': Project.objects.count(),
            'task_queues_count': TaskQueue.objects.count(),
            'reviewers_count': User.objects.filter(role='reviewer').count()}
