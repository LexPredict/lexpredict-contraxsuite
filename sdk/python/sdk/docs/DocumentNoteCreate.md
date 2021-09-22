# DocumentNoteCreate


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**note** | **str** |  | 
**document_id** | **int** |  | 
**pk** | **int** |  | [optional] [readonly] 
**timestamp** | **datetime** |  | [optional] [readonly] 
**location_start** | **int, none_type** |  | [optional] 
**location_end** | **int, none_type** |  | [optional] 
**field_value_id** | **int** |  | [optional] 
**field_id** | **str** |  | [optional] 
**user_id** | **str** |  | [optional] [readonly] 
**username** | **str, none_type** |  | [optional] 
**user** | [**DocumentNoteDetailUser**](DocumentNoteDetailUser.md) |  | [optional] 
**selections** | **[{str: (bool, date, datetime, dict, float, int, list, str, none_type)}]** |  | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


