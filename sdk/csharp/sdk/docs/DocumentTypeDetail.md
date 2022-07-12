
# Org.OpenAPITools.Model.DocumentTypeDetail

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Uid** | **Guid** |  | [optional] [readonly] 
**Title** | **string** |  | 
**Code** | **string** | Field codes must be lowercase, should start with a Latin letter, and contain  only Latin letters, digits, and underscores. | 
**FieldsData** | [**List&lt;DocumentTypeDetailFieldsDataInner&gt;**](DocumentTypeDetailFieldsDataInner.md) |  | [optional] [readonly] 
**SearchFields** | **List&lt;string&gt;** |  | [optional] 
**EditorType** | **string** |  | [optional] 
**CreatedByName** | **string** |  | [optional] [readonly] 
**CreatedDate** | **DateTime** |  | [optional] [readonly] 
**ModifiedByName** | **string** |  | [optional] [readonly] 
**ModifiedDate** | **DateTime** |  | [optional] [readonly] 
**Metadata** | **Object** |  | [optional] 
**FieldsNumber** | **int** |  | 
**Categories** | [**List&lt;DocumentTypeDetailCategoriesInner&gt;**](DocumentTypeDetailCategoriesInner.md) |  | [optional] [readonly] 
**Managers** | **List&lt;int&gt;** | Choose which users can modify this Document Type. Users chosen as Managers can be of any System-Level Permission. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to README]](../README.md)

