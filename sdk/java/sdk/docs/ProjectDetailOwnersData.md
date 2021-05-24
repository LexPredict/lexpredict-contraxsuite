

# ProjectDetailOwnersData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **Integer** |  |  [optional] [readonly]
**username** | **String** | Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. | 
**lastName** | **String** |  |  [optional]
**firstName** | **String** |  |  [optional]
**email** | **String** |  | 
**isSuperuser** | **Boolean** | Designates that this user has all permissions without explicitly assigning them. |  [optional]
**isStaff** | **Boolean** | Designates whether the user can log into this admin site. |  [optional]
**isActive** | **Boolean** | Designates whether this user should be treated as active. Unselect this instead of deleting accounts. |  [optional]
**name** | **String** |  |  [optional]
**organization** | **String** |  |  [optional]
**photo** | **String** |  |  [optional] [readonly]
**permissions** | **Object** |  |  [optional] [readonly]
**groups** | **List&lt;Integer&gt;** | The groups this user belongs to. A user will get all permissions granted to each of their groups. |  [optional]



