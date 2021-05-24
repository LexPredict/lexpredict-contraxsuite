

# DocumentSimilarityByFeaturesForm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**runName** | **String** |  |  [optional]
**similarityThreshold** | **Integer** | Min. Similarity Value 50-100% |  [optional]
**project** | **Integer** |  | 
**featureSource** | [**FeatureSourceEnum**](#FeatureSourceEnum) | Cluster by terms, parties or other fields. |  [optional]
**distanceType** | [**DistanceTypeEnum**](#DistanceTypeEnum) |  |  [optional]
**itemId** | **Integer** | Optional. Search similar for one concrete document |  [optional]
**createReverseRelations** | **Boolean** |  |  [optional]
**useTfidf** | **Boolean** |  |  [optional]
**delete** | **Boolean** |  |  [optional]



## Enum: FeatureSourceEnum

Name | Value
---- | -----
DATE | &quot;date&quot;
DEFINITION | &quot;definition&quot;
DURATION | &quot;duration&quot;
COURT | &quot;court&quot;
CURRENCY_NAME | &quot;currency_name&quot;
CURRENCY_VALUE | &quot;currency_value&quot;
TERM | &quot;term&quot;
PARTY | &quot;party&quot;
GEOENTITY | &quot;geoentity&quot;



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



