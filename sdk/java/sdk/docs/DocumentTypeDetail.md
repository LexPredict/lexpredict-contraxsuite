

# DocumentTypeDetail

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uid** | [**UUID**](UUID.md) |  |  [optional] [readonly]
**title** | **String** |  | 
**code** | **String** | Field codes must be lowercase, should start with a Latin letter, and contain  only Latin letters, digits, and underscores. | 
**fieldsData** | [**List&lt;DocumentTypeDetailFieldsData&gt;**](DocumentTypeDetailFieldsData.md) |  |  [optional] [readonly]
**searchFields** | **List&lt;String&gt;** |  |  [optional]
**modifiedByUsername** | **String** |  |  [optional] [readonly]
**editorType** | [**EditorTypeEnum**](#EditorTypeEnum) |  |  [optional]
**createdBy** | [**DocumentDetailAssigneeData**](DocumentDetailAssigneeData.md) |  | 
**createdDate** | [**OffsetDateTime**](OffsetDateTime.md) |  |  [optional] [readonly]
**modifiedBy** | [**DocumentDetailAssigneeData**](DocumentDetailAssigneeData.md) |  | 
**modifiedDate** | [**OffsetDateTime**](OffsetDateTime.md) |  |  [optional] [readonly]
**metadata** | **Object** |  |  [optional]
**fieldsNumber** | **Integer** |  | 
**categories** | [**List&lt;DocumentTypeDetailCategories&gt;**](DocumentTypeDetailCategories.md) |  |  [optional] [readonly]
**managers** | **List&lt;Integer&gt;** |  |  [optional]



## Enum: EditorTypeEnum

Name | Value
---- | -----
SAVE_BY_FIELD | &quot;save_by_field&quot;
SAVE_ALL_FIELDS_AT_ONCE | &quot;save_all_fields_at_once&quot;
NO_TEXT | &quot;no_text&quot;



