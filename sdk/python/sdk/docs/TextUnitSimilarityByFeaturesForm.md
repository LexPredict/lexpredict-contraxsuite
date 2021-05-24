# TextUnitSimilarityByFeaturesForm


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project** | **int** |  | 
**run_name** | **str, none_type** |  | [optional] 
**similarity_threshold** | **int, none_type** | Min. Similarity Value 50-100% | [optional]  if omitted the server will use the default value of 75
**feature_source** | **str, none_type** | Cluster by terms, parties or other fields. | [optional]  if omitted the server will use the default value of "term"
**distance_type** | **str, none_type** |  | [optional]  if omitted the server will use the default value of "cosine"
**item_id** | **int, none_type** | Optional. Search similar for one concrete text unit. | [optional] 
**create_reverse_relations** | **bool, none_type** |  | [optional] 
**use_tfidf** | **bool, none_type** |  | [optional] 
**delete** | **bool, none_type** |  | [optional] 
**unit_type** | **str, none_type** |  | [optional]  if omitted the server will use the default value of "sentence"

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


