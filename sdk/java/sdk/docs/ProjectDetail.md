

# ProjectDetail


## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**pk** | **Integer** |  |  [optional] [readonly] |
|**name** | **String** |  |  |
|**description** | **String** |  |  [optional] |
|**createdDate** | **OffsetDateTime** |  |  [optional] |
|**createdByName** | **String** |  |  |
|**modifiedDate** | **OffsetDateTime** |  |  [optional] |
|**modifiedByName** | **String** |  |  |
|**sendEmailNotification** | **Boolean** |  |  [optional] |
|**hideClauseReview** | **Boolean** |  |  [optional] |
|**status** | **Integer** |  |  [optional] |
|**statusData** | [**ProjectListStatusData**](ProjectListStatusData.md) |  |  [optional] |
|**owners** | **List&lt;Integer&gt;** |  |  [optional] |
|**ownersData** | [**List&lt;ProjectDetailOwnersDataInner&gt;**](ProjectDetailOwnersDataInner.md) |  |  [optional] [readonly] |
|**reviewers** | **List&lt;Integer&gt;** |  |  [optional] |
|**reviewersData** | [**List&lt;ProjectDetailOwnersDataInner&gt;**](ProjectDetailOwnersDataInner.md) |  |  [optional] [readonly] |
|**superReviewers** | **List&lt;Integer&gt;** |  |  [optional] |
|**superReviewersData** | [**List&lt;ProjectDetailOwnersDataInner&gt;**](ProjectDetailOwnersDataInner.md) |  |  [optional] [readonly] |
|**juniorReviewers** | **List&lt;Integer&gt;** |  |  [optional] |
|**juniorReviewersData** | [**List&lt;ProjectDetailOwnersDataInner&gt;**](ProjectDetailOwnersDataInner.md) |  |  [optional] [readonly] |
|**type** | **String** |  |  [optional] |
|**typeData** | [**ProjectListTypeData**](ProjectListTypeData.md) |  |  |
|**progress** | **String** |  |  [optional] [readonly] |
|**userPermissions** | **String** |  |  [optional] [readonly] |
|**termTags** | **List&lt;Integer&gt;** |  |  [optional] |
|**documentTransformer** | **Integer** |  |  [optional] |
|**textUnitTransformer** | **Integer** |  |  [optional] |
|**companytypeTags** | **List&lt;Integer&gt;** |  |  [optional] |
|**appVars** | **String** |  |  [optional] [readonly] |
|**documentSimilarityRunParams** | **String** |  |  [optional] [readonly] |
|**textUnitSimilarityRunParams** | **String** |  |  [optional] [readonly] |
|**documentSimilarityProcessAllowed** | **String** |  |  [optional] [readonly] |
|**textUnitSimilarityProcessAllowed** | **String** |  |  [optional] [readonly] |



