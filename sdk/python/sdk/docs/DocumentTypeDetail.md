# DocumentTypeDetail


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** |  | 
**code** | **str** | Field codes must be lowercase, should start with a Latin letter, and contain  only Latin letters, digits, and underscores. | 
**fields_number** | **int** |  | 
**uid** | **str** |  | [optional] [readonly] 
**fields_data** | [**[DocumentTypeDetailFieldsData]**](DocumentTypeDetailFieldsData.md) |  | [optional] [readonly] 
**search_fields** | **[str]** |  | [optional] 
**editor_type** | **str** |  | [optional] 
**created_by__name** | **str** |  | [optional] [readonly] 
**created_date** | **datetime** |  | [optional] [readonly] 
**modified_by__name** | **str** |  | [optional] [readonly] 
**modified_date** | **datetime** |  | [optional] [readonly] 
**metadata** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}, none_type** |  | [optional] 
**categories** | [**[DocumentTypeDetailCategories]**](DocumentTypeDetailCategories.md) |  | [optional] [readonly] 
**managers** | **[int]** | Choose which users can modify this Document Type. Users chosen as Managers can be of any System-Level Permission. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


