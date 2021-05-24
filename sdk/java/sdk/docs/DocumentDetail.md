

# DocumentDetail


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**pk** | **Integer** |  |  [optional] [readonly]
**name** | **String** |  |  [optional]
**documentType** | **String** |  |  [optional]
**fileSize** | **Integer** |  |  [optional]
**folder** | **String** |  |  [optional]
**createdDate** | **OffsetDateTime** |  |  [optional]
**createdByName** | **String** |  | 
**modifiedDate** | **OffsetDateTime** |  |  [optional]
**modifiedByName** | **String** |  | 
**status** | **Integer** |  |  [optional]
**statusData** | [**DocumentDetailStatusData**](DocumentDetailStatusData.md) |  | 
**availableStatusesData** | **List&lt;Object&gt;** |  |  [optional] [readonly]
**assignee** | **Integer** |  |  [optional]
**assignDate** | **OffsetDateTime** |  |  [optional]
**assigneeData** | [**DocumentDetailAssigneeData**](DocumentDetailAssigneeData.md) |  | 
**availableAssigneesData** | [**List&lt;DocumentDetailAvailableAssigneesData&gt;**](DocumentDetailAvailableAssigneesData.md) |  | 
**description** | **String** |  |  [optional]
**title** | **String** |  |  [optional]
**initialAnnotationId** | **String** |  |  [optional] [readonly]
**pageLocations** | **List&lt;List&lt;Integer&gt;&gt;** |  |  [optional] [readonly]
**pageBounds** | **List&lt;List&lt;BigDecimal&gt;&gt;** |  |  [optional] [readonly]
**notes** | [**List&lt;DocumentDetailNotes&gt;**](DocumentDetailNotes.md) |  | 
**fieldValues** | **Object** |  |  [optional] [readonly]
**fieldValueObjects** | **Object** |  |  [optional] [readonly]
**prevId** | **Integer** |  |  [optional] [readonly]
**nextId** | **Integer** |  |  [optional] [readonly]
**sections** | **List&lt;Object&gt;** |  |  [optional] [readonly]
**clusterId** | **String** |  |  [optional] [readonly]
**userPermissions** | **Object** |  |  [optional] [readonly]



