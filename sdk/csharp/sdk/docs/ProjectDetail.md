
# Org.OpenAPITools.Model.ProjectDetail

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Pk** | **int** |  | [optional] [readonly] 
**Name** | **string** |  | 
**Description** | **string** |  | [optional] 
**SendEmailNotification** | **bool** |  | [optional] 
**HideClauseReview** | **bool** |  | [optional] 
**Status** | **int** |  | [optional] 
**StatusData** | [**ProjectListStatusData**](ProjectListStatusData.md) |  | [optional] 
**Owners** | **List&lt;int&gt;** |  | [optional] 
**OwnersData** | [**List&lt;ProjectDetailOwnersData&gt;**](ProjectDetailOwnersData.md) |  | [optional] [readonly] 
**Reviewers** | **List&lt;int&gt;** |  | [optional] 
**ReviewersData** | [**List&lt;ProjectDetailOwnersData&gt;**](ProjectDetailOwnersData.md) |  | [optional] [readonly] 
**SuperReviewers** | **List&lt;int&gt;** |  | [optional] 
**SuperReviewersData** | [**List&lt;ProjectDetailOwnersData&gt;**](ProjectDetailOwnersData.md) |  | [optional] [readonly] 
**JuniorReviewers** | **List&lt;int&gt;** |  | [optional] 
**JuniorReviewersData** | [**List&lt;ProjectDetailOwnersData&gt;**](ProjectDetailOwnersData.md) |  | [optional] [readonly] 
**Type** | **string** |  | [optional] 
**TypeData** | [**ProjectListTypeData**](ProjectListTypeData.md) |  | 
**Progress** | **string** |  | [optional] [readonly] 
**UserPermissions** | **string** |  | [optional] [readonly] 

[[Back to Model list]](../README.md#documentation-for-models)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to README]](../README.md)

