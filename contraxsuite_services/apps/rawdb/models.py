from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.deletion import CASCADE

from apps.document.models import DocumentType
from apps.project.models import Project
from apps.users.models import User
from apps.rawdb.constants import FT_COMMON_FILTER, FT_USER_DOC_GRID_CONFIG


class SavedFilter(models.Model):
    FILTER_TYPE_CHOICES = [
        (FT_COMMON_FILTER, 'Common Filter'),
        (FT_USER_DOC_GRID_CONFIG, 'User Document Grid Config')
    ]

    filter_type = models.CharField(max_length=50, blank=False, null=False, default=FT_COMMON_FILTER,
                                   choices=FILTER_TYPE_CHOICES)

    title = models.CharField(max_length=1024, blank=True, null=True)

    display_order = models.PositiveSmallIntegerField(default=0)

    project = models.ForeignKey(Project, null=True, blank=True, db_index=True, on_delete=CASCADE)

    document_type = models.ForeignKey(DocumentType, null=False, blank=False, db_index=True, on_delete=CASCADE)

    user = models.ForeignKey(User, blank=True, null=True, db_index=True, on_delete=CASCADE)

    # filter_sql = models.TextField(blank=True, null=True)

    columns = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

    column_filters = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)

    order_by = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder)
