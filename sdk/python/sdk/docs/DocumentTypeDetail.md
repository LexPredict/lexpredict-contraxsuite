# DocumentTypeDetail

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uid** | **str** |  | [optional] [readonly] 
**title** | **str** |  | 
**code** | **str** | Field codes must be lowercase, should start with a Latin letter, and contain  only Latin letters, digits, and underscores. | 
**fields_data** | [**list[DocumentTypeDetailFieldsData]**](DocumentTypeDetailFieldsData.md) |  | [optional] [readonly] 
**search_fields** | **list[str]** |  | [optional] 
**modified_by__username** | **str** |  | [optional] [readonly] 
**editor_type** | **str** |  | [optional] 
**created_by** | [**DocumentDetailAssigneeData**](DocumentDetailAssigneeData.md) |  | 
**created_date** | **datetime** |  | [optional] [readonly] 
**modified_by** | [**DocumentDetailAssigneeData**](DocumentDetailAssigneeData.md) |  | 
**modified_date** | **datetime** |  | [optional] [readonly] 
**metadata** | **object** |  | [optional] 
**fields_number** | **int** |  | 
**categories** | [**list[DocumentTypeDetailCategories]**](DocumentTypeDetailCategories.md) |  | [optional] [readonly] 
**managers** | **list[int]** |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


