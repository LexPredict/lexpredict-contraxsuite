

# ProjectDetail

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**pk** | **Integer** |  |  [optional] [readonly]
**name** | **String** |  | 
**description** | **String** |  |  [optional]
**sendEmailNotification** | **Boolean** |  |  [optional]
**hideClauseReview** | **Boolean** |  |  [optional]
**status** | **Integer** |  |  [optional]
**statusData** | [**ProjectListStatusData**](ProjectListStatusData.md) |  |  [optional]
**owners** | **List&lt;Integer&gt;** |  |  [optional]
**ownersData** | [**List&lt;ProjectDetailOwnersData&gt;**](ProjectDetailOwnersData.md) |  |  [optional] [readonly]
**reviewers** | **List&lt;Integer&gt;** |  |  [optional]
**reviewersData** | [**List&lt;ProjectDetailOwnersData&gt;**](ProjectDetailOwnersData.md) |  |  [optional] [readonly]
**superReviewers** | **List&lt;Integer&gt;** |  |  [optional]
**superReviewersData** | [**List&lt;ProjectDetailOwnersData&gt;**](ProjectDetailOwnersData.md) |  |  [optional] [readonly]
**juniorReviewers** | **List&lt;Integer&gt;** |  |  [optional]
**juniorReviewersData** | [**List&lt;ProjectDetailOwnersData&gt;**](ProjectDetailOwnersData.md) |  |  [optional] [readonly]
**type** | **String** |  |  [optional]
**typeData** | [**ProjectListTypeData**](ProjectListTypeData.md) |  | 
**progress** | **String** |  |  [optional] [readonly]
**userPermissions** | **String** |  |  [optional] [readonly]



