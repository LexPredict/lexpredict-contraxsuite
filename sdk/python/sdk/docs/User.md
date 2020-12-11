# User

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] [readonly] 
**username** | **str** | Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. | 
**last_name** | **str** |  | [optional] 
**first_name** | **str** |  | [optional] 
**email** | **str** |  | [optional] 
**is_superuser** | **bool** | Designates that this user has all permissions without explicitly assigning them. | [optional] 
**is_staff** | **bool** | Designates whether the user can log into this admin site. | [optional] 
**is_active** | **bool** | Designates whether this user should be treated as active. Unselect this instead of deleting accounts. | [optional] 
**name** | **str** |  | [optional] 
**role** | **int** |  | [optional] 
**role_data** | [**ProjectDetailRoleData**](ProjectDetailRoleData.md) |  | [optional] 
**organization** | **str** |  | [optional] 
**photo** | **str** |  | [optional] [readonly] 
**permissions** | **object** |  | [optional] [readonly] 
**groups** | **list[int]** | The groups this user belongs to. A user will get all permissions granted to each of their groups. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


