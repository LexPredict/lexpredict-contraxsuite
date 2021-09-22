# UserProfile


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**username** | **str** | Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. | [optional] [readonly] 
**last_name** | **str** |  | [optional] 
**first_name** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**initials** | **str** |  | [optional] [readonly] 
**photo** | **file_type, none_type** |  | [optional] 
**email** | **str** |  | [optional] [readonly] 
**organization** | **str, none_type** |  | [optional] 
**groups** | **[int]** | The groups this user belongs to. A user will get all permissions granted to each of their groups. | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


