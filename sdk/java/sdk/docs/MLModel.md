

# MLModel


## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**id** | **Integer** |  |  [optional] [readonly] |
|**name** | **String** | Model name, may include module parameters |  |
|**version** | **String** | Model version |  |
|**vectorName** | **String** |  |  [optional] |
|**modelPath** | **String** | Model path, relative to WebDAV root folder |  |
|**isActive** | **Boolean** | Inactive models are ignored |  [optional] |
|**_default** | **Boolean** | The default model is used unless another model is deliberately selected |  [optional] |
|**applyTo** | [**ApplyToEnum**](#ApplyToEnum) | Should the model be applied to documents or text units |  |
|**targetEntity** | [**TargetEntityEnum**](#TargetEntityEnum) | The model class |  |
|**language** | **String** | Language (ISO 693-1) code, may be omitted |  |
|**textUnitType** | [**TextUnitTypeEnum**](#TextUnitTypeEnum) | Text unit type: sentence or paragraph |  [optional] |
|**codebaseVersion** | **String** | ContraxSuite version in which the model was created |  [optional] |
|**userModified** | **Boolean** | User modified models are not automatically updated |  [optional] |
|**project** | **Integer** | Optional project reference |  [optional] |



## Enum: ApplyToEnum

| Name | Value |
|---- | -----|
| DOCUMENT | &quot;document&quot; |
| TEXT_UNIT | &quot;text_unit&quot; |



## Enum: TargetEntityEnum

| Name | Value |
|---- | -----|
| TRANSFORMER | &quot;transformer&quot; |
| CLASSIFIER | &quot;classifier&quot; |
| CONTRACT_TYPE_CLASSIFIER | &quot;contract_type_classifier&quot; |
| IS_CONTRACT | &quot;is_contract&quot; |



## Enum: TextUnitTypeEnum

| Name | Value |
|---- | -----|
| SENTENCE | &quot;sentence&quot; |
| PARAGRAPH | &quot;paragraph&quot; |



