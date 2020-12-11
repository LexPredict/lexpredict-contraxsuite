

# DocumentTypeCreate

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uid** | [**UUID**](UUID.md) |  |  [optional] [readonly]
**title** | **String** |  | 
**code** | **String** | Field codes must be lowercase, should start with a Latin letter, and contain  only Latin letters, digits, and underscores. | 
**categories** | [**List&lt;DocumentTypeDetailCategories&gt;**](DocumentTypeDetailCategories.md) |  |  [optional] [readonly]
**managers** | **List&lt;Integer&gt;** |  |  [optional]
**fields** | [**List&lt;DocumentFieldCategoryListFields&gt;**](DocumentFieldCategoryListFields.md) |  |  [optional] [readonly]
**searchFields** | **List&lt;String&gt;** |  |  [optional]
**editorType** | [**EditorTypeEnum**](#EditorTypeEnum) |  |  [optional]
**fieldCodeAliases** | **Object** |  |  [optional]
**metadata** | **Object** |  |  [optional]
**warningMessage** | **String** |  |  [optional] [readonly]



## Enum: EditorTypeEnum

Name | Value
---- | -----
SAVE_BY_FIELD | &quot;save_by_field&quot;
SAVE_ALL_FIELDS_AT_ONCE | &quot;save_all_fields_at_once&quot;
NO_TEXT | &quot;no_text&quot;



