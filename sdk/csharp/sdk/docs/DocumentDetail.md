
# Org.OpenAPITools.Model.DocumentDetail

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Pk** | **int** |  | [optional] [readonly] 
**Name** | **string** |  | [optional] 
**DocumentType** | **string** |  | [optional] 
**FileSize** | **int** |  | [optional] 
**Folder** | **string** |  | [optional] 
**CreatedDate** | **DateTime?** |  | [optional] 
**CreatedByName** | **string** |  | 
**ModifiedDate** | **DateTime?** |  | [optional] 
**ModifiedByName** | **string** |  | 
**Status** | **int?** |  | [optional] 
**StatusData** | [**DocumentDetailStatusData**](DocumentDetailStatusData.md) |  | 
**AvailableStatusesData** | **List&lt;Object&gt;** |  | [optional] [readonly] 
**Assignee** | **int?** |  | [optional] 
**AssignDate** | **DateTime?** |  | [optional] 
**AssigneeData** | [**DocumentDetailAssigneeData**](DocumentDetailAssigneeData.md) |  | 
**AvailableAssigneesData** | [**List&lt;DocumentDetailAvailableAssigneesData&gt;**](DocumentDetailAvailableAssigneesData.md) |  | 
**Description** | **string** |  | [optional] 
**Title** | **string** |  | [optional] 
**InitialAnnotationId** | **string** |  | [optional] [readonly] 
**PageLocations** | **List&lt;List&lt;int&gt;&gt;** |  | [optional] [readonly] 
**PageBounds** | **List&lt;List&lt;decimal&gt;&gt;** |  | [optional] [readonly] 
**Notes** | [**List&lt;DocumentDetailNotes&gt;**](DocumentDetailNotes.md) |  | 
**FieldValues** | **Object** |  | [optional] [readonly] 
**FieldValueObjects** | **Object** |  | [optional] [readonly] 
**PrevId** | **int** |  | [optional] [readonly] 
**NextId** | **int** |  | [optional] [readonly] 
**Sections** | **List&lt;Object&gt;** |  | [optional] [readonly] 
**ClusterId** | **string** |  | [optional] [readonly] 
**UserPermissions** | **Object** |  | [optional] [readonly] 

[[Back to Model list]](../README.md#documentation-for-models)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to README]](../README.md)

