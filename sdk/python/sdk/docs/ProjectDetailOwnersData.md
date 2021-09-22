# ProjectDetailOwnersData


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**username** | **str** | Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. | 
**email** | **str** |  | 
**id** | **int** |  | [optional] [readonly] 
**last_name** | **str** |  | [optional] 
**first_name** | **str** |  | [optional] 
**is_superuser** | **bool** | Designates that this user has all permissions without explicitly assigning them. | [optional] 
**is_staff** | **bool** | Designates whether the user can log into this admin site. | [optional] 
**is_active** | **bool** | Designates whether this user should be treated as active. Unselect this instead of deleting accounts. | [optional] 
**name** | **str** |  | [optional] 
**initials** | **str** |  | [optional] 
**organization** | **str, none_type** |  | [optional] 
**photo** | **str** |  | [optional] [readonly] 
**permissions** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** |  | [optional] [readonly] 
**groups** | **[int]** | The groups this user belongs to. A user will get all permissions granted to each of their groups. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


