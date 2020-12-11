"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""
# -*- coding: utf-8 -*-

from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

# Django imports
from django.conf.urls import url

# Project imports
from apps.similarity.views import SimilarityView, PartySimilarityView, SimilarityByFeaturesView
from apps.common.schemas import ObjectResponseSchema, json_ct

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class SimilaritySchema(ObjectResponseSchema):
    object_response_for_methods = ['GET', 'POST']

    class SimilarityPOSTObjectResponseSerializer(serializers.Serializer):
        detail = serializers.CharField()
        confirm = serializers.BooleanField(required=False)

    def get_responses(self, path, method):
        res = super().get_responses(path, method)
        if method == 'GET':
            return res
        return {
            '200': {
                'content': {json_ct: {'schema': {'$ref': 'SimilarityPOSTObjectResponse'}}}}}

    def get_components(self, path, method):
        return {'SimilarityPOSTObjectResponse': self.map_serializer(self.SimilarityPOSTObjectResponseSerializer())}


class RunTaskPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.has_perm('task.add_task')


class SimilarityAPIView(APIView, SimilarityView):
    """
    "Similarity" admin task\n
    POST params:
        - search_similar_documents: bool
        - search_similar_text_units: bool
        - similarity_threshold: int
        - use_idf: bool
        - delete: bool
        - project: bool
    """
    http_method_names = ["get", "post"]
    schema = SimilaritySchema()
    permission_classes = [RunTaskPermission]


class SimilarityByFeaturesAPIView(APIView, SimilarityByFeaturesView):
    """
    "Similarity" admin task\n
    POST params:
        - search_similar_documents: bool
        - search_similar_text_units: bool
        - similarity_threshold: int
        - use_idf: bool
        - delete: bool
        - project: int
        - feature_source: list - list[date, definition, duration, court,
          currency_name, currency_value, term, party, geoentity]
        - unit_type: str sentence|paragraph
        - distance_type: str - see scipy.spatial.distance._METRICS
    """
    http_method_names = ["get", "post"]
    schema = SimilaritySchema()
    permission_classes = [RunTaskPermission]


class PartySimilarityAPIView(APIView, PartySimilarityView):
    """
    "Party Similarity" admin task\n
    POST params:
        - case_sensitive: bool
        - similarity_type: str[]
        - similarity_threshold: int
        - delete: bool
    """
    http_method_names = ["get", "post"]
    schema = SimilaritySchema()
    permission_classes = [RunTaskPermission]


urlpatterns = [
    url(r'^similarity/$', SimilarityAPIView.as_view(),
        name='similarity'),
    url(r'^similarity-by-features/$', SimilarityByFeaturesAPIView.as_view(),
        name='similarity-by-features'),
    url(r'^party-similarity/$', PartySimilarityAPIView.as_view(),
        name='party-similarity'),
]
