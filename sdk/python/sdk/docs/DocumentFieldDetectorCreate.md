# DocumentFieldDetectorCreate


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**field** | **str** |  | 
**uid** | **str** |  | [optional] [readonly] 
**warning_message** | **str** |  | [optional] [readonly] 
**category** | **str, none_type** | Field detector category used for technical needs e.g. for determining  which field detectors were created automatically during import process. | [optional]  if omitted the server will use the default value of "simple_config"
**exclude_regexps** | **str, none_type** | Enter regular expressions, each on a new line, for text patterns  you want EXCLUDED. The Field Detector will attempt to skip any Text Unit that contains any of the patterns written  here, and will move on to the next Text Unit. Avoid using “.*” and similar unlimited multipliers, as they can crash  or slow ContraxSuite. Use bounded multipliers for variable length matching, like “.{0,100}” or similar. Note that  Exclude regexps are checked before Definition words and Include regexps. If a Field Detector has Exclude regexps, but  no Definition words or Include regexps, it will not extract any data. | [optional] 
**definition_words** | **str, none_type** | Enter words or phrases, each on a new line, that must be present  in the Text Unit. These words must be in the Definitions List. If ContraxSuite fails to recognize these words as  definitions, then the Field Detector skips and moves to the next Text Unit. If there are Include regexps, then the  Field Detector checks against those requirements. The Field Detector marks the entire Text Unit as a match. Note that  the Field Detector checks for definition words after filtering using the Exclude regexps. | [optional] 
**include_regexps** | **str, none_type** | Enter regular expressions, each on a new  line, for text patterns you want INCLUDED. The Field Detector will attempt to match each of these regular expressions  within a given Text Unit. Avoid using “.*” and similar unlimited multipliers, as they can crash or slow ContraxSuite.  Use bounded multipliers for variable length matching, like “.{0,100}” or similar. Note that Include regexps are checked  after both Exclude regexps and Definition words. | [optional] 
**regexps_pre_process_lower** | **bool** | Set &#39;ignore case&#39; flag for both &#39;Include regexps&#39; and &#39;Exclude regexps&#39; options. | [optional] 
**detected_value** | **str, none_type** | The string value written here  will be assigned to the field if the Field Detector positively matches a Text Unit. This is only applicable to Choice,  Multichoice, and String fields, as their respective Field Detectors do not extract and display values from the source  text. | [optional] 
**extraction_hint** | **str, none_type** | Provide additional instruction on which  specific values should be prioritized for extraction, when multiple values of the same type  (e.g., Company, Person, Geography) are found within the relevant detected Text Unit. | [optional] 
**text_part** | **str** | Defines which part of the matched Text Unit  should be passed to the extraction function. Example: In the string \&quot;2019-01-23 is the start date and 2019-01-24 is the  end date,\&quot; if text part &#x3D; \&quot;Before matching substring\&quot; and Include regexp is \&quot;is.{0,100}start\&quot; then \&quot;2019-01-23\&quot; will be  parsed correctly as the start date. | [optional] 
**detect_limit_unit** | **str** | Choose to add an upward limit to the amount of document text                                               ContraxSuite will search for this Document Field. For example, you can choose                                               to only search the first 10 paragraphs of text for the value required (this                                               often works best for values like “Company,” “Execution Date,” or “Parties,”                                              all of which typically appear in the first few paragraphs of a contract). | [optional] 
**detect_limit_count** | **int** | Specify the maximum      range for a bounded search. Field detection begins at the top of the document and continues until this Nth      \&quot;Detect limit unit\&quot; element. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


