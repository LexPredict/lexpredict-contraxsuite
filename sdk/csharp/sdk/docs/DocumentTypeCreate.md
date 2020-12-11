
# Org.OpenAPITools.Model.DocumentTypeCreate

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Uid** | **Guid** |  | [optional] [readonly] 
**Title** | **string** |  | 
**Code** | **string** | Field codes must be lowercase, should start with a Latin letter, and contain  only Latin letters, digits, and underscores. | 
**Categories** | [**List&lt;DocumentTypeDetailCategories&gt;**](DocumentTypeDetailCategories.md) |  | [optional] [readonly] 
**Managers** | **List&lt;int&gt;** |  | [optional] 
**Fields** | [**List&lt;DocumentFieldCategoryListFields&gt;**](DocumentFieldCategoryListFields.md) |  | [optional] [readonly] 
**SearchFields** | **List&lt;string&gt;** |  | [optional] 
**EditorType** | **string** |  | [optional] 
**FieldCodeAliases** | **Object** |  | [optional] 
**Metadata** | **Object** |  | [optional] 
**WarningMessage** | **string** |  | [optional] [readonly] 

[[Back to Model list]](../README.md#documentation-for-models)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to README]](../README.md)

