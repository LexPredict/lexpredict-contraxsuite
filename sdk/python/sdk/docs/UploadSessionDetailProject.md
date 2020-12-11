# UploadSessionDetailProject

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**pk** | **int** |  | [optional] [readonly] 
**name** | **str** |  | 
**description** | **str** |  | [optional] 
**send_email_notification** | **bool** |  | [optional] 
**hide_clause_review** | **bool** |  | [optional] 
**status** | **int** |  | [optional] 
**status_data** | [**ProjectListStatusData**](ProjectListStatusData.md) |  | [optional] 
**owners** | **list[int]** |  | [optional] 
**owners_data** | [**list[ProjectDetailOwnersData]**](ProjectDetailOwnersData.md) |  | [optional] [readonly] 
**reviewers** | **list[int]** |  | [optional] 
**reviewers_data** | [**list[ProjectDetailOwnersData]**](ProjectDetailOwnersData.md) |  | [optional] [readonly] 
**super_reviewers** | **list[int]** |  | [optional] 
**super_reviewers_data** | [**list[ProjectDetailOwnersData]**](ProjectDetailOwnersData.md) |  | [optional] [readonly] 
**junior_reviewers** | **list[int]** |  | [optional] 
**junior_reviewers_data** | [**list[ProjectDetailOwnersData]**](ProjectDetailOwnersData.md) |  | [optional] [readonly] 
**type** | **str** |  | [optional] 
**type_data** | [**ProjectListTypeData**](ProjectListTypeData.md) |  | 
**progress** | **str** |  | [optional] [readonly] 
**user_permissions** | **str** |  | [optional] [readonly] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


