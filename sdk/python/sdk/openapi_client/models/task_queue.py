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


class TaskQueue(object):
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
        'description': 'str',
        'documents': 'list[int]',
        'documents_data': 'list[TaskQueueDocumentsData]',
        'completed_documents': 'list[int]',
        'completed_documents_data': 'list[TaskQueueDocumentsData]',
        'reviewers': 'list[int]',
        'reviewers_data': 'list[TaskQueueReviewersData]',
        'progress': 'str',
        'data': 'str'
    }

    attribute_map = {
        'pk': 'pk',
        'description': 'description',
        'documents': 'documents',
        'documents_data': 'documents_data',
        'completed_documents': 'completed_documents',
        'completed_documents_data': 'completed_documents_data',
        'reviewers': 'reviewers',
        'reviewers_data': 'reviewers_data',
        'progress': 'progress',
        'data': 'data'
    }

    def __init__(self, pk=None, description=None, documents=None, documents_data=None, completed_documents=None, completed_documents_data=None, reviewers=None, reviewers_data=None, progress=None, data=None, local_vars_configuration=None):  # noqa: E501
        """TaskQueue - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._pk = None
        self._description = None
        self._documents = None
        self._documents_data = None
        self._completed_documents = None
        self._completed_documents_data = None
        self._reviewers = None
        self._reviewers_data = None
        self._progress = None
        self._data = None
        self.discriminator = None

        if pk is not None:
            self.pk = pk
        self.description = description
        if documents is not None:
            self.documents = documents
        if documents_data is not None:
            self.documents_data = documents_data
        if completed_documents is not None:
            self.completed_documents = completed_documents
        if completed_documents_data is not None:
            self.completed_documents_data = completed_documents_data
        if reviewers is not None:
            self.reviewers = reviewers
        if reviewers_data is not None:
            self.reviewers_data = reviewers_data
        if progress is not None:
            self.progress = progress
        if data is not None:
            self.data = data

    @property
    def pk(self):
        """Gets the pk of this TaskQueue.  # noqa: E501


        :return: The pk of this TaskQueue.  # noqa: E501
        :rtype: int
        """
        return self._pk

    @pk.setter
    def pk(self, pk):
        """Sets the pk of this TaskQueue.


        :param pk: The pk of this TaskQueue.  # noqa: E501
        :type pk: int
        """

        self._pk = pk

    @property
    def description(self):
        """Gets the description of this TaskQueue.  # noqa: E501


        :return: The description of this TaskQueue.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this TaskQueue.


        :param description: The description of this TaskQueue.  # noqa: E501
        :type description: str
        """

        self._description = description

    @property
    def documents(self):
        """Gets the documents of this TaskQueue.  # noqa: E501


        :return: The documents of this TaskQueue.  # noqa: E501
        :rtype: list[int]
        """
        return self._documents

    @documents.setter
    def documents(self, documents):
        """Sets the documents of this TaskQueue.


        :param documents: The documents of this TaskQueue.  # noqa: E501
        :type documents: list[int]
        """

        self._documents = documents

    @property
    def documents_data(self):
        """Gets the documents_data of this TaskQueue.  # noqa: E501


        :return: The documents_data of this TaskQueue.  # noqa: E501
        :rtype: list[TaskQueueDocumentsData]
        """
        return self._documents_data

    @documents_data.setter
    def documents_data(self, documents_data):
        """Sets the documents_data of this TaskQueue.


        :param documents_data: The documents_data of this TaskQueue.  # noqa: E501
        :type documents_data: list[TaskQueueDocumentsData]
        """

        self._documents_data = documents_data

    @property
    def completed_documents(self):
        """Gets the completed_documents of this TaskQueue.  # noqa: E501


        :return: The completed_documents of this TaskQueue.  # noqa: E501
        :rtype: list[int]
        """
        return self._completed_documents

    @completed_documents.setter
    def completed_documents(self, completed_documents):
        """Sets the completed_documents of this TaskQueue.


        :param completed_documents: The completed_documents of this TaskQueue.  # noqa: E501
        :type completed_documents: list[int]
        """

        self._completed_documents = completed_documents

    @property
    def completed_documents_data(self):
        """Gets the completed_documents_data of this TaskQueue.  # noqa: E501


        :return: The completed_documents_data of this TaskQueue.  # noqa: E501
        :rtype: list[TaskQueueDocumentsData]
        """
        return self._completed_documents_data

    @completed_documents_data.setter
    def completed_documents_data(self, completed_documents_data):
        """Sets the completed_documents_data of this TaskQueue.


        :param completed_documents_data: The completed_documents_data of this TaskQueue.  # noqa: E501
        :type completed_documents_data: list[TaskQueueDocumentsData]
        """

        self._completed_documents_data = completed_documents_data

    @property
    def reviewers(self):
        """Gets the reviewers of this TaskQueue.  # noqa: E501


        :return: The reviewers of this TaskQueue.  # noqa: E501
        :rtype: list[int]
        """
        return self._reviewers

    @reviewers.setter
    def reviewers(self, reviewers):
        """Sets the reviewers of this TaskQueue.


        :param reviewers: The reviewers of this TaskQueue.  # noqa: E501
        :type reviewers: list[int]
        """

        self._reviewers = reviewers

    @property
    def reviewers_data(self):
        """Gets the reviewers_data of this TaskQueue.  # noqa: E501


        :return: The reviewers_data of this TaskQueue.  # noqa: E501
        :rtype: list[TaskQueueReviewersData]
        """
        return self._reviewers_data

    @reviewers_data.setter
    def reviewers_data(self, reviewers_data):
        """Sets the reviewers_data of this TaskQueue.


        :param reviewers_data: The reviewers_data of this TaskQueue.  # noqa: E501
        :type reviewers_data: list[TaskQueueReviewersData]
        """

        self._reviewers_data = reviewers_data

    @property
    def progress(self):
        """Gets the progress of this TaskQueue.  # noqa: E501


        :return: The progress of this TaskQueue.  # noqa: E501
        :rtype: str
        """
        return self._progress

    @progress.setter
    def progress(self, progress):
        """Sets the progress of this TaskQueue.


        :param progress: The progress of this TaskQueue.  # noqa: E501
        :type progress: str
        """

        self._progress = progress

    @property
    def data(self):
        """Gets the data of this TaskQueue.  # noqa: E501


        :return: The data of this TaskQueue.  # noqa: E501
        :rtype: str
        """
        return self._data

    @data.setter
    def data(self, data):
        """Sets the data of this TaskQueue.


        :param data: The data of this TaskQueue.  # noqa: E501
        :type data: str
        """

        self._data = data

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
        if not isinstance(other, TaskQueue):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, TaskQueue):
            return True

        return self.to_dict() != other.to_dict()
