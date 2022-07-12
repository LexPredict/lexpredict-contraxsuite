

# ClusterProjectRequest


## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**nClusters** | **Integer** |  |  |
|**force** | **Boolean** |  |  [optional] |
|**clusterBy** | [**ClusterByEnum**](#ClusterByEnum) |  |  |
|**method** | [**MethodEnum**](#MethodEnum) |  |  |
|**requireConfirmation** | **Boolean** |  |  [optional] |



## Enum: ClusterByEnum

| Name | Value |
|---- | -----|
| TERM | &quot;term&quot; |
| DATE | &quot;date&quot; |
| TEXT | &quot;text&quot; |
| DEFINITION | &quot;definition&quot; |
| DURATION | &quot;duration&quot; |
| PARTY | &quot;party&quot; |
| GEOENTITY | &quot;geoentity&quot; |
| CURRENCY_NAME | &quot;currency_name&quot; |
| CURRENCY_VALUE | &quot;currency_value&quot; |



## Enum: MethodEnum

| Name | Value |
|---- | -----|
| KMEANS | &quot;kmeans&quot; |
| MINIBATCHKMEANS | &quot;minibatchkmeans&quot; |
| BIRCH | &quot;birch&quot; |



