

# DocumentTypeCreate


## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**uid** | **UUID** |  |  [optional] [readonly] |
|**title** | **String** |  |  |
|**code** | **String** | Field codes must be lowercase, should start with a Latin letter, and contain  only Latin letters, digits, and underscores. |  |
|**categories** | [**List&lt;DocumentTypeDetailCategoriesInner&gt;**](DocumentTypeDetailCategoriesInner.md) |  |  [optional] [readonly] |
|**managers** | **List&lt;Integer&gt;** | Choose which users can modify this Document Type. Users chosen as Managers can be of any System-Level Permission. |  [optional] |
|**fields** | [**List&lt;DocumentFieldCategoryListFieldsInner&gt;**](DocumentFieldCategoryListFieldsInner.md) |  |  [optional] [readonly] |
|**searchFields** | **List&lt;String&gt;** |  |  [optional] |
|**editorType** | [**EditorTypeEnum**](#EditorTypeEnum) |  |  |
|**fieldCodeAliases** | **Object** |  |  [optional] |
|**metadata** | **Object** |  |  [optional] |
|**warningMessage** | **String** |  |  [optional] [readonly] |



## Enum: EditorTypeEnum

| Name | Value |
|---- | -----|
| BY_FIELD | &quot;save_by_field&quot; |
| ALL_FIELDS_AT_ONCE | &quot;save_all_fields_at_once&quot; |



