# -*- coding: utf-8 -*-

# EL imports
from haystack import indexes

# Project imports
from apps.document.models import TextUnit

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.3/LICENSE"
__version__ = "1.0.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TextUnitIndex(indexes.SearchIndex, indexes.Indexable):
    """TextUnitIndex

    ElasticSearch text unit index object.
    """

    # EL primary key
    _pk = indexes.IntegerField(model_attr='pk')

    # Text
    text = indexes.CharField(document=True, use_template=True)

    # Document
    document = indexes.CharField(model_attr='document__pk')

    # Text unit type
    unit_type = indexes.CharField(model_attr='unit_type')

    # Language
    language = indexes.CharField(model_attr='language')

    # Text hash for identical matching/de-dupe
    text_hash = indexes.CharField(model_attr='text_hash')

    def get_model(self):
        return TextUnit

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
