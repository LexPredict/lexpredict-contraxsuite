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


class ProjectCreate(object):
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
        'description': 'str',
        'type': 'str',
        'send_email_notification': 'bool'
    }

    attribute_map = {
        'pk': 'pk',
        'name': 'name',
        'description': 'description',
        'type': 'type',
        'send_email_notification': 'send_email_notification'
    }

    def __init__(self, pk=None, name=None, description=None, type=None, send_email_notification=None, local_vars_configuration=None):  # noqa: E501
        """ProjectCreate - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._pk = None
        self._name = None
        self._description = None
        self._type = None
        self._send_email_notification = None
        self.discriminator = None

        if pk is not None:
            self.pk = pk
        self.name = name
        self.description = description
        self.type = type
        if send_email_notification is not None:
            self.send_email_notification = send_email_notification

    @property
    def pk(self):
        """Gets the pk of this ProjectCreate.  # noqa: E501


        :return: The pk of this ProjectCreate.  # noqa: E501
        :rtype: int
        """
        return self._pk

    @pk.setter
    def pk(self, pk):
        """Sets the pk of this ProjectCreate.


        :param pk: The pk of this ProjectCreate.  # noqa: E501
        :type pk: int
        """

        self._pk = pk

    @property
    def name(self):
        """Gets the name of this ProjectCreate.  # noqa: E501


        :return: The name of this ProjectCreate.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this ProjectCreate.


        :param name: The name of this ProjectCreate.  # noqa: E501
        :type name: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                name is not None and len(name) > 100):
            raise ValueError("Invalid value for `name`, length must be less than or equal to `100`")  # noqa: E501

        self._name = name

    @property
    def description(self):
        """Gets the description of this ProjectCreate.  # noqa: E501


        :return: The description of this ProjectCreate.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this ProjectCreate.


        :param description: The description of this ProjectCreate.  # noqa: E501
        :type description: str
        """

        self._description = description

    @property
    def type(self):
        """Gets the type of this ProjectCreate.  # noqa: E501


        :return: The type of this ProjectCreate.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this ProjectCreate.


        :param type: The type of this ProjectCreate.  # noqa: E501
        :type type: str
        """

        self._type = type

    @property
    def send_email_notification(self):
        """Gets the send_email_notification of this ProjectCreate.  # noqa: E501


        :return: The send_email_notification of this ProjectCreate.  # noqa: E501
        :rtype: bool
        """
        return self._send_email_notification

    @send_email_notification.setter
    def send_email_notification(self, send_email_notification):
        """Sets the send_email_notification of this ProjectCreate.


        :param send_email_notification: The send_email_notification of this ProjectCreate.  # noqa: E501
        :type send_email_notification: bool
        """

        self._send_email_notification = send_email_notification

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
        if not isinstance(other, ProjectCreate):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ProjectCreate):
            return True

        return self.to_dict() != other.to_dict()
