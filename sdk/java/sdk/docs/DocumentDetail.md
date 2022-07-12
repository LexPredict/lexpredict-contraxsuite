

# DocumentDetail


## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**pk** | **Integer** |  |  [optional] [readonly] |
|**name** | **String** |  |  [optional] |
|**documentType** | **String** |  |  [optional] |
|**fileSize** | **Integer** |  |  [optional] |
|**folder** | **String** |  |  [optional] |
|**createdDate** | **OffsetDateTime** |  |  [optional] |
|**modifiedDate** | **OffsetDateTime** |  |  [optional] |
|**modifiedByName** | **String** |  |  |
|**createdByName** | **String** |  |  |
|**createdByInitials** | **String** |  |  |
|**createdByPhoto** | **String** |  |  |
|**modifiedByInitials** | **String** |  |  |
|**modifiedByPhoto** | **String** |  |  |
|**status** | **Integer** |  |  [optional] |
|**statusData** | [**DocumentDetailStatusData**](DocumentDetailStatusData.md) |  |  |
|**availableStatusesData** | **List&lt;Object&gt;** |  |  [optional] [readonly] |
|**assignee** | **Integer** |  |  [optional] |
|**assignDate** | **OffsetDateTime** |  |  [optional] |
|**assigneeData** | [**DocumentDetailAssigneeData**](DocumentDetailAssigneeData.md) |  |  |
|**availableAssigneesData** | [**List&lt;DocumentDetailAvailableAssigneesDataInner&gt;**](DocumentDetailAvailableAssigneesDataInner.md) |  |  |
|**description** | **String** |  |  [optional] |
|**title** | **String** |  |  [optional] |
|**initialAnnotationId** | **String** |  |  [optional] [readonly] |
|**pageLocations** | **List&lt;List&lt;Integer&gt;&gt;** |  |  [optional] [readonly] |
|**pageBounds** | **List&lt;List&lt;BigDecimal&gt;&gt;** |  |  [optional] [readonly] |
|**fieldValues** | **Object** |  |  [optional] [readonly] |
|**fieldValueObjects** | **Object** |  |  [optional] [readonly] |
|**prevId** | **Integer** |  |  [optional] [readonly] |
|**nextId** | **Integer** |  |  [optional] [readonly] |
|**position** | **String** |  |  [optional] [readonly] |
|**documentsCount** | **String** |  |  [optional] [readonly] |
|**sections** | **List&lt;Object&gt;** |  |  [optional] [readonly] |
|**clusterId** | **String** |  |  [optional] [readonly] |
|**wasOpenedInAnnotator** | **Boolean** |  |  [optional] [readonly] |
|**userPermissions** | **Object** |  |  [optional] [readonly] |



