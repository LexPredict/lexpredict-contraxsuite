

# DocumentTypeDetail


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uid** | **UUID** |  |  [optional] [readonly]
**title** | **String** |  | 
**code** | **String** | Field codes must be lowercase, should start with a Latin letter, and contain  only Latin letters, digits, and underscores. | 
**fieldsData** | [**List&lt;DocumentTypeDetailFieldsData&gt;**](DocumentTypeDetailFieldsData.md) |  |  [optional] [readonly]
**searchFields** | **List&lt;String&gt;** |  |  [optional]
**editorType** | [**EditorTypeEnum**](#EditorTypeEnum) |  |  [optional]
**createdByName** | **String** |  | 
**createdDate** | **OffsetDateTime** |  |  [optional] [readonly]
**modifiedByName** | **String** |  | 
**modifiedDate** | **OffsetDateTime** |  |  [optional] [readonly]
**metadata** | **Object** |  |  [optional]
**fieldsNumber** | **Integer** |  | 
**categories** | [**List&lt;DocumentTypeDetailCategories&gt;**](DocumentTypeDetailCategories.md) |  |  [optional] [readonly]
**managers** | **List&lt;Integer&gt;** | Choose which users can modify this Document Type. Users chosen as Managers can be of any System-Level Permission. |  [optional]



## Enum: EditorTypeEnum

Name | Value
---- | -----
BY_FIELD | &quot;save_by_field&quot;
ALL_FIELDS_AT_ONCE | &quot;save_all_fields_at_once&quot;



