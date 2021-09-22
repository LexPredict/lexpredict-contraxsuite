

# WebNotificationDetailNotification


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **Integer** |  |  [optional] [readonly]
**messageData** | **Object** |  |  [optional]
**messageTemplate** | **String** |  |  [optional] [readonly]
**createdDate** | **OffsetDateTime** |  |  [optional] [readonly]
**notificationType** | [**NotificationTypeEnum**](#NotificationTypeEnum) | Notification type |  [optional]
**redirectLink** | **Object** |  |  [optional]



## Enum: NotificationTypeEnum

Name | Value
---- | -----
DOCUMENT_ASSIGNED | &quot;DOCUMENT_ASSIGNED&quot;
DOCUMENT_UNASSIGNED | &quot;DOCUMENT_UNASSIGNED&quot;
CLAUSES_ASSIGNED | &quot;CLAUSES_ASSIGNED&quot;
CLAUSES_UNASSIGNED | &quot;CLAUSES_UNASSIGNED&quot;
DOCUMENTS_UPLOADED | &quot;DOCUMENTS_UPLOADED&quot;
DOCUMENT_DELETED | &quot;DOCUMENT_DELETED&quot;
DOCUMENT_ADDED | &quot;DOCUMENT_ADDED&quot;
DOCUMENT_STATUS_CHANGED | &quot;DOCUMENT_STATUS_CHANGED&quot;
CLUSTER_IMPORTED | &quot;CLUSTER_IMPORTED&quot;
FIELD_VALUE_DETECTION_COMPLETED | &quot;FIELD_VALUE_DETECTION_COMPLETED&quot;
CUSTOM_TERM_SET_SEARCH_FINISHED | &quot;CUSTOM_TERM_SET_SEARCH_FINISHED&quot;
CUSTOM_COMPANY_TYPE_SEARCH_FINISHED | &quot;CUSTOM_COMPANY_TYPE_SEARCH_FINISHED&quot;
DOCUMENT_SIMILARITY_SEARCH_FINISHED | &quot;DOCUMENT_SIMILARITY_SEARCH_FINISHED&quot;
TEXT_UNIT_SIMILARITY_SEARCH_FINISHED | &quot;TEXT_UNIT_SIMILARITY_SEARCH_FINISHED&quot;



