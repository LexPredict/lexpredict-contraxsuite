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


class DocumentsForUserResponseData(object):
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
        'name': 'str',
        'document_type': 'str',
        'project': 'int',
        'status_name': 'str'
    }

    attribute_map = {
        'pk': 'pk',
        'name': 'name',
        'document_type': 'document_type',
        'project': 'project',
        'status_name': 'status_name'
    }

    def __init__(self, pk=None, name=None, document_type=None, project=None, status_name=None, local_vars_configuration=None):  # noqa: E501
        """DocumentsForUserResponseData - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._pk = None
        self._name = None
        self._document_type = None
        self._project = None
        self._status_name = None
        self.discriminator = None

        if pk is not None:
            self.pk = pk
        self.name = name
        self.document_type = document_type
        self.project = project
        self.status_name = status_name

    @property
    def pk(self):
        """Gets the pk of this DocumentsForUserResponseData.  # noqa: E501


        :return: The pk of this DocumentsForUserResponseData.  # noqa: E501
        :rtype: int
        """
        return self._pk

    @pk.setter
    def pk(self, pk):
        """Sets the pk of this DocumentsForUserResponseData.


        :param pk: The pk of this DocumentsForUserResponseData.  # noqa: E501
        :type pk: int
        """

        self._pk = pk

    @property
    def name(self):
        """Gets the name of this DocumentsForUserResponseData.  # noqa: E501


        :return: The name of this DocumentsForUserResponseData.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this DocumentsForUserResponseData.


        :param name: The name of this DocumentsForUserResponseData.  # noqa: E501
        :type name: str
        """
        if (self.local_vars_configuration.client_side_validation and
                name is not None and len(name) > 1024):
            raise ValueError("Invalid value for `name`, length must be less than or equal to `1024`")  # noqa: E501

        self._name = name

    @property
    def document_type(self):
        """Gets the document_type of this DocumentsForUserResponseData.  # noqa: E501


        :return: The document_type of this DocumentsForUserResponseData.  # noqa: E501
        :rtype: str
        """
        return self._document_type

    @document_type.setter
    def document_type(self, document_type):
        """Sets the document_type of this DocumentsForUserResponseData.


        :param document_type: The document_type of this DocumentsForUserResponseData.  # noqa: E501
        :type document_type: str
        """

        self._document_type = document_type

    @property
    def project(self):
        """Gets the project of this DocumentsForUserResponseData.  # noqa: E501


        :return: The project of this DocumentsForUserResponseData.  # noqa: E501
        :rtype: int
        """
        return self._project

    @project.setter
    def project(self, project):
        """Sets the project of this DocumentsForUserResponseData.


        :param project: The project of this DocumentsForUserResponseData.  # noqa: E501
        :type project: int
        """

        self._project = project

    @property
    def status_name(self):
        """Gets the status_name of this DocumentsForUserResponseData.  # noqa: E501


        :return: The status_name of this DocumentsForUserResponseData.  # noqa: E501
        :rtype: str
        """
        return self._status_name

    @status_name.setter
    def status_name(self, status_name):
        """Sets the status_name of this DocumentsForUserResponseData.


        :param status_name: The status_name of this DocumentsForUserResponseData.  # noqa: E501
        :type status_name: str
        """
        if self.local_vars_configuration.client_side_validation and status_name is None:  # noqa: E501
            raise ValueError("Invalid value for `status_name`, must not be `None`")  # noqa: E501

        self._status_name = status_name

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
        if not isinstance(other, DocumentsForUserResponseData):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DocumentsForUserResponseData):
            return True

        return self.to_dict() != other.to_dict()
