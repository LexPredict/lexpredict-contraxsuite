# DocumentTypeCreate

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uid** | **str** |  | [optional] [readonly] 
**title** | **str** |  | 
**code** | **str** | Field codes must be lowercase, should start with a Latin letter, and contain  only Latin letters, digits, and underscores. | 
**categories** | [**list[DocumentTypeDetailCategories]**](DocumentTypeDetailCategories.md) |  | [optional] [readonly] 
**managers** | **list[int]** |  | [optional] 
**fields** | [**list[DocumentFieldCategoryListFields]**](DocumentFieldCategoryListFields.md) |  | [optional] [readonly] 
**search_fields** | **list[str]** |  | [optional] 
**editor_type** | **str** |  | [optional] 
**field_code_aliases** | **object** |  | [optional] 
**metadata** | **object** |  | [optional] 
**warning_message** | **str** |  | [optional] [readonly] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


