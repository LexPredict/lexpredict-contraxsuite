
# Org.OpenAPITools.Model.MLModel

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **int** |  | [optional] [readonly] 
**Name** | **string** | Model name, may include module parameters | 
**Version** | **string** | Model version | 
**VectorName** | **string** |  | [optional] 
**ModelPath** | **string** | Model path, relative to WebDAV root folder | 
**IsActive** | **bool** | Inactive models are ignored | [optional] 
**Default** | **bool** | The default model is used unless another model is deliberately selected | [optional] 
**ApplyTo** | **string** | Should the model be applied to documents or text units | 
**TargetEntity** | **string** | The model class | 
**Language** | **string** | Language (ISO 693-1) code, may be omitted | 
**TextUnitType** | **string** | Text unit type: sentence or paragraph | [optional] 
**Project** | **int?** | Optional project reference | [optional] 

[[Back to Model list]](../README.md#documentation-for-models)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to README]](../README.md)

