

# DocumentTypeImportRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**file** | [**File**](File.md) |  | 
**updateCache** | **Boolean** |  |  [optional]
**action** | [**ActionEnum**](#ActionEnum) |  |  [optional]
**sourceVersion** | **String** |  |  [optional]



## Enum: ActionEnum

Name | Value
---- | -----
VALIDATE | &quot;validate&quot;
VALIDATE_IMPORT | &quot;validate|import&quot;
IMPORT_AUTO_FIX_RETAIN_MISSING_OBJECTS | &quot;import|auto_fix|retain_missing_objects&quot;
IMPORT_AUTO_FIX_REMOVE_MISSING_OBJECTS | &quot;import|auto_fix|remove_missing_objects&quot;



