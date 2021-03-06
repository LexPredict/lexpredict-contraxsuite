# coding: utf-8

"""

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from openapi_client.configuration import Configuration


class ProjectClustering(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'pk': 'int',
        'document_clusters': 'list[ProjectClusteringDocumentClusters]',
        'metadata': 'object',
        'created_date': 'datetime',
        'status': 'str',
        'reason': 'str',
        'project_clusters_documents_count': 'int'
    }

    attribute_map = {
        'pk': 'pk',
        'document_clusters': 'document_clusters',
        'metadata': 'metadata',
        'created_date': 'created_date',
        'status': 'status',
        'reason': 'reason',
        'project_clusters_documents_count': 'project_clusters_documents_count'
    }

    def __init__(self, pk=None, document_clusters=None, metadata=None, created_date=None, status=None, reason=None, project_clusters_documents_count=None, local_vars_configuration=None):  # noqa: E501
        """ProjectClustering - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._pk = None
        self._document_clusters = None
        self._metadata = None
        self._created_date = None
        self._status = None
        self._reason = None
        self._project_clusters_documents_count = None
        self.discriminator = None

        if pk is not None:
            self.pk = pk
        if document_clusters is not None:
            self.document_clusters = document_clusters
        self.metadata = metadata
        if created_date is not None:
            self.created_date = created_date
        if status is not None:
            self.status = status
        self.reason = reason
        self.project_clusters_documents_count = project_clusters_documents_count

    @property
    def pk(self):
        """Gets the pk of this ProjectClustering.  # noqa: E501


        :return: The pk of this ProjectClustering.  # noqa: E501
        :rtype: int
        """
        return self._pk

    @pk.setter
    def pk(self, pk):
        """Sets the pk of this ProjectClustering.


        :param pk: The pk of this ProjectClustering.  # noqa: E501
        :type pk: int
        """

        self._pk = pk

    @property
    def document_clusters(self):
        """Gets the document_clusters of this ProjectClustering.  # noqa: E501


        :return: The document_clusters of this ProjectClustering.  # noqa: E501
        :rtype: list[ProjectClusteringDocumentClusters]
        """
        return self._document_clusters

    @document_clusters.setter
    def document_clusters(self, document_clusters):
        """Sets the document_clusters of this ProjectClustering.


        :param document_clusters: The document_clusters of this ProjectClustering.  # noqa: E501
        :type document_clusters: list[ProjectClusteringDocumentClusters]
        """

        self._document_clusters = document_clusters

    @property
    def metadata(self):
        """Gets the metadata of this ProjectClustering.  # noqa: E501


        :return: The metadata of this ProjectClustering.  # noqa: E501
        :rtype: object
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """Sets the metadata of this ProjectClustering.


        :param metadata: The metadata of this ProjectClustering.  # noqa: E501
        :type metadata: object
        """

        self._metadata = metadata

    @property
    def created_date(self):
        """Gets the created_date of this ProjectClustering.  # noqa: E501


        :return: The created_date of this ProjectClustering.  # noqa: E501
        :rtype: datetime
        """
        return self._created_date

    @created_date.setter
    def created_date(self, created_date):
        """Sets the created_date of this ProjectClustering.


        :param created_date: The created_date of this ProjectClustering.  # noqa: E501
        :type created_date: datetime
        """

        self._created_date = created_date

    @property
    def status(self):
        """Gets the status of this ProjectClustering.  # noqa: E501


        :return: The status of this ProjectClustering.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this ProjectClustering.


        :param status: The status of this ProjectClustering.  # noqa: E501
        :type status: str
        """

        self._status = status

    @property
    def reason(self):
        """Gets the reason of this ProjectClustering.  # noqa: E501


        :return: The reason of this ProjectClustering.  # noqa: E501
        :rtype: str
        """
        return self._reason

    @reason.setter
    def reason(self, reason):
        """Sets the reason of this ProjectClustering.


        :param reason: The reason of this ProjectClustering.  # noqa: E501
        :type reason: str
        """

        self._reason = reason

    @property
    def project_clusters_documents_count(self):
        """Gets the project_clusters_documents_count of this ProjectClustering.  # noqa: E501


        :return: The project_clusters_documents_count of this ProjectClustering.  # noqa: E501
        :rtype: int
        """
        return self._project_clusters_documents_count

    @project_clusters_documents_count.setter
    def project_clusters_documents_count(self, project_clusters_documents_count):
        """Sets the project_clusters_documents_count of this ProjectClustering.


        :param project_clusters_documents_count: The project_clusters_documents_count of this ProjectClustering.  # noqa: E501
        :type project_clusters_documents_count: int
        """
        if self.local_vars_configuration.client_side_validation and project_clusters_documents_count is None:  # noqa: E501
            raise ValueError("Invalid value for `project_clusters_documents_count`, must not be `None`")  # noqa: E501

        self._project_clusters_documents_count = project_clusters_documents_count

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, ProjectClustering):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ProjectClustering):
            return True

        return self.to_dict() != other.to_dict()
