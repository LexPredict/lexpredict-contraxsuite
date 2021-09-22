# DocumentTypeCreate


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** |  | 
**code** | **str** | Field codes must be lowercase, should start with a Latin letter, and contain  only Latin letters, digits, and underscores. | 
**editor_type** | **str** |  | 
**uid** | **str** |  | [optional] [readonly] 
**categories** | [**[DocumentTypeDetailCategories]**](DocumentTypeDetailCategories.md) |  | [optional] [readonly] 
**managers** | **[int]** | Choose which users can modify this Document Type. Users chosen as Managers can be of any System-Level Permission. | [optional] 
**fields** | [**[DocumentFieldCategoryListFields]**](DocumentFieldCategoryListFields.md) |  | [optional] [readonly] 
**search_fields** | **[str]** |  | [optional] 
**field_code_aliases** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}, none_type** |  | [optional] 
**metadata** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}, none_type** |  | [optional] 
**warning_message** | **str** |  | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


