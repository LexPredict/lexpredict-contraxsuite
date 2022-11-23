

# DocumentTypeDetailFieldsDataInner


## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**uid** | **UUID** |  |  [optional] [readonly] |
|**documentType** | **String** |  |  |
|**documentTypeTitle** | **String** |  |  [optional] [readonly] |
|**code** | **String** | Field codes must be lowercase, should start with  a Latin letter, and contain only Latin letters, digits, underscores. Field codes must be unique to every Document Type. |  |
|**longCode** | **String** |  |  [optional] |
|**title** | **String** |  |  |
|**description** | **String** |  |  [optional] |
|**type** | [**TypeEnum**](#TypeEnum) |  |  [optional] |
|**textUnitType** | [**TextUnitTypeEnum**](#TextUnitTypeEnum) |  |  [optional] |
|**valueDetectionStrategy** | [**ValueDetectionStrategyEnum**](#ValueDetectionStrategyEnum) |  |  [optional] |
|**classifierInitScript** | **String** |  |  [optional] |
|**formula** | **String** |  |  [optional] |
|**convertDecimalsToFloatsInFormulaArgs** | **Boolean** | Floating point field values      are represented in Python Decimal type to avoid rounding problems in machine numbers representations.      Use this checkbox for converting them to Python float type before calculating the formula.      Float: 0.1 + 0.2 &#x3D; 0.30000000000000004. Decimal: 0.1 + 0.2 &#x3D; 0.3. |  [optional] |
|**valueRegexp** | **String** | This regular expression is run on the sentence      found by a Field Detector and extracts a specific string value from a Text Unit. If the regular expression returns multiple matching groups, then the first matching group will be used by the Field. This is only applicable to String Fields. |  [optional] |
|**dependsOnFields** | **List&lt;UUID&gt;** |  |  [optional] [readonly] |
|**valueDetectionStrategyName** | **String** |  |  [optional] [readonly] |
|**confidence** | [**ConfidenceEnum**](#ConfidenceEnum) |  |  [optional] |
|**requiresTextAnnotations** | **Boolean** |  |  [optional] |
|**readOnly** | **Boolean** |  |  [optional] |
|**category** | [**DocumentFieldListCategory**](DocumentFieldListCategory.md) |  |  [optional] |
|**family** | **Integer** |  |  [optional] |
|**defaultValue** | **Object** | If populated, the Default Value will be displayed for this Field if no other value is found by the chosen Value Detection Strategy. Leave this form blank to have the Field Value remain empty by default. Please wrap entries with quotes, example: “landlord”. This is only applicable to Choice and Multi Choice Fields. |  [optional] |
|**choices** | **List&lt;String&gt;** |  |  [optional] [readonly] |
|**allowValuesNotSpecifiedInChoices** | **Boolean** |  |  [optional] |
|**metadata** | **Object** |  |  [optional] |
|**trainingFinished** | **Boolean** |  |  [optional] |
|**dirty** | **Boolean** |  |  [optional] |
|**order** | **Integer** |  |  [optional] |
|**trainedAfterDocumentsNumber** | **Integer** |  |  [optional] |
|**hiddenAlways** | **Boolean** |  |  [optional] |
|**hideUntilPython** | **String** |  |  [optional] |
|**hideUntilJs** | **String** |  |  [optional] |
|**isValueDetectionStrategyDisabled** | **Boolean** |  |  [optional] [readonly] |
|**displayYesNo** | **Boolean** | Checking this box will      display “Yes” if Related Info text is found, and display “No” if no text is found. |  [optional] |
|**valueAware** | **Boolean** |  |  [optional] [readonly] |
|**createdByName** | **String** |  |  [optional] [readonly] |
|**modifiedByName** | **String** |  |  [optional] [readonly] |
|**createdDate** | **OffsetDateTime** |  |  [optional] [readonly] |
|**modifiedDate** | **OffsetDateTime** |  |  [optional] [readonly] |
|**vectorizerStopWords** | **String** | Stop words for vectorizers      user in field-based ML field detection. These stop words are excluded from going into the feature vector part      build based on this field. In addition to these words the standard sklearn \&quot;english\&quot; word list is used.      Format: each word on new line |  [optional] |
|**unsureChoiceValue** | **String** | Makes sense for machine learning      strategies with \&quot;Unsure\&quot; category. The strategy will return this value if probabilities of all other categories      appear lower than the specified threshold. |  [optional] |
|**unsureThresholdsByValue** | **Object** | Makes sense for machine learning      strategies with \&quot;Unsure\&quot; category. The strategy will return concrete result (one of choice values) only if      the probability of the detected value is greater than this threshold. Otherwise the strategy returns None      or the choice value specified in \&quot;Unsure choice value\&quot; field. Format: { \&quot;value1\&quot;: 0.9, \&quot;value2\&quot;: 0.5, ...}.      Default: 0.9 |  [optional] |
|**mlflowModelUri** | **String** | MLFlow model URI      understandable by the MLFlow artifact downloading routines. |  [optional] |
|**mlflowDetectOnDocumentLevel** | **Boolean** | If true - whole      document text will be sent to the MLFlow model and the field value will be returned for the whole text with no     annotations. If false - each text unit will be sent separately. |  [optional] |



## Enum: TypeEnum

| Name | Value |
|---- | -----|
| ADDRESS | &quot;address&quot; |
| CHOICE | &quot;choice&quot; |
| COMPANY | &quot;company&quot; |
| DATE | &quot;date&quot; |
| DATE_RECURRING | &quot;date_recurring&quot; |
| DATETIME | &quot;datetime&quot; |
| DURATION | &quot;duration&quot; |
| FLOAT | &quot;float&quot; |
| GEOGRAPHY | &quot;geography&quot; |
| INT | &quot;int&quot; |
| LINKED_DOCUMENTS | &quot;linked_documents&quot; |
| MONEY | &quot;money&quot; |
| MULTI_CHOICE | &quot;multi_choice&quot; |
| PERCENT | &quot;percent&quot; |
| PERSON | &quot;person&quot; |
| RATIO | &quot;ratio&quot; |
| RELATED_INFO | &quot;related_info&quot; |
| STRING | &quot;string&quot; |
| STRING_NO_WORD_WRAP | &quot;string_no_word_wrap&quot; |
| TEXT | &quot;text&quot; |



## Enum: TextUnitTypeEnum

| Name | Value |
|---- | -----|
| SENTENCE | &quot;sentence&quot; |
| PARAGRAPH | &quot;paragraph&quot; |
| SECTION | &quot;section&quot; |



## Enum: ValueDetectionStrategyEnum

| Name | Value |
|---- | -----|
| DISABLED | &quot;disabled&quot; |
| USE_REGEXPS_ONLY | &quot;use_regexps_only&quot; |
| USE_FORMULA_ONLY | &quot;use_formula_only&quot; |
| REGEXP_TABLE | &quot;regexp_table&quot; |
| TEXT_BASED_ML_ONLY | &quot;text_based_ml_only&quot; |
| FIELDS_BASED_ML_ONLY | &quot;fields_based_ml_only&quot; |
| FIELDS_BASED_PROB_ML_ONLY | &quot;fields_based_prob_ml_only&quot; |
| FIELD_BASED_REGEXPS | &quot;field_based_regexps&quot; |
| MLFLOW_MODEL | &quot;mlflow_model&quot; |



## Enum: ConfidenceEnum

| Name | Value |
|---- | -----|
| HIGH | &quot;High&quot; |
| MEDIUM | &quot;Medium&quot; |
| LOW | &quot;Low&quot; |


