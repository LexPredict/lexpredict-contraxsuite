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


class PartyUsage(object):
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
        'party__name': 'str',
        'party__type_abbr': 'str',
        'party__pk': 'str',
        'count': 'int',
        'pk': 'int',
        'text_unit__pk': 'str',
        'text_unit__unit_type': 'str',
        'text_unit__location_start': 'str',
        'text_unit__location_end': 'str',
        'text_unit__document__pk': 'str',
        'text_unit__document__name': 'str',
        'text_unit__document__description': 'str',
        'text_unit__document__document_type': 'str'
    }

    attribute_map = {
        'party__name': 'party__name',
        'party__type_abbr': 'party__type_abbr',
        'party__pk': 'party__pk',
        'count': 'count',
        'pk': 'pk',
        'text_unit__pk': 'text_unit__pk',
        'text_unit__unit_type': 'text_unit__unit_type',
        'text_unit__location_start': 'text_unit__location_start',
        'text_unit__location_end': 'text_unit__location_end',
        'text_unit__document__pk': 'text_unit__document__pk',
        'text_unit__document__name': 'text_unit__document__name',
        'text_unit__document__description': 'text_unit__document__description',
        'text_unit__document__document_type': 'text_unit__document__document_type'
    }

    def __init__(self, party__name=None, party__type_abbr=None, party__pk=None, count=None, pk=None, text_unit__pk=None, text_unit__unit_type=None, text_unit__location_start=None, text_unit__location_end=None, text_unit__document__pk=None, text_unit__document__name=None, text_unit__document__description=None, text_unit__document__document_type=None, local_vars_configuration=None):  # noqa: E501
        """PartyUsage - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._party__name = None
        self._party__type_abbr = None
        self._party__pk = None
        self._count = None
        self._pk = None
        self._text_unit__pk = None
        self._text_unit__unit_type = None
        self._text_unit__location_start = None
        self._text_unit__location_end = None
        self._text_unit__document__pk = None
        self._text_unit__document__name = None
        self._text_unit__document__description = None
        self._text_unit__document__document_type = None
        self.discriminator = None

        if party__name is not None:
            self.party__name = party__name
        if party__type_abbr is not None:
            self.party__type_abbr = party__type_abbr
        if party__pk is not None:
            self.party__pk = party__pk
        if count is not None:
            self.count = count
        if pk is not None:
            self.pk = pk
        if text_unit__pk is not None:
            self.text_unit__pk = text_unit__pk
        if text_unit__unit_type is not None:
            self.text_unit__unit_type = text_unit__unit_type
        if text_unit__location_start is not None:
            self.text_unit__location_start = text_unit__location_start
        if text_unit__location_end is not None:
            self.text_unit__location_end = text_unit__location_end
        if text_unit__document__pk is not None:
            self.text_unit__document__pk = text_unit__document__pk
        if text_unit__document__name is not None:
            self.text_unit__document__name = text_unit__document__name
        if text_unit__document__description is not None:
            self.text_unit__document__description = text_unit__document__description
        if text_unit__document__document_type is not None:
            self.text_unit__document__document_type = text_unit__document__document_type

    @property
    def party__name(self):
        """Gets the party__name of this PartyUsage.  # noqa: E501


        :return: The party__name of this PartyUsage.  # noqa: E501
        :rtype: str
        """
        return self._party__name

    @party__name.setter
    def party__name(self, party__name):
        """Sets the party__name of this PartyUsage.


        :param party__name: The party__name of this PartyUsage.  # noqa: E501
        :type party__name: str
        """

        self._party__name = party__name

    @property
    def party__type_abbr(self):
        """Gets the party__type_abbr of this PartyUsage.  # noqa: E501


        :return: The party__type_abbr of this PartyUsage.  # noqa: E501
        :rtype: str
        """
        return self._party__type_abbr

    @party__type_abbr.setter
    def party__type_abbr(self, party__type_abbr):
        """Sets the party__type_abbr of this PartyUsage.


        :param party__type_abbr: The party__type_abbr of this PartyUsage.  # noqa: E501
        :type party__type_abbr: str
        """

        self._party__type_abbr = party__type_abbr

    @property
    def party__pk(self):
        """Gets the party__pk of this PartyUsage.  # noqa: E501


        :return: The party__pk of this PartyUsage.  # noqa: E501
        :rtype: str
        """
        return self._party__pk

    @party__pk.setter
    def party__pk(self, party__pk):
        """Sets the party__pk of this PartyUsage.


        :param party__pk: The party__pk of this PartyUsage.  # noqa: E501
        :type party__pk: str
        """

        self._party__pk = party__pk

    @property
    def count(self):
        """Gets the count of this PartyUsage.  # noqa: E501


        :return: The count of this PartyUsage.  # noqa: E501
        :rtype: int
        """
        return self._count

    @count.setter
    def count(self, count):
        """Sets the count of this PartyUsage.


        :param count: The count of this PartyUsage.  # noqa: E501
        :type count: int
        """
        if (self.local_vars_configuration.client_side_validation and
                count is not None and count > 2147483647):  # noqa: E501
            raise ValueError("Invalid value for `count`, must be a value less than or equal to `2147483647`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                count is not None and count < -2147483648):  # noqa: E501
            raise ValueError("Invalid value for `count`, must be a value greater than or equal to `-2147483648`")  # noqa: E501

        self._count = count

    @property
    def pk(self):
        """Gets the pk of this PartyUsage.  # noqa: E501


        :return: The pk of this PartyUsage.  # noqa: E501
        :rtype: int
        """
        return self._pk

    @pk.setter
    def pk(self, pk):
        """Sets the pk of this PartyUsage.


        :param pk: The pk of this PartyUsage.  # noqa: E501
        :type pk: int
        """

        self._pk = pk

    @property
    def text_unit__pk(self):
        """Gets the text_unit__pk of this PartyUsage.  # noqa: E501


        :return: The text_unit__pk of this PartyUsage.  # noqa: E501
        :rtype: str
        """
        return self._text_unit__pk

    @text_unit__pk.setter
    def text_unit__pk(self, text_unit__pk):
        """Sets the text_unit__pk of this PartyUsage.


        :param text_unit__pk: The text_unit__pk of this PartyUsage.  # noqa: E501
        :type text_unit__pk: str
        """

        self._text_unit__pk = text_unit__pk

    @property
    def text_unit__unit_type(self):
        """Gets the text_unit__unit_type of this PartyUsage.  # noqa: E501


        :return: The text_unit__unit_type of this PartyUsage.  # noqa: E501
        :rtype: str
        """
        return self._text_unit__unit_type

    @text_unit__unit_type.setter
    def text_unit__unit_type(self, text_unit__unit_type):
        """Sets the text_unit__unit_type of this PartyUsage.


        :param text_unit__unit_type: The text_unit__unit_type of this PartyUsage.  # noqa: E501
        :type text_unit__unit_type: str
        """

        self._text_unit__unit_type = text_unit__unit_type

    @property
    def text_unit__location_start(self):
        """Gets the text_unit__location_start of this PartyUsage.  # noqa: E501


        :return: The text_unit__location_start of this PartyUsage.  # noqa: E501
        :rtype: str
        """
        return self._text_unit__location_start

    @text_unit__location_start.setter
    def text_unit__location_start(self, text_unit__location_start):
        """Sets the text_unit__location_start of this PartyUsage.


        :param text_unit__location_start: The text_unit__location_start of this PartyUsage.  # noqa: E501
        :type text_unit__location_start: str
        """

        self._text_unit__location_start = text_unit__location_start

    @property
    def text_unit__location_end(self):
        """Gets the text_unit__location_end of this PartyUsage.  # noqa: E501


        :return: The text_unit__location_end of this PartyUsage.  # noqa: E501
        :rtype: str
        """
        return self._text_unit__location_end

    @text_unit__location_end.setter
    def text_unit__location_end(self, text_unit__location_end):
        """Sets the text_unit__location_end of this PartyUsage.


        :param text_unit__location_end: The text_unit__location_end of this PartyUsage.  # noqa: E501
        :type text_unit__location_end: str
        """

        self._text_unit__location_end = text_unit__location_end

    @property
    def text_unit__document__pk(self):
        """Gets the text_unit__document__pk of this PartyUsage.  # noqa: E501


        :return: The text_unit__document__pk of this PartyUsage.  # noqa: E501
        :rtype: str
        """
        return self._text_unit__document__pk

    @text_unit__document__pk.setter
    def text_unit__document__pk(self, text_unit__document__pk):
        """Sets the text_unit__document__pk of this PartyUsage.


        :param text_unit__document__pk: The text_unit__document__pk of this PartyUsage.  # noqa: E501
        :type text_unit__document__pk: str
        """

        self._text_unit__document__pk = text_unit__document__pk

    @property
    def text_unit__document__name(self):
        """Gets the text_unit__document__name of this PartyUsage.  # noqa: E501


        :return: The text_unit__document__name of this PartyUsage.  # noqa: E501
        :rtype: str
        """
        return self._text_unit__document__name

    @text_unit__document__name.setter
    def text_unit__document__name(self, text_unit__document__name):
        """Sets the text_unit__document__name of this PartyUsage.


        :param text_unit__document__name: The text_unit__document__name of this PartyUsage.  # noqa: E501
        :type text_unit__document__name: str
        """

        self._text_unit__document__name = text_unit__document__name

    @property
    def text_unit__document__description(self):
        """Gets the text_unit__document__description of this PartyUsage.  # noqa: E501


        :return: The text_unit__document__description of this PartyUsage.  # noqa: E501
        :rtype: str
        """
        return self._text_unit__document__description

    @text_unit__document__description.setter
    def text_unit__document__description(self, text_unit__document__description):
        """Sets the text_unit__document__description of this PartyUsage.


        :param text_unit__document__description: The text_unit__document__description of this PartyUsage.  # noqa: E501
        :type text_unit__document__description: str
        """

        self._text_unit__document__description = text_unit__document__description

    @property
    def text_unit__document__document_type(self):
        """Gets the text_unit__document__document_type of this PartyUsage.  # noqa: E501


        :return: The text_unit__document__document_type of this PartyUsage.  # noqa: E501
        :rtype: str
        """
        return self._text_unit__document__document_type

    @text_unit__document__document_type.setter
    def text_unit__document__document_type(self, text_unit__document__document_type):
        """Sets the text_unit__document__document_type of this PartyUsage.


        :param text_unit__document__document_type: The text_unit__document__document_type of this PartyUsage.  # noqa: E501
        :type text_unit__document__document_type: str
        """

        self._text_unit__document__document_type = text_unit__document__document_type

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
        if not isinstance(other, PartyUsage):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, PartyUsage):
            return True

        return self.to_dict() != other.to_dict()
