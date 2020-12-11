
# Org.OpenAPITools.Model.DocumentFieldList

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Uid** | **Guid** |  | [optional] [readonly] 
**DocumentType** | **string** |  | 
**Code** | **string** | Field codes must be lowercase, should start with  a Latin letter, and contain only Latin letters, digits, underscores. Field codes must be unique to every Document Type. | 
**LongCode** | **string** |  | [optional] 
**Title** | **string** |  | 
**Description** | **string** |  | [optional] 
**Type** | **string** |  | [optional] 
**TextUnitType** | **string** |  | [optional] 
**ValueDetectionStrategy** | **string** |  | [optional] 
**PythonCodedField** | **string** |  | [optional] 
**ClassifierInitScript** | **string** |  | [optional] 
**Formula** | **string** |  | [optional] 
**ConvertDecimalsToFloatsInFormulaArgs** | **bool** | Floating point field values      are represented in Python Decimal type to avoid rounding problems in machine numbers representations.      Use this checkbox for converting them to Python float type before calculating the formula.      Float: 0.1 + 0.2 &#x3D; 0.30000000000000004. Decimal: 0.1 + 0.2 &#x3D; 0.3. | [optional] 
**ValueRegexp** | **string** | This regular expression is run on the sentence      found by a Field Detector and extracts a specific string value from a Text Unit. The first matching group is used if      the regular expression returns multiple matching groups. This is only applicable to string fields. | [optional] 
**DependsOnFields** | **string** |  | [optional] [readonly] 
**Confidence** | **string** |  | [optional] 
**RequiresTextAnnotations** | **bool** |  | [optional] 
**ReadOnly** | **bool** |  | [optional] 
**Category** | [**DocumentFieldListCategory**](DocumentFieldListCategory.md) |  | [optional] 
**Family** | [**DocumentFieldListFamily**](DocumentFieldListFamily.md) |  | [optional] 
**DefaultValue** | **Object** | When populated, this      default value is displayed in the user interface’s annotator sidebar for the associated field. If not populated, the      Field Value remains empty by default. Please wrap entries with quotes, example: “landlord”. This is only applicable       to Choice and Multichoice fields. | [optional] 
**Choices** | **string** |  | [optional] [readonly] 
**AllowValuesNotSpecifiedInChoices** | **bool** |  | [optional] 
**StopWords** | **Object** |  | [optional] 
**Metadata** | **Object** |  | [optional] 
**TrainingFinished** | **bool** |  | [optional] 
**Dirty** | **bool** |  | [optional] 
**Order** | **int** |  | [optional] 
**TrainedAfterDocumentsNumber** | **int** |  | [optional] 
**HiddenAlways** | **bool** |  | [optional] 
**HideUntilPython** | **string** |  | [optional] 
**HideUntilJs** | **string** |  | [optional] 
**DetectLimitUnit** | **string** | Choose to add an upward limit to the amount of document text                                           ContraxSuite will search for this Document Field. For example, you can choose                                           to only search the first 10 paragraphs of text for the value required (this                                           often works best for values like “Company,” “Execution Date,” or “Parties,”                                          all of which typically appear in the first few paragraphs of a contract). | [optional] 
**DetectLimitCount** | **int** | Specify the maximum  range for a bounded search. Field detection begins at the top of the document and continues until this Nth  \&quot;Detect limit unit\&quot; element. | [optional] 
**DisplayYesNo** | **bool** | Checking this box will      display “Yes” if Related Info text is found, and display “No” if no text is found. | [optional] 
**ValueAware** | **string** |  | [optional] [readonly] 
**CreatedBy** | **int?** |  | [optional] 
**ModifiedBy** | **int?** |  | 
**CreatedDate** | **DateTime** |  | [optional] [readonly] 
**ModifiedDate** | **DateTime** |  | [optional] [readonly] 
**VectorizerStopWords** | **string** | Stop words for vectorizers      user in field-based ML field detection. These stop words are excluded from going into the feature vector part      build based on this field. In addition to these words the standard sklearn \&quot;english\&quot; word list is used.      Format: each word on new line | [optional] 
**UnsureChoiceValue** | **string** | Makes sense for machine learning      strategies with \&quot;Unsure\&quot; category. The strategy will return this value if probabilities of all other categories      appear lower than the specified threshold. | [optional] 
**UnsureThresholdsByValue** | **Object** | Makes sense for machine learning      strategies with \&quot;Unsure\&quot; category. The strategy will return concrete result (one of choice values) only if      the probability of the detected value is greater than this threshold. Otherwise the strategy returns None      or the choice value specified in \&quot;Unsure choice value\&quot; field. Format: { \&quot;value1\&quot;: 0.9, \&quot;value2\&quot;: 0.5, ...}.      Default: 0.9 | [optional] 
**MlflowModelUri** | **string** | MLFlow model URI      understandable by the MLFlow artifact downloading routines. | [optional] 
**MlflowDetectOnDocumentLevel** | **bool** | If true - whole      document text will be sent to the MLFlow model and the field value will be returned for the whole text with no     annotations. If false - each text unit will be sent separately. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models)
[[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to README]](../README.md)

