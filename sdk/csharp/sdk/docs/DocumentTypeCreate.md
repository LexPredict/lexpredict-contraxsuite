
# Org.OpenAPITools.Model.DocumentTypeCreate

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Uid** | **Guid** |  | [optional] [readonly] 
**Title** | **string** |  | 
**Code** | **string** | Field codes must be lowercase, should start with a Latin letter, and contain  only Latin letters, digits, and underscores. | 
**Categories** | [**List&lt;DocumentTypeDetailCategoriesInner&gt;**](DocumentTypeDetailCategoriesInner.md) |  | [optional] [readonly] 
**Managers** | **List&lt;int&gt;** | Choose which users can modify this Document Type. Users chosen as Managers can be of any System-Level Permission. | [optional] 
**Fields** | [**List&lt;DocumentFieldCategoryListFieldsInner&gt;**](DocumentFieldCategoryListFieldsInner.md) |  | [optional] [readonly] 
**SearchFields** | **List&lt;string&gt;** |  | [optional] 
**EditorType** | **string** |  | 
**FieldCodeAliases** | **Object** |  | [optional] 
**Metadata** | **Object** |  | [optional] 
**WarningMessage** | **string** |  | [optional] [readonly] 

[[Back to Model list]](../README.md#documentation-for-models)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to README]](../README.md)

