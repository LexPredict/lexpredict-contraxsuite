

# ProjectActiveTasksTasks


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **String** |  |  [optional]
**name** | **String** |  |  [optional]
**verboseName** | **String** |  | 
**userName** | **String** |  |  [optional] [readonly]
**worker** | **String** |  |  [optional]
**status** | [**StatusEnum**](#StatusEnum) |  |  [optional]
**progress** | **Integer** |  |  [optional]
**description** | **String** |  |  [optional] [readonly]
**dateStart** | **OffsetDateTime** |  | 
**dateWorkStart** | **OffsetDateTime** |  | 
**dateDone** | **OffsetDateTime** |  | 
**totalTime** | **String** |  | 
**workTime** | **String** |  | 



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



