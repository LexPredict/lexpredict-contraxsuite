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


class CheckDocumentFieldFormulaRequest(object):
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
        'formula': 'str',
        'hide_until_python': 'str'
    }

    attribute_map = {
        'formula': 'formula',
        'hide_until_python': 'hide_until_python'
    }

    def __init__(self, formula=None, hide_until_python=None, local_vars_configuration=None):  # noqa: E501
        """CheckDocumentFieldFormulaRequest - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._formula = None
        self._hide_until_python = None
        self.discriminator = None

        if formula is not None:
            self.formula = formula
        if hide_until_python is not None:
            self.hide_until_python = hide_until_python

    @property
    def formula(self):
        """Gets the formula of this CheckDocumentFieldFormulaRequest.  # noqa: E501


        :return: The formula of this CheckDocumentFieldFormulaRequest.  # noqa: E501
        :rtype: str
        """
        return self._formula

    @formula.setter
    def formula(self, formula):
        """Sets the formula of this CheckDocumentFieldFormulaRequest.


        :param formula: The formula of this CheckDocumentFieldFormulaRequest.  # noqa: E501
        :type formula: str
        """

        self._formula = formula

    @property
    def hide_until_python(self):
        """Gets the hide_until_python of this CheckDocumentFieldFormulaRequest.  # noqa: E501


        :return: The hide_until_python of this CheckDocumentFieldFormulaRequest.  # noqa: E501
        :rtype: str
        """
        return self._hide_until_python

    @hide_until_python.setter
    def hide_until_python(self, hide_until_python):
        """Sets the hide_until_python of this CheckDocumentFieldFormulaRequest.


        :param hide_until_python: The hide_until_python of this CheckDocumentFieldFormulaRequest.  # noqa: E501
        :type hide_until_python: str
        """

        self._hide_until_python = hide_until_python

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
        if not isinstance(other, CheckDocumentFieldFormulaRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CheckDocumentFieldFormulaRequest):
            return True

        return self.to_dict() != other.to_dict()
