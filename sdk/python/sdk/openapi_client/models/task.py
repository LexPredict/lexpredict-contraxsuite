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


class Task(object):
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
        'pk': 'str',
        'name': 'str',
        'date_start': 'datetime',
        'date_work_start': 'datetime',
        'user__username': 'str',
        'date_done': 'datetime',
        'duration': 'str',
        'progress': 'int',
        'status': 'str',
        'has_error': 'str',
        'description': 'str'
    }

    attribute_map = {
        'pk': 'pk',
        'name': 'name',
        'date_start': 'date_start',
        'date_work_start': 'date_work_start',
        'user__username': 'user__username',
        'date_done': 'date_done',
        'duration': 'duration',
        'progress': 'progress',
        'status': 'status',
        'has_error': 'has_error',
        'description': 'description'
    }

    def __init__(self, pk=None, name=None, date_start=None, date_work_start=None, user__username=None, date_done=None, duration=None, progress=None, status=None, has_error=None, description=None, local_vars_configuration=None):  # noqa: E501
        """Task - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._pk = None
        self._name = None
        self._date_start = None
        self._date_work_start = None
        self._user__username = None
        self._date_done = None
        self._duration = None
        self._progress = None
        self._status = None
        self._has_error = None
        self._description = None
        self.discriminator = None

        if pk is not None:
            self.pk = pk
        self.name = name
        if date_start is not None:
            self.date_start = date_start
        self.date_work_start = date_work_start
        if user__username is not None:
            self.user__username = user__username
        self.date_done = date_done
        if duration is not None:
            self.duration = duration
        self.progress = progress
        self.status = status
        if has_error is not None:
            self.has_error = has_error
        if description is not None:
            self.description = description

    @property
    def pk(self):
        """Gets the pk of this Task.  # noqa: E501


        :return: The pk of this Task.  # noqa: E501
        :rtype: str
        """
        return self._pk

    @pk.setter
    def pk(self, pk):
        """Sets the pk of this Task.


        :param pk: The pk of this Task.  # noqa: E501
        :type pk: str
        """
        if (self.local_vars_configuration.client_side_validation and
                pk is not None and len(pk) > 255):
            raise ValueError("Invalid value for `pk`, length must be less than or equal to `255`")  # noqa: E501

        self._pk = pk

    @property
    def name(self):
        """Gets the name of this Task.  # noqa: E501


        :return: The name of this Task.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Task.


        :param name: The name of this Task.  # noqa: E501
        :type name: str
        """
        if (self.local_vars_configuration.client_side_validation and
                name is not None and len(name) > 100):
            raise ValueError("Invalid value for `name`, length must be less than or equal to `100`")  # noqa: E501

        self._name = name

    @property
    def date_start(self):
        """Gets the date_start of this Task.  # noqa: E501


        :return: The date_start of this Task.  # noqa: E501
        :rtype: datetime
        """
        return self._date_start

    @date_start.setter
    def date_start(self, date_start):
        """Sets the date_start of this Task.


        :param date_start: The date_start of this Task.  # noqa: E501
        :type date_start: datetime
        """

        self._date_start = date_start

    @property
    def date_work_start(self):
        """Gets the date_work_start of this Task.  # noqa: E501


        :return: The date_work_start of this Task.  # noqa: E501
        :rtype: datetime
        """
        return self._date_work_start

    @date_work_start.setter
    def date_work_start(self, date_work_start):
        """Sets the date_work_start of this Task.


        :param date_work_start: The date_work_start of this Task.  # noqa: E501
        :type date_work_start: datetime
        """

        self._date_work_start = date_work_start

    @property
    def user__username(self):
        """Gets the user__username of this Task.  # noqa: E501


        :return: The user__username of this Task.  # noqa: E501
        :rtype: str
        """
        return self._user__username

    @user__username.setter
    def user__username(self, user__username):
        """Sets the user__username of this Task.


        :param user__username: The user__username of this Task.  # noqa: E501
        :type user__username: str
        """

        self._user__username = user__username

    @property
    def date_done(self):
        """Gets the date_done of this Task.  # noqa: E501


        :return: The date_done of this Task.  # noqa: E501
        :rtype: datetime
        """
        return self._date_done

    @date_done.setter
    def date_done(self, date_done):
        """Sets the date_done of this Task.


        :param date_done: The date_done of this Task.  # noqa: E501
        :type date_done: datetime
        """

        self._date_done = date_done

    @property
    def duration(self):
        """Gets the duration of this Task.  # noqa: E501


        :return: The duration of this Task.  # noqa: E501
        :rtype: str
        """
        return self._duration

    @duration.setter
    def duration(self, duration):
        """Sets the duration of this Task.


        :param duration: The duration of this Task.  # noqa: E501
        :type duration: str
        """

        self._duration = duration

    @property
    def progress(self):
        """Gets the progress of this Task.  # noqa: E501


        :return: The progress of this Task.  # noqa: E501
        :rtype: int
        """
        return self._progress

    @progress.setter
    def progress(self, progress):
        """Sets the progress of this Task.


        :param progress: The progress of this Task.  # noqa: E501
        :type progress: int
        """
        if (self.local_vars_configuration.client_side_validation and
                progress is not None and progress > 2147483647):  # noqa: E501
            raise ValueError("Invalid value for `progress`, must be a value less than or equal to `2147483647`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                progress is not None and progress < 0):  # noqa: E501
            raise ValueError("Invalid value for `progress`, must be a value greater than or equal to `0`")  # noqa: E501

        self._progress = progress

    @property
    def status(self):
        """Gets the status of this Task.  # noqa: E501


        :return: The status of this Task.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this Task.


        :param status: The status of this Task.  # noqa: E501
        :type status: str
        """
        allowed_values = [None,"FAILURE", "PENDING", "RECEIVED", "RETRY", "REVOKED", "STARTED", "SUCCESS"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and status not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `status` ({0}), must be one of {1}"  # noqa: E501
                .format(status, allowed_values)
            )

        self._status = status

    @property
    def has_error(self):
        """Gets the has_error of this Task.  # noqa: E501


        :return: The has_error of this Task.  # noqa: E501
        :rtype: str
        """
        return self._has_error

    @has_error.setter
    def has_error(self, has_error):
        """Sets the has_error of this Task.


        :param has_error: The has_error of this Task.  # noqa: E501
        :type has_error: str
        """

        self._has_error = has_error

    @property
    def description(self):
        """Gets the description of this Task.  # noqa: E501


        :return: The description of this Task.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this Task.


        :param description: The description of this Task.  # noqa: E501
        :type description: str
        """

        self._description = description

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
        if not isinstance(other, Task):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Task):
            return True

        return self.to_dict() != other.to_dict()
