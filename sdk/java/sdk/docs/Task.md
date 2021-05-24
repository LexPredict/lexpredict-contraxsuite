

# Task


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**pk** | **String** |  |  [optional]
**name** | **String** |  |  [optional]
**dateStart** | **OffsetDateTime** |  |  [optional]
**dateWorkStart** | **OffsetDateTime** |  |  [optional]
**userUsername** | **String** |  |  [optional] [readonly]
**dateDone** | **OffsetDateTime** |  |  [optional]
**duration** | **String** |  |  [optional] [readonly]
**progress** | **Integer** |  |  [optional]
**status** | [**StatusEnum**](#StatusEnum) |  |  [optional]
**hasError** | **String** |  |  [optional] [readonly]
**description** | **String** |  |  [optional] [readonly]



## Enum: StatusEnum

Name | Value
---- | -----
FAILURE | &quot;FAILURE&quot;
PENDING | &quot;PENDING&quot;
RECEIVED | &quot;RECEIVED&quot;
RETRY | &quot;RETRY&quot;
REVOKED | &quot;REVOKED&quot;
STARTED | &quot;STARTED&quot;
SUCCESS | &quot;SUCCESS&quot;



