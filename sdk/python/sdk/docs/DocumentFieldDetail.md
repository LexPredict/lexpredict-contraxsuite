# DocumentFieldDetail

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uid** | **str** |  | [optional] [readonly] 
**document_type** | **str** |  | 
**code** | **str** | Field codes must be lowercase, should start with  a Latin letter, and contain only Latin letters, digits, underscores. Field codes must be unique to every Document Type. | 
**long_code** | **str** |  | [optional] 
**title** | **str** |  | 
**description** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**text_unit_type** | **str** |  | [optional] 
**value_detection_strategy** | **str** |  | [optional] 
**python_coded_field** | **str** |  | [optional] 
**classifier_init_script** | **str** |  | [optional] 
**formula** | **str** |  | [optional] 
**convert_decimals_to_floats_in_formula_args** | **bool** | Floating point field values      are represented in Python Decimal type to avoid rounding problems in machine numbers representations.      Use this checkbox for converting them to Python float type before calculating the formula.      Float: 0.1 + 0.2 &#x3D; 0.30000000000000004. Decimal: 0.1 + 0.2 &#x3D; 0.3. | [optional] 
**value_regexp** | **str** | This regular expression is run on the sentence      found by a Field Detector and extracts a specific string value from a Text Unit. The first matching group is used if      the regular expression returns multiple matching groups. This is only applicable to string fields. | [optional] 
**depends_on_fields** | **str** |  | [optional] [readonly] 
**confidence** | **str** |  | [optional] 
**requires_text_annotations** | **bool** |  | [optional] 
**read_only** | **bool** |  | [optional] 
**category** | **str** |  | [optional] [readonly] 
**family** | **int** |  | [optional] 
**default_value** | **object** | When populated, this      default value is displayed in the user interface’s annotator sidebar for the associated field. If not populated, the      Field Value remains empty by default. Please wrap entries with quotes, example: “landlord”. This is only applicable       to Choice and Multichoice fields. | [optional] 
**choices** | **str** |  | [optional] [readonly] 
**allow_values_not_specified_in_choices** | **bool** |  | [optional] 
**stop_words** | **object** |  | [optional] 
**metadata** | **object** |  | [optional] 
**training_finished** | **bool** |  | [optional] 
**dirty** | **bool** |  | [optional] 
**order** | **int** |  | [optional] 
**trained_after_documents_number** | **int** |  | [optional] 
**hidden_always** | **bool** |  | [optional] 
**hide_until_python** | **str** |  | [optional] 
**hide_until_js** | **str** |  | [optional] 
**detect_limit_unit** | **str** | Choose to add an upward limit to the amount of document text                                           ContraxSuite will search for this Document Field. For example, you can choose                                           to only search the first 10 paragraphs of text for the value required (this                                           often works best for values like “Company,” “Execution Date,” or “Parties,”                                          all of which typically appear in the first few paragraphs of a contract). | [optional] 
**detect_limit_count** | **int** | Specify the maximum  range for a bounded search. Field detection begins at the top of the document and continues until this Nth  \&quot;Detect limit unit\&quot; element. | [optional] 
**display_yes_no** | **bool** | Checking this box will      display “Yes” if Related Info text is found, and display “No” if no text is found. | [optional] 
**value_aware** | **str** |  | [optional] [readonly] 
**created_by** | **int** |  | [optional] 
**modified_by** | **int** |  | 
**created_date** | **datetime** |  | [optional] [readonly] 
**modified_date** | **datetime** |  | [optional] [readonly] 
**vectorizer_stop_words** | **str** | Stop words for vectorizers      user in field-based ML field detection. These stop words are excluded from going into the feature vector part      build based on this field. In addition to these words the standard sklearn \&quot;english\&quot; word list is used.      Format: each word on new line | [optional] 
**unsure_choice_value** | **str** | Makes sense for machine learning      strategies with \&quot;Unsure\&quot; category. The strategy will return this value if probabilities of all other categories      appear lower than the specified threshold. | [optional] 
**unsure_thresholds_by_value** | **object** | Makes sense for machine learning      strategies with \&quot;Unsure\&quot; category. The strategy will return concrete result (one of choice values) only if      the probability of the detected value is greater than this threshold. Otherwise the strategy returns None      or the choice value specified in \&quot;Unsure choice value\&quot; field. Format: { \&quot;value1\&quot;: 0.9, \&quot;value2\&quot;: 0.5, ...}.      Default: 0.9 | [optional] 
**mlflow_model_uri** | **str** | MLFlow model URI      understandable by the MLFlow artifact downloading routines. | [optional] 
**mlflow_detect_on_document_level** | **bool** | If true - whole      document text will be sent to the MLFlow model and the field value will be returned for the whole text with no     annotations. If false - each text unit will be sent separately. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


