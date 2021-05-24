
# Org.OpenAPITools.Model.ProjectTextUnitsSimilarityByVectorsForm

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**RunName** | **string** |  | [optional] 
**SimilarityThreshold** | **int?** | Min. Similarity Value 50-100% | [optional] [default to 75]
**Project** | **int?** | Project with Text Unit Transformer trained model | [optional] 
**FeatureSource** | **string** |  | [optional] [default to "vector"]
**DistanceType** | **string** |  | [optional] [default to DistanceTypeEnum.Cosine]
**ItemId** | **int?** | Optional. Search similar for one concrete text unit. | [optional] 
**CreateReverseRelations** | **bool?** |  | [optional] 
**UseTfidf** | **bool?** |  | [optional] 
**Delete** | **bool?** |  | [optional] 
**UnitType** | **string** |  | [optional] [default to UnitTypeEnum.Sentence]
**DocumentId** | **int?** |  | [optional] 
**LocationStart** | **int?** |  | [optional] 
**LocationEnd** | **int?** |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to README]](../README.md)

