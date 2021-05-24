# MLModel


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Model name, may include module parameters | 
**version** | **str** | Model version | 
**model_path** | **str** | Model path, relative to WebDAV root folder | 
**apply_to** | **str, none_type** | Should the model be applied to documents or text units | 
**target_entity** | **str, none_type** | The model class | 
**language** | **str, none_type** | Language (ISO 693-1) code, may be omitted | 
**id** | **int** |  | [optional] [readonly] 
**vector_name** | **str, none_type** |  | [optional] 
**is_active** | **bool** | Inactive models are ignored | [optional] 
**default** | **bool** | The default model is used unless another model is deliberately selected | [optional] 
**text_unit_type** | **str, none_type** | Text unit type: sentence or paragraph | [optional] 
**project** | **int, none_type** | Optional project reference | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


