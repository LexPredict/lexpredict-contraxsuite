# DocumentFieldDetail


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_type** | **str, none_type** |  | 
**code** | **str** | Field codes must be lowercase, should start with  a Latin letter, and contain only Latin letters, digits, underscores. Field codes must be unique to every Document Type. | 
**title** | **str** |  | 
**uid** | **str** |  | [optional] [readonly] 
**long_code** | **str** |  | [optional] 
**description** | **str, none_type** |  | [optional] 
**type** | **str** |  | [optional] 
**text_unit_type** | **str** |  | [optional] 
**value_detection_strategy** | **str** |  | [optional] 
**classifier_init_script** | **str, none_type** |  | [optional] 
**formula** | **str, none_type** |  | [optional] 
**convert_decimals_to_floats_in_formula_args** | **bool** | Floating point field values      are represented in Python Decimal type to avoid rounding problems in machine numbers representations.      Use this checkbox for converting them to Python float type before calculating the formula.      Float: 0.1 + 0.2 &#x3D; 0.30000000000000004. Decimal: 0.1 + 0.2 &#x3D; 0.3. | [optional] 
**value_regexp** | **str, none_type** | This regular expression is run on the sentence      found by a Field Detector and extracts a specific string value from a Text Unit. If the regular expression returns multiple matching groups, then the first matching group will be used by the Field. This is only applicable to String Fields. | [optional] 
**depends_on_fields** | **[str]** |  | [optional] [readonly] 
**value_detection_strategy_name** | **str** |  | [optional] [readonly] 
**confidence** | **str, none_type** |  | [optional] 
**requires_text_annotations** | **bool** |  | [optional] 
**read_only** | **bool** |  | [optional] 
**category** | **str** |  | [optional] [readonly] 
**family** | **int, none_type** |  | [optional] 
**default_value** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}, none_type** | If populated, the Default Value will be displayed for this Field if no other value is found by the chosen Value Detection Strategy. Leave this form blank to have the Field Value remain empty by default. Please wrap entries with quotes, example: “landlord”. This is only applicable to Choice and Multi Choice Fields. | [optional] 
**choices** | **[str]** |  | [optional] [readonly] 
**allow_values_not_specified_in_choices** | **bool** |  | [optional] 
**metadata** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}, none_type** |  | [optional] 
**training_finished** | **bool** |  | [optional] 
**dirty** | **bool** |  | [optional] 
**order** | **int** |  | [optional] 
**trained_after_documents_number** | **int** |  | [optional] 
**hidden_always** | **bool** |  | [optional] 
**hide_until_python** | **str, none_type** |  | [optional] 
**hide_until_js** | **str, none_type** |  | [optional] 
**is_value_detection_strategy_disabled** | **bool** |  | [optional] [readonly] 
**display_yes_no** | **bool** | Checking this box will      display “Yes” if Related Info text is found, and display “No” if no text is found. | [optional] 
**value_aware** | **bool** |  | [optional] [readonly] 
**created_by__name** | **str** |  | [optional] [readonly] 
**modified_by__name** | **str** |  | [optional] [readonly] 
**created_date** | **datetime** |  | [optional] [readonly] 
**modified_date** | **datetime** |  | [optional] [readonly] 
**vectorizer_stop_words** | **str, none_type** | Stop words for vectorizers      user in field-based ML field detection. These stop words are excluded from going into the feature vector part      build based on this field. In addition to these words the standard sklearn \&quot;english\&quot; word list is used.      Format: each word on new line | [optional] 
**unsure_choice_value** | **str, none_type** | Makes sense for machine learning      strategies with \&quot;Unsure\&quot; category. The strategy will return this value if probabilities of all other categories      appear lower than the specified threshold. | [optional] 
**unsure_thresholds_by_value** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}, none_type** | Makes sense for machine learning      strategies with \&quot;Unsure\&quot; category. The strategy will return concrete result (one of choice values) only if      the probability of the detected value is greater than this threshold. Otherwise the strategy returns None      or the choice value specified in \&quot;Unsure choice value\&quot; field. Format: { \&quot;value1\&quot;: 0.9, \&quot;value2\&quot;: 0.5, ...}.      Default: 0.9 | [optional] 
**mlflow_model_uri** | **str, none_type** | MLFlow model URI      understandable by the MLFlow artifact downloading routines. | [optional] 
**mlflow_detect_on_document_level** | **bool** | If true - whole      document text will be sent to the MLFlow model and the field value will be returned for the whole text with no     annotations. If false - each text unit will be sent separately. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


