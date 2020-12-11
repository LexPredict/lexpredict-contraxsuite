

# DocumentFieldList

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uid** | [**UUID**](UUID.md) |  |  [optional] [readonly]
**documentType** | **String** |  | 
**code** | **String** | Field codes must be lowercase, should start with  a Latin letter, and contain only Latin letters, digits, underscores. Field codes must be unique to every Document Type. | 
**longCode** | **String** |  |  [optional]
**title** | **String** |  | 
**description** | **String** |  |  [optional]
**type** | [**TypeEnum**](#TypeEnum) |  |  [optional]
**textUnitType** | [**TextUnitTypeEnum**](#TextUnitTypeEnum) |  |  [optional]
**valueDetectionStrategy** | [**ValueDetectionStrategyEnum**](#ValueDetectionStrategyEnum) |  |  [optional]
**pythonCodedField** | [**PythonCodedFieldEnum**](#PythonCodedFieldEnum) |  |  [optional]
**classifierInitScript** | **String** |  |  [optional]
**formula** | **String** |  |  [optional]
**convertDecimalsToFloatsInFormulaArgs** | **Boolean** | Floating point field values      are represented in Python Decimal type to avoid rounding problems in machine numbers representations.      Use this checkbox for converting them to Python float type before calculating the formula.      Float: 0.1 + 0.2 &#x3D; 0.30000000000000004. Decimal: 0.1 + 0.2 &#x3D; 0.3. |  [optional]
**valueRegexp** | **String** | This regular expression is run on the sentence      found by a Field Detector and extracts a specific string value from a Text Unit. The first matching group is used if      the regular expression returns multiple matching groups. This is only applicable to string fields. |  [optional]
**dependsOnFields** | **String** |  |  [optional] [readonly]
**confidence** | [**ConfidenceEnum**](#ConfidenceEnum) |  |  [optional]
**requiresTextAnnotations** | **Boolean** |  |  [optional]
**readOnly** | **Boolean** |  |  [optional]
**category** | [**DocumentFieldListCategory**](DocumentFieldListCategory.md) |  |  [optional]
**family** | [**DocumentFieldListFamily**](DocumentFieldListFamily.md) |  |  [optional]
**defaultValue** | **Object** | When populated, this      default value is displayed in the user interface’s annotator sidebar for the associated field. If not populated, the      Field Value remains empty by default. Please wrap entries with quotes, example: “landlord”. This is only applicable       to Choice and Multichoice fields. |  [optional]
**choices** | **String** |  |  [optional] [readonly]
**allowValuesNotSpecifiedInChoices** | **Boolean** |  |  [optional]
**stopWords** | **Object** |  |  [optional]
**metadata** | **Object** |  |  [optional]
**trainingFinished** | **Boolean** |  |  [optional]
**dirty** | **Boolean** |  |  [optional]
**order** | **Integer** |  |  [optional]
**trainedAfterDocumentsNumber** | **Integer** |  |  [optional]
**hiddenAlways** | **Boolean** |  |  [optional]
**hideUntilPython** | **String** |  |  [optional]
**hideUntilJs** | **String** |  |  [optional]
**detectLimitUnit** | [**DetectLimitUnitEnum**](#DetectLimitUnitEnum) | Choose to add an upward limit to the amount of document text                                           ContraxSuite will search for this Document Field. For example, you can choose                                           to only search the first 10 paragraphs of text for the value required (this                                           often works best for values like “Company,” “Execution Date,” or “Parties,”                                          all of which typically appear in the first few paragraphs of a contract). |  [optional]
**detectLimitCount** | **Integer** | Specify the maximum  range for a bounded search. Field detection begins at the top of the document and continues until this Nth  \&quot;Detect limit unit\&quot; element. |  [optional]
**displayYesNo** | **Boolean** | Checking this box will      display “Yes” if Related Info text is found, and display “No” if no text is found. |  [optional]
**valueAware** | **String** |  |  [optional] [readonly]
**createdBy** | **Integer** |  |  [optional]
**modifiedBy** | **Integer** |  | 
**createdDate** | [**OffsetDateTime**](OffsetDateTime.md) |  |  [optional] [readonly]
**modifiedDate** | [**OffsetDateTime**](OffsetDateTime.md) |  |  [optional] [readonly]
**vectorizerStopWords** | **String** | Stop words for vectorizers      user in field-based ML field detection. These stop words are excluded from going into the feature vector part      build based on this field. In addition to these words the standard sklearn \&quot;english\&quot; word list is used.      Format: each word on new line |  [optional]
**unsureChoiceValue** | **String** | Makes sense for machine learning      strategies with \&quot;Unsure\&quot; category. The strategy will return this value if probabilities of all other categories      appear lower than the specified threshold. |  [optional]
**unsureThresholdsByValue** | **Object** | Makes sense for machine learning      strategies with \&quot;Unsure\&quot; category. The strategy will return concrete result (one of choice values) only if      the probability of the detected value is greater than this threshold. Otherwise the strategy returns None      or the choice value specified in \&quot;Unsure choice value\&quot; field. Format: { \&quot;value1\&quot;: 0.9, \&quot;value2\&quot;: 0.5, ...}.      Default: 0.9 |  [optional]
**mlflowModelUri** | **String** | MLFlow model URI      understandable by the MLFlow artifact downloading routines. |  [optional]
**mlflowDetectOnDocumentLevel** | **Boolean** | If true - whole      document text will be sent to the MLFlow model and the field value will be returned for the whole text with no     annotations. If false - each text unit will be sent separately. |  [optional]



## Enum: TypeEnum

Name | Value
---- | -----
ADDRESS | &quot;address&quot;
AMOUNT | &quot;amount&quot;
BOOLEAN | &quot;boolean&quot;
CHOICE | &quot;choice&quot;
COMPANY | &quot;company&quot;
DATE | &quot;date&quot;
DATE_RECURRING | &quot;date_recurring&quot;
DATETIME | &quot;datetime&quot;
DURATION | &quot;duration&quot;
FLOAT | &quot;float&quot;
GEOGRAPHY | &quot;geography&quot;
INT | &quot;int&quot;
LINKED_DOCUMENTS | &quot;linked_documents&quot;
MONEY | &quot;money&quot;
MULTI_CHOICE | &quot;multi_choice&quot;
PERCENT | &quot;percent&quot;
PERSON | &quot;person&quot;
RATIO | &quot;ratio&quot;
RELATED_INFO | &quot;related_info&quot;
STRING | &quot;string&quot;
STRING_NO_WORD_WRAP | &quot;string_no_word_wrap&quot;
TEXT | &quot;text&quot;



## Enum: TextUnitTypeEnum

Name | Value
---- | -----
SENTENCE | &quot;sentence&quot;
PARAGRAPH | &quot;paragraph&quot;
SECTION | &quot;section&quot;



## Enum: ValueDetectionStrategyEnum

Name | Value
---- | -----
DISABLED | &quot;disabled&quot;
USE_REGEXPS_ONLY | &quot;use_regexps_only&quot;
REGEXP_TABLE | &quot;regexp_table&quot;
USE_FORMULA_ONLY | &quot;use_formula_only&quot;
REGEXPS_AND_TEXT_BASED_ML | &quot;regexps_and_text_based_ml&quot;
TEXT_BASED_ML_ONLY | &quot;text_based_ml_only&quot;
FORMULA_AND_FIELDS_BASED_ML | &quot;formula_and_fields_based_ml&quot;
FIELDS_BASED_ML_ONLY | &quot;fields_based_ml_only&quot;
FIELDS_BASED_PROB_ML_ONLY | &quot;fields_based_prob_ml_only&quot;
PYTHON_CODED_FIELD | &quot;python_coded_field&quot;
FIELD_BASED_REGEXPS | &quot;field_based_regexps&quot;
MLFLOW_MODEL | &quot;mlflow_model&quot;



## Enum: PythonCodedFieldEnum

Name | Value
---- | -----
GENERIC_EARLIESTDATE | &quot;generic.EarliestDate&quot;
GENERIC_LATESTDATE | &quot;generic.LatestDate&quot;
GENERIC_MAXCURRENCY | &quot;generic.MaxCurrency&quot;
GENERIC_PARTIES | &quot;generic.Parties&quot;
SIMILARITY_SIMILARDOCUMENTS | &quot;similarity.SimilarDocuments&quot;



## Enum: ConfidenceEnum

Name | Value
---- | -----
HIGH | &quot;High&quot;
MEDIUM | &quot;Medium&quot;
LOW | &quot;Low&quot;



## Enum: DetectLimitUnitEnum

Name | Value
---- | -----
NONE | &quot;NONE&quot;
UNIT | &quot;UNIT&quot;



