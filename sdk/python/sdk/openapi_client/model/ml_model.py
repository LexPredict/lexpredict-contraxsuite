"""
    Contraxsuite API

    Contraxsuite API  # noqa: E501

    The version of the OpenAPI document: 2.0.0
    Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401
import sys  # noqa: F401

from openapi_client.model_utils import (  # noqa: F401
    ApiTypeError,
    ModelComposed,
    ModelNormal,
    ModelSimple,
    cached_property,
    change_keys_js_to_python,
    convert_js_args_to_python_args,
    date,
    datetime,
    file_type,
    none_type,
    validate_get_composed_info,
)


class MLModel(ModelNormal):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.

    Attributes:
      allowed_values (dict): The key is the tuple path to the attribute
          and the for var_name this is (var_name,). The value is a dict
          with a capitalized key describing the allowed value and an allowed
          value. These dicts store the allowed enum values.
      attribute_map (dict): The key is attribute name
          and the value is json key in definition.
      discriminator_value_class_map (dict): A dict to go from the discriminator
          variable value to the discriminator class name.
      validations (dict): The key is the tuple path to the attribute
          and the for var_name this is (var_name,). The value is a dict
          that stores validations for max_length, min_length, max_items,
          min_items, exclusive_maximum, inclusive_maximum, exclusive_minimum,
          inclusive_minimum, and regex.
      additional_properties_type (tuple): A tuple of classes accepted
          as additional properties values.
    """

    allowed_values = {
        ('apply_to',): {
            'None': None,
            'DOCUMENT': "document",
            'TEXT_UNIT': "text_unit",
        },
        ('target_entity',): {
            'None': None,
            'TRANSFORMER': "transformer",
            'CLASSIFIER': "classifier",
            'CONTRACT_TYPE_CLASSIFIER': "contract_type_classifier",
        },
        ('text_unit_type',): {
            'None': None,
            'SENTENCE': "sentence",
            'PARAGRAPH': "paragraph",
        },
    }

    validations = {
        ('name',): {
            'max_length': 1024,
        },
        ('version',): {
            'max_length': 1024,
        },
        ('model_path',): {
            'max_length': 1024,
        },
        ('language',): {
            'max_length': 12,
        },
        ('vector_name',): {
            'max_length': 1024,
        },
    }

    additional_properties_type = None

    _nullable = False

    @cached_property
    def openapi_types():
        """
        This must be a method because a model may have properties that are
        of type self, this must run after the class is loaded

        Returns
            openapi_types (dict): The key is attribute name
                and the value is attribute type.
        """
        return {
            'name': (str,),  # noqa: E501
            'version': (str,),  # noqa: E501
            'model_path': (str,),  # noqa: E501
            'apply_to': (str, none_type,),  # noqa: E501
            'target_entity': (str, none_type,),  # noqa: E501
            'language': (str, none_type,),  # noqa: E501
            'id': (int,),  # noqa: E501
            'vector_name': (str, none_type,),  # noqa: E501
            'is_active': (bool,),  # noqa: E501
            'default': (bool,),  # noqa: E501
            'text_unit_type': (str, none_type,),  # noqa: E501
            'project': (int, none_type,),  # noqa: E501
        }

    @cached_property
    def discriminator():
        return None


    attribute_map = {
        'name': 'name',  # noqa: E501
        'version': 'version',  # noqa: E501
        'model_path': 'model_path',  # noqa: E501
        'apply_to': 'apply_to',  # noqa: E501
        'target_entity': 'target_entity',  # noqa: E501
        'language': 'language',  # noqa: E501
        'id': 'id',  # noqa: E501
        'vector_name': 'vector_name',  # noqa: E501
        'is_active': 'is_active',  # noqa: E501
        'default': 'default',  # noqa: E501
        'text_unit_type': 'text_unit_type',  # noqa: E501
        'project': 'project',  # noqa: E501
    }

    _composed_schemas = {}

    required_properties = set([
        '_data_store',
        '_check_type',
        '_spec_property_naming',
        '_path_to_item',
        '_configuration',
        '_visited_composed_classes',
    ])

    @convert_js_args_to_python_args
    def __init__(self, name, version, model_path, apply_to, target_entity, language, *args, **kwargs):  # noqa: E501
        """MLModel - a model defined in OpenAPI

        Args:
            name (str): Model name, may include module parameters
            version (str): Model version
            model_path (str): Model path, relative to WebDAV root folder
            apply_to (str, none_type): Should the model be applied to documents or text units
            target_entity (str, none_type): The model class
            language (str, none_type): Language (ISO 693-1) code, may be omitted

        Keyword Args:
            _check_type (bool): if True, values for parameters in openapi_types
                                will be type checked and a TypeError will be
                                raised if the wrong type is input.
                                Defaults to True
            _path_to_item (tuple/list): This is a list of keys or values to
                                drill down to the model in received_data
                                when deserializing a response
            _spec_property_naming (bool): True if the variable names in the input data
                                are serialized names, as specified in the OpenAPI document.
                                False if the variable names in the input data
                                are pythonic names, e.g. snake case (default)
            _configuration (Configuration): the instance to use when
                                deserializing a file_type parameter.
                                If passed, type conversion is attempted
                                If omitted no type conversion is done.
            _visited_composed_classes (tuple): This stores a tuple of
                                classes that we have traveled through so that
                                if we see that class again we will not use its
                                discriminator again.
                                When traveling through a discriminator, the
                                composed schema that is
                                is traveled through is added to this set.
                                For example if Animal has a discriminator
                                petType and we pass in "Dog", and the class Dog
                                allOf includes Animal, we move through Animal
                                once using the discriminator, and pick Dog.
                                Then in Dog, we will make an instance of the
                                Animal class but this time we won't travel
                                through its discriminator because we passed in
                                _visited_composed_classes = (Animal,)
            id (int): [optional]  # noqa: E501
            vector_name (str, none_type): [optional]  # noqa: E501
            is_active (bool): Inactive models are ignored. [optional]  # noqa: E501
            default (bool): The default model is used unless another model is deliberately selected. [optional]  # noqa: E501
            text_unit_type (str, none_type): Text unit type: sentence or paragraph. [optional]  # noqa: E501
            project (int, none_type): Optional project reference. [optional]  # noqa: E501
        """

        _check_type = kwargs.pop('_check_type', True)
        _spec_property_naming = kwargs.pop('_spec_property_naming', False)
        _path_to_item = kwargs.pop('_path_to_item', ())
        _configuration = kwargs.pop('_configuration', None)
        _visited_composed_classes = kwargs.pop('_visited_composed_classes', ())

        if args:
            raise ApiTypeError(
                "Invalid positional arguments=%s passed to %s. Remove those invalid positional arguments." % (
                    args,
                    self.__class__.__name__,
                ),
                path_to_item=_path_to_item,
                valid_classes=(self.__class__,),
            )

        self._data_store = {}
        self._check_type = _check_type
        self._spec_property_naming = _spec_property_naming
        self._path_to_item = _path_to_item
        self._configuration = _configuration
        self._visited_composed_classes = _visited_composed_classes + (self.__class__,)

        self.name = name
        self.version = version
        self.model_path = model_path
        self.apply_to = apply_to
        self.target_entity = target_entity
        self.language = language
        for var_name, var_value in kwargs.items():
            if var_name not in self.attribute_map and \
                        self._configuration is not None and \
                        self._configuration.discard_unknown_keys and \
                        self.additional_properties_type is None:
                # discard variable.
                continue
            setattr(self, var_name, var_value)