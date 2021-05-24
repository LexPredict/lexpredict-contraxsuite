# DocumentDetail


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by_name** | **str** |  | 
**modified_by_name** | **str** |  | 
**status_data** | [**DocumentDetailStatusData**](DocumentDetailStatusData.md) |  | 
**assignee_data** | [**DocumentDetailAssigneeData**](DocumentDetailAssigneeData.md) |  | 
**available_assignees_data** | [**[DocumentDetailAvailableAssigneesData], none_type**](DocumentDetailAvailableAssigneesData.md) |  | 
**notes** | [**[DocumentDetailNotes]**](DocumentDetailNotes.md) |  | 
**pk** | **int** |  | [optional] [readonly] 
**name** | **str, none_type** |  | [optional] 
**document_type** | **str, none_type** |  | [optional] 
**file_size** | **int** |  | [optional] 
**folder** | **str, none_type** |  | [optional] 
**created_date** | **datetime, none_type** |  | [optional] 
**modified_date** | **datetime, none_type** |  | [optional] 
**status** | **int, none_type** |  | [optional] 
**available_statuses_data** | **[{str: (bool, date, datetime, dict, float, int, list, str, none_type)}]** |  | [optional] [readonly] 
**assignee** | **int, none_type** |  | [optional] 
**assign_date** | **datetime, none_type** |  | [optional] 
**description** | **str, none_type** |  | [optional] 
**title** | **str, none_type** |  | [optional] 
**initial_annotation_id** | **str** |  | [optional] [readonly] 
**page_locations** | **[[int]]** |  | [optional] [readonly] 
**page_bounds** | **[[float]]** |  | [optional] [readonly] 
**field_values** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** |  | [optional] [readonly] 
**field_value_objects** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** |  | [optional] [readonly] 
**prev_id** | **int** |  | [optional] [readonly] 
**next_id** | **int** |  | [optional] [readonly] 
**sections** | **[{str: (bool, date, datetime, dict, float, int, list, str, none_type)}]** |  | [optional] [readonly] 
**cluster_id** | **str** |  | [optional] [readonly] 
**user_permissions** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** |  | [optional] [readonly] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


