

# DocumentFieldCreate


## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**documentType** | **String** |  |  |
|**code** | **String** | Field codes must be lowercase, should start with  a Latin letter, and contain only Latin letters, digits, underscores. Field codes must be unique to every Document Type. |  |
|**longCode** | **String** |  |  [optional] [readonly] |
|**title** | **String** |  |  |
|**description** | **String** |  |  [optional] |
|**type** | [**TypeEnum**](#TypeEnum) |  |  |
|**textUnitType** | [**TextUnitTypeEnum**](#TextUnitTypeEnum) |  |  [optional] |
|**valueDetectionStrategy** | [**ValueDetectionStrategyEnum**](#ValueDetectionStrategyEnum) |  |  [optional] |
|**classifierInitScript** | **String** | Classifier initialization script. Here is how it used: &lt;br /&gt;&lt;br /&gt;def&amp;nbsp;init_classifier_impl(field_code:&amp;nbsp;str,&amp;nbsp;init_script:&amp;nbsp;str):&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;if&amp;nbsp;init_script&amp;nbsp;is&amp;nbsp;not&amp;nbsp;None:&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;init_script&amp;nbsp;&#x3D;&amp;nbsp;init_script.strip()&lt;br /&gt;&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;if&amp;nbsp;not&amp;nbsp;init_script:&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;from&amp;nbsp;sklearn&amp;nbsp;import&amp;nbsp;tree&amp;nbsp;as&amp;nbsp;sklearn_tree&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;return&amp;nbsp;sklearn_tree.DecisionTreeClassifier()&lt;br /&gt;&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;from&amp;nbsp;sklearn&amp;nbsp;import&amp;nbsp;tree&amp;nbsp;as&amp;nbsp;sklearn_tree&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;from&amp;nbsp;sklearn&amp;nbsp;import&amp;nbsp;neural_network&amp;nbsp;as&amp;nbsp;sklearn_neural_network&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;from&amp;nbsp;sklearn&amp;nbsp;import&amp;nbsp;neighbors&amp;nbsp;as&amp;nbsp;sklearn_neighbors&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;from&amp;nbsp;sklearn&amp;nbsp;import&amp;nbsp;svm&amp;nbsp;as&amp;nbsp;sklearn_svm&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;from&amp;nbsp;sklearn&amp;nbsp;import&amp;nbsp;gaussian_process&amp;nbsp;as&amp;nbsp;sklearn_gaussian_process&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;from&amp;nbsp;sklearn.gaussian_process&amp;nbsp;import&amp;nbsp;kernels&amp;nbsp;as&amp;nbsp;sklearn_gaussian_process_kernels&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;from&amp;nbsp;sklearn&amp;nbsp;import&amp;nbsp;ensemble&amp;nbsp;as&amp;nbsp;sklearn_ensemble&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;from&amp;nbsp;sklearn&amp;nbsp;import&amp;nbsp;naive_bayes&amp;nbsp;as&amp;nbsp;sklearn_naive_bayes&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;from&amp;nbsp;sklearn&amp;nbsp;import&amp;nbsp;discriminant_analysis&amp;nbsp;as&amp;nbsp;sklearn_discriminant_analysis&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;from&amp;nbsp;sklearn&amp;nbsp;import&amp;nbsp;linear_model&amp;nbsp;as&amp;nbsp;sklearn_linear_model&lt;br /&gt;&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;eval_locals&amp;nbsp;&#x3D;&amp;nbsp;{&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&#39;sklearn_linear_model&#39;:&amp;nbsp;sklearn_linear_model,&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&#39;sklearn_tree&#39;:&amp;nbsp;sklearn_tree,&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&#39;sklearn_neural_network&#39;:&amp;nbsp;sklearn_neural_network,&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&#39;sklearn_neighbors&#39;:&amp;nbsp;sklearn_neighbors,&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&#39;sklearn_svm&#39;:&amp;nbsp;sklearn_svm,&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&#39;sklearn_gaussian_process&#39;:&amp;nbsp;sklearn_gaussian_process,&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&#39;sklearn_gaussian_process_kernels&#39;:&amp;nbsp;sklearn_gaussian_process_kernels,&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&#39;sklearn_ensemble&#39;:&amp;nbsp;sklearn_ensemble,&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&#39;sklearn_naive_bayes&#39;:&amp;nbsp;sklearn_naive_bayes,&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;&#39;sklearn_discriminant_analysis&#39;:&amp;nbsp;sklearn_discriminant_analysis&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;}&lt;br /&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;&amp;nbsp;return&amp;nbsp;eval_script(&#39;classifier&amp;nbsp;init&amp;nbsp;script&amp;nbsp;of&amp;nbsp;field&amp;nbsp;{0}&#39;.format(field_code),&amp;nbsp;init_script,&amp;nbsp;eval_locals)&lt;br /&gt; |  [optional] |
|**formula** | **String** |  |  [optional] |
|**convertDecimalsToFloatsInFormulaArgs** | **Boolean** | Floating point field values      are represented in Python Decimal type to avoid rounding problems in machine numbers representations.      Use this checkbox for converting them to Python float type before calculating the formula.      Float: 0.1 + 0.2 &#x3D; 0.30000000000000004. Decimal: 0.1 + 0.2 &#x3D; 0.3. |  [optional] |
|**valueRegexp** | **String** | This regular expression is run on the sentence      found by a Field Detector and extracts a specific string value from a Text Unit. If the regular expression returns multiple matching groups, then the first matching group will be used by the Field. This is only applicable to String Fields. |  [optional] |
|**dependsOnFields** | **List&lt;String&gt;** |  |  [optional] |
|**confidence** | [**ConfidenceEnum**](#ConfidenceEnum) |  |  [optional] |
|**requiresTextAnnotations** | **Boolean** |  |  [optional] |
|**readOnly** | **Boolean** |  |  [optional] |
|**category** | **Integer** |  |  [optional] |
|**family** | **Integer** |  |  [optional] |
|**defaultValue** | **Object** | If populated, the Default Value will be displayed for this Field if no other value is found by the chosen Value Detection Strategy. Leave this form blank to have the Field Value remain empty by default. Please wrap entries with quotes, example: “landlord”. This is only applicable to Choice and Multi Choice Fields. |  [optional] |
|**choices** | **String** | Newline-separated choices. A choice cannot contain a comma. |  [optional] |
|**allowValuesNotSpecifiedInChoices** | **Boolean** |  |  [optional] |
|**metadata** | **Object** |  |  [optional] |
|**trainingFinished** | **Boolean** |  |  [optional] |
|**dirty** | **Boolean** |  |  [optional] |
|**order** | **Integer** |  |  [optional] |
|**trainedAfterDocumentsNumber** | **Integer** |  |  [optional] |
|**hiddenAlways** | **Boolean** |  |  [optional] |
|**hideUntilPython** | **String** |                      Enter a boolean expression in Python syntax. If this Python expression evaluates to True, then this              Document Field will be displayed in the user interface. Likewise, if this Python expression evaluates to              False, then this Document Field will be hidden from view. Importantly, if a document’s status is set to              complete and this Document Field remains hidden, then this Document Field’s data will be erased. Similarly,              this Document Field might contain data that a user can not review if it is hidden and the document has not              been set to complete. |  [optional] |
|**hideUntilJs** | **String** | Target expression (\&quot;Hide until python\&quot; expression converted to JavaScript syntax for frontend). Allowed operators: +, -, *, /, &#x3D;&#x3D;&#x3D;, !&#x3D;&#x3D;, &#x3D;&#x3D;, !&#x3D;, &amp;&amp;, ||, &gt;, &lt;, &gt;&#x3D;, &lt;&#x3D;, % |  [optional] [readonly] |
|**displayYesNo** | **Boolean** | Checking this box will      display “Yes” if Related Info text is found, and display “No” if no text is found. |  [optional] |
|**vectorizerStopWords** | **String** | Stop words for vectorizers      user in field-based ML field detection. These stop words are excluded from going into the feature vector part      build based on this field. In addition to these words the standard sklearn \&quot;english\&quot; word list is used.      Format: each word on new line |  [optional] |
|**unsureChoiceValue** | **String** | Makes sense for machine learning      strategies with \&quot;Unsure\&quot; category. The strategy will return this value if probabilities of all other categories      appear lower than the specified threshold. |  [optional] |
|**unsureThresholdsByValue** | **Object** | Makes sense for machine learning      strategies with \&quot;Unsure\&quot; category. The strategy will return concrete result (one of choice values) only if      the probability of the detected value is greater than this threshold. Otherwise the strategy returns None      or the choice value specified in \&quot;Unsure choice value\&quot; field. Format: { \&quot;value1\&quot;: 0.9, \&quot;value2\&quot;: 0.5, ...}.      Default: 0.9 |  [optional] |
|**mlflowModelUri** | **String** | MLFlow model URI      understandable by the MLFlow artifact downloading routines. |  [optional] |
|**mlflowDetectOnDocumentLevel** | **Boolean** | If true - whole      document text will be sent to the MLFlow model and the field value will be returned for the whole text with no     annotations. If false - each text unit will be sent separately. |  [optional] |
|**warningMessage** | **String** |  |  [optional] [readonly] |



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
| MLFLOW_MODEL | &quot;mlflow_model&quot; |



## Enum: ConfidenceEnum

| Name | Value |
|---- | -----|
| HIGH | &quot;High&quot; |
| MEDIUM | &quot;Medium&quot; |
| LOW | &quot;Low&quot; |



