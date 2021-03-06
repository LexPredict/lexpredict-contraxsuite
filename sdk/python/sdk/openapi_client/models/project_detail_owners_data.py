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


class ProjectDetailOwnersData(object):
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
        'id': 'int',
        'username': 'str',
        'last_name': 'str',
        'first_name': 'str',
        'email': 'str',
        'is_superuser': 'bool',
        'is_staff': 'bool',
        'is_active': 'bool',
        'name': 'str',
        'role': 'int',
        'role_data': 'ProjectDetailRoleData',
        'organization': 'str',
        'photo': 'str',
        'permissions': 'object',
        'groups': 'list[int]'
    }

    attribute_map = {
        'id': 'id',
        'username': 'username',
        'last_name': 'last_name',
        'first_name': 'first_name',
        'email': 'email',
        'is_superuser': 'is_superuser',
        'is_staff': 'is_staff',
        'is_active': 'is_active',
        'name': 'name',
        'role': 'role',
        'role_data': 'role_data',
        'organization': 'organization',
        'photo': 'photo',
        'permissions': 'permissions',
        'groups': 'groups'
    }

    def __init__(self, id=None, username=None, last_name=None, first_name=None, email=None, is_superuser=None, is_staff=None, is_active=None, name=None, role=None, role_data=None, organization=None, photo=None, permissions=None, groups=None, local_vars_configuration=None):  # noqa: E501
        """ProjectDetailOwnersData - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._username = None
        self._last_name = None
        self._first_name = None
        self._email = None
        self._is_superuser = None
        self._is_staff = None
        self._is_active = None
        self._name = None
        self._role = None
        self._role_data = None
        self._organization = None
        self._photo = None
        self._permissions = None
        self._groups = None
        self.discriminator = None

        if id is not None:
            self.id = id
        self.username = username
        if last_name is not None:
            self.last_name = last_name
        if first_name is not None:
            self.first_name = first_name
        if email is not None:
            self.email = email
        if is_superuser is not None:
            self.is_superuser = is_superuser
        if is_staff is not None:
            self.is_staff = is_staff
        if is_active is not None:
            self.is_active = is_active
        if name is not None:
            self.name = name
        self.role = role
        if role_data is not None:
            self.role_data = role_data
        self.organization = organization
        if photo is not None:
            self.photo = photo
        if permissions is not None:
            self.permissions = permissions
        if groups is not None:
            self.groups = groups

    @property
    def id(self):
        """Gets the id of this ProjectDetailOwnersData.  # noqa: E501


        :return: The id of this ProjectDetailOwnersData.  # noqa: E501
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this ProjectDetailOwnersData.


        :param id: The id of this ProjectDetailOwnersData.  # noqa: E501
        :type id: int
        """

        self._id = id

    @property
    def username(self):
        """Gets the username of this ProjectDetailOwnersData.  # noqa: E501

        Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.  # noqa: E501

        :return: The username of this ProjectDetailOwnersData.  # noqa: E501
        :rtype: str
        """
        return self._username

    @username.setter
    def username(self, username):
        """Sets the username of this ProjectDetailOwnersData.

        Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.  # noqa: E501

        :param username: The username of this ProjectDetailOwnersData.  # noqa: E501
        :type username: str
        """
        if self.local_vars_configuration.client_side_validation and username is None:  # noqa: E501
            raise ValueError("Invalid value for `username`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                username is not None and len(username) > 150):
            raise ValueError("Invalid value for `username`, length must be less than or equal to `150`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                username is not None and not re.search(r'^[\w.@+-]+$', username)):  # noqa: E501
            raise ValueError(r"Invalid value for `username`, must be a follow pattern or equal to `/^[\w.@+-]+$/`")  # noqa: E501

        self._username = username

    @property
    def last_name(self):
        """Gets the last_name of this ProjectDetailOwnersData.  # noqa: E501


        :return: The last_name of this ProjectDetailOwnersData.  # noqa: E501
        :rtype: str
        """
        return self._last_name

    @last_name.setter
    def last_name(self, last_name):
        """Sets the last_name of this ProjectDetailOwnersData.


        :param last_name: The last_name of this ProjectDetailOwnersData.  # noqa: E501
        :type last_name: str
        """
        if (self.local_vars_configuration.client_side_validation and
                last_name is not None and len(last_name) > 150):
            raise ValueError("Invalid value for `last_name`, length must be less than or equal to `150`")  # noqa: E501

        self._last_name = last_name

    @property
    def first_name(self):
        """Gets the first_name of this ProjectDetailOwnersData.  # noqa: E501


        :return: The first_name of this ProjectDetailOwnersData.  # noqa: E501
        :rtype: str
        """
        return self._first_name

    @first_name.setter
    def first_name(self, first_name):
        """Sets the first_name of this ProjectDetailOwnersData.


        :param first_name: The first_name of this ProjectDetailOwnersData.  # noqa: E501
        :type first_name: str
        """
        if (self.local_vars_configuration.client_side_validation and
                first_name is not None and len(first_name) > 30):
            raise ValueError("Invalid value for `first_name`, length must be less than or equal to `30`")  # noqa: E501

        self._first_name = first_name

    @property
    def email(self):
        """Gets the email of this ProjectDetailOwnersData.  # noqa: E501


        :return: The email of this ProjectDetailOwnersData.  # noqa: E501
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email):
        """Sets the email of this ProjectDetailOwnersData.


        :param email: The email of this ProjectDetailOwnersData.  # noqa: E501
        :type email: str
        """
        if (self.local_vars_configuration.client_side_validation and
                email is not None and len(email) > 254):
            raise ValueError("Invalid value for `email`, length must be less than or equal to `254`")  # noqa: E501

        self._email = email

    @property
    def is_superuser(self):
        """Gets the is_superuser of this ProjectDetailOwnersData.  # noqa: E501

        Designates that this user has all permissions without explicitly assigning them.  # noqa: E501

        :return: The is_superuser of this ProjectDetailOwnersData.  # noqa: E501
        :rtype: bool
        """
        return self._is_superuser

    @is_superuser.setter
    def is_superuser(self, is_superuser):
        """Sets the is_superuser of this ProjectDetailOwnersData.

        Designates that this user has all permissions without explicitly assigning them.  # noqa: E501

        :param is_superuser: The is_superuser of this ProjectDetailOwnersData.  # noqa: E501
        :type is_superuser: bool
        """

        self._is_superuser = is_superuser

    @property
    def is_staff(self):
        """Gets the is_staff of this ProjectDetailOwnersData.  # noqa: E501

        Designates whether the user can log into this admin site.  # noqa: E501

        :return: The is_staff of this ProjectDetailOwnersData.  # noqa: E501
        :rtype: bool
        """
        return self._is_staff

    @is_staff.setter
    def is_staff(self, is_staff):
        """Sets the is_staff of this ProjectDetailOwnersData.

        Designates whether the user can log into this admin site.  # noqa: E501

        :param is_staff: The is_staff of this ProjectDetailOwnersData.  # noqa: E501
        :type is_staff: bool
        """

        self._is_staff = is_staff

    @property
    def is_active(self):
        """Gets the is_active of this ProjectDetailOwnersData.  # noqa: E501

        Designates whether this user should be treated as active. Unselect this instead of deleting accounts.  # noqa: E501

        :return: The is_active of this ProjectDetailOwnersData.  # noqa: E501
        :rtype: bool
        """
        return self._is_active

    @is_active.setter
    def is_active(self, is_active):
        """Sets the is_active of this ProjectDetailOwnersData.

        Designates whether this user should be treated as active. Unselect this instead of deleting accounts.  # noqa: E501

        :param is_active: The is_active of this ProjectDetailOwnersData.  # noqa: E501
        :type is_active: bool
        """

        self._is_active = is_active

    @property
    def name(self):
        """Gets the name of this ProjectDetailOwnersData.  # noqa: E501


        :return: The name of this ProjectDetailOwnersData.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this ProjectDetailOwnersData.


        :param name: The name of this ProjectDetailOwnersData.  # noqa: E501
        :type name: str
        """
        if (self.local_vars_configuration.client_side_validation and
                name is not None and len(name) > 255):
            raise ValueError("Invalid value for `name`, length must be less than or equal to `255`")  # noqa: E501

        self._name = name

    @property
    def role(self):
        """Gets the role of this ProjectDetailOwnersData.  # noqa: E501


        :return: The role of this ProjectDetailOwnersData.  # noqa: E501
        :rtype: int
        """
        return self._role

    @role.setter
    def role(self, role):
        """Sets the role of this ProjectDetailOwnersData.


        :param role: The role of this ProjectDetailOwnersData.  # noqa: E501
        :type role: int
        """

        self._role = role

    @property
    def role_data(self):
        """Gets the role_data of this ProjectDetailOwnersData.  # noqa: E501


        :return: The role_data of this ProjectDetailOwnersData.  # noqa: E501
        :rtype: ProjectDetailRoleData
        """
        return self._role_data

    @role_data.setter
    def role_data(self, role_data):
        """Sets the role_data of this ProjectDetailOwnersData.


        :param role_data: The role_data of this ProjectDetailOwnersData.  # noqa: E501
        :type role_data: ProjectDetailRoleData
        """

        self._role_data = role_data

    @property
    def organization(self):
        """Gets the organization of this ProjectDetailOwnersData.  # noqa: E501


        :return: The organization of this ProjectDetailOwnersData.  # noqa: E501
        :rtype: str
        """
        return self._organization

    @organization.setter
    def organization(self, organization):
        """Sets the organization of this ProjectDetailOwnersData.


        :param organization: The organization of this ProjectDetailOwnersData.  # noqa: E501
        :type organization: str
        """
        if (self.local_vars_configuration.client_side_validation and
                organization is not None and len(organization) > 100):
            raise ValueError("Invalid value for `organization`, length must be less than or equal to `100`")  # noqa: E501

        self._organization = organization

    @property
    def photo(self):
        """Gets the photo of this ProjectDetailOwnersData.  # noqa: E501


        :return: The photo of this ProjectDetailOwnersData.  # noqa: E501
        :rtype: str
        """
        return self._photo

    @photo.setter
    def photo(self, photo):
        """Sets the photo of this ProjectDetailOwnersData.


        :param photo: The photo of this ProjectDetailOwnersData.  # noqa: E501
        :type photo: str
        """

        self._photo = photo

    @property
    def permissions(self):
        """Gets the permissions of this ProjectDetailOwnersData.  # noqa: E501


        :return: The permissions of this ProjectDetailOwnersData.  # noqa: E501
        :rtype: object
        """
        return self._permissions

    @permissions.setter
    def permissions(self, permissions):
        """Sets the permissions of this ProjectDetailOwnersData.


        :param permissions: The permissions of this ProjectDetailOwnersData.  # noqa: E501
        :type permissions: object
        """

        self._permissions = permissions

    @property
    def groups(self):
        """Gets the groups of this ProjectDetailOwnersData.  # noqa: E501

        The groups this user belongs to. A user will get all permissions granted to each of their groups.  # noqa: E501

        :return: The groups of this ProjectDetailOwnersData.  # noqa: E501
        :rtype: list[int]
        """
        return self._groups

    @groups.setter
    def groups(self, groups):
        """Sets the groups of this ProjectDetailOwnersData.

        The groups this user belongs to. A user will get all permissions granted to each of their groups.  # noqa: E501

        :param groups: The groups of this ProjectDetailOwnersData.  # noqa: E501
        :type groups: list[int]
        """

        self._groups = groups

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
        if not isinstance(other, ProjectDetailOwnersData):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ProjectDetailOwnersData):
            return True

        return self.to_dict() != other.to_dict()
