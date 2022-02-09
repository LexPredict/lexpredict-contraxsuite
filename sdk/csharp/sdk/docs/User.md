
# Org.OpenAPITools.Model.User

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **int** |  | [optional] [readonly] 
**Uid** | **Guid** |  | [optional] [readonly] 
**Username** | **string** | Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. | 
**LastName** | **string** |  | [optional] 
**FirstName** | **string** |  | [optional] 
**Email** | **string** |  | 
**IsSuperuser** | **bool** | Designates that this user has all permissions without explicitly assigning them. | [optional] 
**IsStaff** | **bool** | Designates whether the user can log into this admin site. | [optional] 
**IsActive** | **bool** | Designates whether this user should be treated as active. Unselect this instead of deleting accounts. | [optional] 
**Name** | **string** |  | [optional] 
**Initials** | **string** |  | [optional] 
**Organization** | **string** |  | [optional] 
**Photo** | **string** |  | [optional] [readonly] 
**Permissions** | **Object** |  | [optional] [readonly] 
**Groups** | **List&lt;int&gt;** | The groups this user belongs to. A user will get all permissions granted to each of their groups. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to README]](../README.md)

