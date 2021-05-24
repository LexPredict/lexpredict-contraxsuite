

# ProjectSearchSimilarTextUnitsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**runName** | **String** |  |  [optional]
**distanceType** | [**DistanceTypeEnum**](#DistanceTypeEnum) |  |  [optional]
**similarityThreshold** | **Integer** |  |  [optional]
**createReverseRelations** | **Boolean** |  |  [optional]
**useTfidf** | **Boolean** |  |  [optional]
**delete** | **Boolean** |  |  [optional]
**itemId** | **Integer** |  |  [optional]
**unitType** | [**UnitTypeEnum**](#UnitTypeEnum) |  |  [optional]
**documentId** | **Integer** |  |  [optional]
**locationStart** | **Integer** |  |  [optional]
**locationEnd** | **Integer** |  |  [optional]



## Enum: DistanceTypeEnum

Name | Value
---- | -----
BRAYCURTIS | &quot;braycurtis&quot;
CANBERRA | &quot;canberra&quot;
CHEBYSHEV | &quot;chebyshev&quot;
CITYBLOCK | &quot;cityblock&quot;
CORRELATION | &quot;correlation&quot;
COSINE | &quot;cosine&quot;
DICE | &quot;dice&quot;
EUCLIDEAN | &quot;euclidean&quot;
HAMMING | &quot;hamming&quot;
JACCARD | &quot;jaccard&quot;
JENSENSHANNON | &quot;jensenshannon&quot;
KULSINSKI | &quot;kulsinski&quot;
MAHALANOBIS | &quot;mahalanobis&quot;
MINKOWSKI | &quot;minkowski&quot;
ROGERSTANIMOTO | &quot;rogerstanimoto&quot;
RUSSELLRAO | &quot;russellrao&quot;
SEUCLIDEAN | &quot;seuclidean&quot;
SOKALMICHENER | &quot;sokalmichener&quot;
SOKALSNEATH | &quot;sokalsneath&quot;
SQEUCLIDEAN | &quot;sqeuclidean&quot;
WMINKOWSKI | &quot;wminkowski&quot;
YULE | &quot;yule&quot;



## Enum: UnitTypeEnum

Name | Value
---- | -----
SENTENCE | &quot;sentence&quot;
PARAGRAPH | &quot;paragraph&quot;



