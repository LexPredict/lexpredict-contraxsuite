# ProjectSearchSimilarTextUnitsRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**run_name** | **str** |  | [optional] 
**distance_type** | **str** |  | [optional]  if omitted the server will use the default value of "cosine"
**similarity_threshold** | **int** |  | [optional]  if omitted the server will use the default value of 75
**create_reverse_relations** | **bool** |  | [optional]  if omitted the server will use the default value of True
**use_tfidf** | **bool** |  | [optional]  if omitted the server will use the default value of False
**delete** | **bool** |  | [optional]  if omitted the server will use the default value of True
**item_id** | **int** |  | [optional] 
**unit_type** | **str** |  | [optional]  if omitted the server will use the default value of "sentence"
**document_id** | **int** |  | [optional] 
**location_start** | **int** |  | [optional] 
**location_end** | **int** |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


