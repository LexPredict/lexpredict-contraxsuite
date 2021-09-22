# ProjectDocumentsSimilarityByVectorsForm


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**run_name** | **str, none_type** |  | [optional] 
**similarity_threshold** | **int, none_type** | Min. Similarity Value 50-100% | [optional]  if omitted the server will use the default value of 75
**project** | **int, none_type** | Project with Document Transformer trained model | [optional] 
**feature_source** | **str, none_type** |  | [optional]  if omitted the server will use the default value of "vector"
**distance_type** | **str, none_type** |  | [optional]  if omitted the server will use the default value of "cosine"
**item_id** | **int, none_type** | Optional. Search similar for one concrete document | [optional] 
**create_reverse_relations** | **bool, none_type** |  | [optional] 
**use_tfidf** | **bool, none_type** |  | [optional] 
**delete** | **bool, none_type** |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


