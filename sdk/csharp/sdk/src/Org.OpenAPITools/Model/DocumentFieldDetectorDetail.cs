/*
 * Contraxsuite API
 *
 * Contraxsuite API
 *
 * The version of the OpenAPI document: 2.1.0
 * 
 * Generated by: https://github.com/openapitools/openapi-generator.git
 */

using System;
using System.Linq;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Collections;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Runtime.Serialization;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using System.ComponentModel.DataAnnotations;
using OpenAPIDateConverter = Org.OpenAPITools.Client.OpenAPIDateConverter;

namespace Org.OpenAPITools.Model
{
    /// <summary>
    /// DocumentFieldDetectorDetail
    /// </summary>
    [DataContract]
    public partial class DocumentFieldDetectorDetail :  IEquatable<DocumentFieldDetectorDetail>, IValidatableObject
    {
        /// <summary>
        /// Field detector category used for technical needs e.g. for determining  which field detectors were created automatically during import process.
        /// </summary>
        /// <value>Field detector category used for technical needs e.g. for determining  which field detectors were created automatically during import process.</value>
        [JsonConverter(typeof(StringEnumConverter))]
        public enum CategoryEnum
        {
            /// <summary>
            /// Enum Simpleconfig for value: simple_config
            /// </summary>
            [EnumMember(Value = "simple_config")]
            Simpleconfig = 1

        }

        /// <summary>
        /// Field detector category used for technical needs e.g. for determining  which field detectors were created automatically during import process.
        /// </summary>
        /// <value>Field detector category used for technical needs e.g. for determining  which field detectors were created automatically during import process.</value>
        [DataMember(Name="category", EmitDefaultValue=true)]
        public CategoryEnum? Category { get; set; }
        /// <summary>
        /// Provide additional instruction on which  specific values should be prioritized for extraction, when multiple values of the same type  (e.g., Company, Person, Geography) are found within the relevant detected Text Unit.
        /// </summary>
        /// <value>Provide additional instruction on which  specific values should be prioritized for extraction, when multiple values of the same type  (e.g., Company, Person, Geography) are found within the relevant detected Text Unit.</value>
        [JsonConverter(typeof(StringEnumConverter))]
        public enum ExtractionHintEnum
        {
            /// <summary>
            /// Enum FIRST for value: TAKE_FIRST
            /// </summary>
            [EnumMember(Value = "TAKE_FIRST")]
            FIRST = 1,

            /// <summary>
            /// Enum SECOND for value: TAKE_SECOND
            /// </summary>
            [EnumMember(Value = "TAKE_SECOND")]
            SECOND = 2,

            /// <summary>
            /// Enum LAST for value: TAKE_LAST
            /// </summary>
            [EnumMember(Value = "TAKE_LAST")]
            LAST = 3,

            /// <summary>
            /// Enum MIN for value: TAKE_MIN
            /// </summary>
            [EnumMember(Value = "TAKE_MIN")]
            MIN = 4,

            /// <summary>
            /// Enum MAX for value: TAKE_MAX
            /// </summary>
            [EnumMember(Value = "TAKE_MAX")]
            MAX = 5

        }

        /// <summary>
        /// Provide additional instruction on which  specific values should be prioritized for extraction, when multiple values of the same type  (e.g., Company, Person, Geography) are found within the relevant detected Text Unit.
        /// </summary>
        /// <value>Provide additional instruction on which  specific values should be prioritized for extraction, when multiple values of the same type  (e.g., Company, Person, Geography) are found within the relevant detected Text Unit.</value>
        [DataMember(Name="extraction_hint", EmitDefaultValue=true)]
        public ExtractionHintEnum? ExtractionHint { get; set; }
        /// <summary>
        /// Defines which part of the matched Text Unit  should be passed to the extraction function. Example: In the string \&quot;2019-01-23 is the start date and 2019-01-24 is the  end date,\&quot; if text part &#x3D; \&quot;Before matching substring\&quot; and Include regexp is \&quot;is.{0,100}start\&quot; then \&quot;2019-01-23\&quot; will be  parsed correctly as the start date.
        /// </summary>
        /// <value>Defines which part of the matched Text Unit  should be passed to the extraction function. Example: In the string \&quot;2019-01-23 is the start date and 2019-01-24 is the  end date,\&quot; if text part &#x3D; \&quot;Before matching substring\&quot; and Include regexp is \&quot;is.{0,100}start\&quot; then \&quot;2019-01-23\&quot; will be  parsed correctly as the start date.</value>
        [JsonConverter(typeof(StringEnumConverter))]
        public enum TextPartEnum
        {
            /// <summary>
            /// Enum FULL for value: FULL
            /// </summary>
            [EnumMember(Value = "FULL")]
            FULL = 1,

            /// <summary>
            /// Enum BEFOREREGEXP for value: BEFORE_REGEXP
            /// </summary>
            [EnumMember(Value = "BEFORE_REGEXP")]
            BEFOREREGEXP = 2,

            /// <summary>
            /// Enum AFTERREGEXP for value: AFTER_REGEXP
            /// </summary>
            [EnumMember(Value = "AFTER_REGEXP")]
            AFTERREGEXP = 3,

            /// <summary>
            /// Enum INSIDEREGEXP for value: INSIDE_REGEXP
            /// </summary>
            [EnumMember(Value = "INSIDE_REGEXP")]
            INSIDEREGEXP = 4

        }

        /// <summary>
        /// Defines which part of the matched Text Unit  should be passed to the extraction function. Example: In the string \&quot;2019-01-23 is the start date and 2019-01-24 is the  end date,\&quot; if text part &#x3D; \&quot;Before matching substring\&quot; and Include regexp is \&quot;is.{0,100}start\&quot; then \&quot;2019-01-23\&quot; will be  parsed correctly as the start date.
        /// </summary>
        /// <value>Defines which part of the matched Text Unit  should be passed to the extraction function. Example: In the string \&quot;2019-01-23 is the start date and 2019-01-24 is the  end date,\&quot; if text part &#x3D; \&quot;Before matching substring\&quot; and Include regexp is \&quot;is.{0,100}start\&quot; then \&quot;2019-01-23\&quot; will be  parsed correctly as the start date.</value>
        [DataMember(Name="text_part", EmitDefaultValue=false)]
        public TextPartEnum? TextPart { get; set; }
        /// <summary>
        /// Choose to add an upward limit to the amount of document text                                               ContraxSuite will search for this Document Field. For example, you can choose                                               to only search the first 10 paragraphs of text for the value required (this                                               often works best for values like “Company,” “Execution Date,” or “Parties,”                                              all of which typically appear in the first few paragraphs of a contract).
        /// </summary>
        /// <value>Choose to add an upward limit to the amount of document text                                               ContraxSuite will search for this Document Field. For example, you can choose                                               to only search the first 10 paragraphs of text for the value required (this                                               often works best for values like “Company,” “Execution Date,” or “Parties,”                                              all of which typically appear in the first few paragraphs of a contract).</value>
        [JsonConverter(typeof(StringEnumConverter))]
        public enum DetectLimitUnitEnum
        {
            /// <summary>
            /// Enum NONE for value: NONE
            /// </summary>
            [EnumMember(Value = "NONE")]
            NONE = 1,

            /// <summary>
            /// Enum UNIT for value: UNIT
            /// </summary>
            [EnumMember(Value = "UNIT")]
            UNIT = 2

        }

        /// <summary>
        /// Choose to add an upward limit to the amount of document text                                               ContraxSuite will search for this Document Field. For example, you can choose                                               to only search the first 10 paragraphs of text for the value required (this                                               often works best for values like “Company,” “Execution Date,” or “Parties,”                                              all of which typically appear in the first few paragraphs of a contract).
        /// </summary>
        /// <value>Choose to add an upward limit to the amount of document text                                               ContraxSuite will search for this Document Field. For example, you can choose                                               to only search the first 10 paragraphs of text for the value required (this                                               often works best for values like “Company,” “Execution Date,” or “Parties,”                                              all of which typically appear in the first few paragraphs of a contract).</value>
        [DataMember(Name="detect_limit_unit", EmitDefaultValue=false)]
        public DetectLimitUnitEnum? DetectLimitUnit { get; set; }
        /// <summary>
        /// Initializes a new instance of the <see cref="DocumentFieldDetectorDetail" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected DocumentFieldDetectorDetail() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="DocumentFieldDetectorDetail" /> class.
        /// </summary>
        /// <param name="category">Field detector category used for technical needs e.g. for determining  which field detectors were created automatically during import process..</param>
        /// <param name="field">field (required).</param>
        /// <param name="excludeRegexps">Enter regular expressions, each on a new line, for text patterns  you want EXCLUDED. The Field Detector will attempt to skip any Text Unit that contains any of the patterns written  here, and will move on to the next Text Unit. Avoid using “.*” and similar unlimited multipliers, as they can crash  or slow ContraxSuite. Use bounded multipliers for variable length matching, like “.{0,100}” or similar. Note that  Exclude regexps are checked before Definition words and Include regexps. If a Field Detector has Exclude regexps, but  no Definition words or Include regexps, it will not extract any data..</param>
        /// <param name="definitionWords">Enter words or phrases, each on a new line, that must be present  in the Text Unit. These words must be in the Definitions List. If ContraxSuite fails to recognize these words as  definitions, then the Field Detector skips and moves to the next Text Unit. If there are Include regexps, then the  Field Detector checks against those requirements. The Field Detector marks the entire Text Unit as a match. Note that  the Field Detector checks for definition words after filtering using the Exclude regexps..</param>
        /// <param name="regexpsPreProcessLower">Set &#39;ignore case&#39; flag for both &#39;Include regexps&#39; and &#39;Exclude regexps&#39; options..</param>
        /// <param name="detectedValue">The string value written here  will be assigned to the field if the Field Detector positively matches a Text Unit. This is only applicable to Choice,  Multichoice, and String fields, as their respective Field Detectors do not extract and display values from the source  text..</param>
        /// <param name="extractionHint">Provide additional instruction on which  specific values should be prioritized for extraction, when multiple values of the same type  (e.g., Company, Person, Geography) are found within the relevant detected Text Unit..</param>
        /// <param name="textPart">Defines which part of the matched Text Unit  should be passed to the extraction function. Example: In the string \&quot;2019-01-23 is the start date and 2019-01-24 is the  end date,\&quot; if text part &#x3D; \&quot;Before matching substring\&quot; and Include regexp is \&quot;is.{0,100}start\&quot; then \&quot;2019-01-23\&quot; will be  parsed correctly as the start date..</param>
        /// <param name="detectLimitUnit">Choose to add an upward limit to the amount of document text                                               ContraxSuite will search for this Document Field. For example, you can choose                                               to only search the first 10 paragraphs of text for the value required (this                                               often works best for values like “Company,” “Execution Date,” or “Parties,”                                              all of which typically appear in the first few paragraphs of a contract)..</param>
        /// <param name="detectLimitCount">Specify the maximum      range for a bounded search. Field detection begins at the top of the document and continues until this Nth      \&quot;Detect limit unit\&quot; element..</param>
        public DocumentFieldDetectorDetail(CategoryEnum? category = default(CategoryEnum?), string field = default(string), string excludeRegexps = default(string), string definitionWords = default(string), bool regexpsPreProcessLower = default(bool), string detectedValue = default(string), ExtractionHintEnum? extractionHint = default(ExtractionHintEnum?), TextPartEnum? textPart = default(TextPartEnum?), DetectLimitUnitEnum? detectLimitUnit = default(DetectLimitUnitEnum?), int detectLimitCount = default(int))
        {
            this.Category = category;
            // to ensure "field" is required (not null)
            if (field == null)
            {
                throw new InvalidDataException("field is a required property for DocumentFieldDetectorDetail and cannot be null");
            }
            else
            {
                this.Field = field;
            }

            this.ExcludeRegexps = excludeRegexps;
            this.DefinitionWords = definitionWords;
            this.DetectedValue = detectedValue;
            this.ExtractionHint = extractionHint;
            this.Category = category;
            this.ExcludeRegexps = excludeRegexps;
            this.DefinitionWords = definitionWords;
            this.RegexpsPreProcessLower = regexpsPreProcessLower;
            this.DetectedValue = detectedValue;
            this.ExtractionHint = extractionHint;
            this.TextPart = textPart;
            this.DetectLimitUnit = detectLimitUnit;
            this.DetectLimitCount = detectLimitCount;
        }

        /// <summary>
        /// Gets or Sets Uid
        /// </summary>
        [DataMember(Name="uid", EmitDefaultValue=false)]
        public Guid Uid { get; private set; }


        /// <summary>
        /// Gets or Sets Field
        /// </summary>
        [DataMember(Name="field", EmitDefaultValue=true)]
        public string Field { get; set; }

        /// <summary>
        /// Gets or Sets FieldCode
        /// </summary>
        [DataMember(Name="field__code", EmitDefaultValue=false)]
        public string FieldCode { get; private set; }

        /// <summary>
        /// Gets or Sets FieldTitle
        /// </summary>
        [DataMember(Name="field__title", EmitDefaultValue=false)]
        public string FieldTitle { get; private set; }

        /// <summary>
        /// Gets or Sets FieldUid
        /// </summary>
        [DataMember(Name="field__uid", EmitDefaultValue=false)]
        public string FieldUid { get; private set; }

        /// <summary>
        /// Gets or Sets FieldType
        /// </summary>
        [DataMember(Name="field__type", EmitDefaultValue=false)]
        public string FieldType { get; private set; }

        /// <summary>
        /// Gets or Sets FieldDocumentTypeTitle
        /// </summary>
        [DataMember(Name="field__document_type__title", EmitDefaultValue=false)]
        public string FieldDocumentTypeTitle { get; private set; }

        /// <summary>
        /// Enter regular expressions, each on a new line, for text patterns  you want EXCLUDED. The Field Detector will attempt to skip any Text Unit that contains any of the patterns written  here, and will move on to the next Text Unit. Avoid using “.*” and similar unlimited multipliers, as they can crash  or slow ContraxSuite. Use bounded multipliers for variable length matching, like “.{0,100}” or similar. Note that  Exclude regexps are checked before Definition words and Include regexps. If a Field Detector has Exclude regexps, but  no Definition words or Include regexps, it will not extract any data.
        /// </summary>
        /// <value>Enter regular expressions, each on a new line, for text patterns  you want EXCLUDED. The Field Detector will attempt to skip any Text Unit that contains any of the patterns written  here, and will move on to the next Text Unit. Avoid using “.*” and similar unlimited multipliers, as they can crash  or slow ContraxSuite. Use bounded multipliers for variable length matching, like “.{0,100}” or similar. Note that  Exclude regexps are checked before Definition words and Include regexps. If a Field Detector has Exclude regexps, but  no Definition words or Include regexps, it will not extract any data.</value>
        [DataMember(Name="exclude_regexps", EmitDefaultValue=true)]
        public string ExcludeRegexps { get; set; }

        /// <summary>
        /// Enter words or phrases, each on a new line, that must be present  in the Text Unit. These words must be in the Definitions List. If ContraxSuite fails to recognize these words as  definitions, then the Field Detector skips and moves to the next Text Unit. If there are Include regexps, then the  Field Detector checks against those requirements. The Field Detector marks the entire Text Unit as a match. Note that  the Field Detector checks for definition words after filtering using the Exclude regexps.
        /// </summary>
        /// <value>Enter words or phrases, each on a new line, that must be present  in the Text Unit. These words must be in the Definitions List. If ContraxSuite fails to recognize these words as  definitions, then the Field Detector skips and moves to the next Text Unit. If there are Include regexps, then the  Field Detector checks against those requirements. The Field Detector marks the entire Text Unit as a match. Note that  the Field Detector checks for definition words after filtering using the Exclude regexps.</value>
        [DataMember(Name="definition_words", EmitDefaultValue=true)]
        public string DefinitionWords { get; set; }

        /// <summary>
        /// Gets or Sets IncludeRegexps
        /// </summary>
        [DataMember(Name="include_regexps", EmitDefaultValue=false)]
        public List<string> IncludeRegexps { get; private set; }

        /// <summary>
        /// Set &#39;ignore case&#39; flag for both &#39;Include regexps&#39; and &#39;Exclude regexps&#39; options.
        /// </summary>
        /// <value>Set &#39;ignore case&#39; flag for both &#39;Include regexps&#39; and &#39;Exclude regexps&#39; options.</value>
        [DataMember(Name="regexps_pre_process_lower", EmitDefaultValue=false)]
        public bool RegexpsPreProcessLower { get; set; }

        /// <summary>
        /// The string value written here  will be assigned to the field if the Field Detector positively matches a Text Unit. This is only applicable to Choice,  Multichoice, and String fields, as their respective Field Detectors do not extract and display values from the source  text.
        /// </summary>
        /// <value>The string value written here  will be assigned to the field if the Field Detector positively matches a Text Unit. This is only applicable to Choice,  Multichoice, and String fields, as their respective Field Detectors do not extract and display values from the source  text.</value>
        [DataMember(Name="detected_value", EmitDefaultValue=true)]
        public string DetectedValue { get; set; }




        /// <summary>
        /// Specify the maximum      range for a bounded search. Field detection begins at the top of the document and continues until this Nth      \&quot;Detect limit unit\&quot; element.
        /// </summary>
        /// <value>Specify the maximum      range for a bounded search. Field detection begins at the top of the document and continues until this Nth      \&quot;Detect limit unit\&quot; element.</value>
        [DataMember(Name="detect_limit_count", EmitDefaultValue=false)]
        public int DetectLimitCount { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class DocumentFieldDetectorDetail {\n");
            sb.Append("  Uid: ").Append(Uid).Append("\n");
            sb.Append("  Category: ").Append(Category).Append("\n");
            sb.Append("  Field: ").Append(Field).Append("\n");
            sb.Append("  FieldCode: ").Append(FieldCode).Append("\n");
            sb.Append("  FieldTitle: ").Append(FieldTitle).Append("\n");
            sb.Append("  FieldUid: ").Append(FieldUid).Append("\n");
            sb.Append("  FieldType: ").Append(FieldType).Append("\n");
            sb.Append("  FieldDocumentTypeTitle: ").Append(FieldDocumentTypeTitle).Append("\n");
            sb.Append("  ExcludeRegexps: ").Append(ExcludeRegexps).Append("\n");
            sb.Append("  DefinitionWords: ").Append(DefinitionWords).Append("\n");
            sb.Append("  IncludeRegexps: ").Append(IncludeRegexps).Append("\n");
            sb.Append("  RegexpsPreProcessLower: ").Append(RegexpsPreProcessLower).Append("\n");
            sb.Append("  DetectedValue: ").Append(DetectedValue).Append("\n");
            sb.Append("  ExtractionHint: ").Append(ExtractionHint).Append("\n");
            sb.Append("  TextPart: ").Append(TextPart).Append("\n");
            sb.Append("  DetectLimitUnit: ").Append(DetectLimitUnit).Append("\n");
            sb.Append("  DetectLimitCount: ").Append(DetectLimitCount).Append("\n");
            sb.Append("}\n");
            return sb.ToString();
        }

        /// <summary>
        /// Returns the JSON string presentation of the object
        /// </summary>
        /// <returns>JSON string presentation of the object</returns>
        public virtual string ToJson()
        {
            return Newtonsoft.Json.JsonConvert.SerializeObject(this, Newtonsoft.Json.Formatting.Indented);
        }

        /// <summary>
        /// Returns true if objects are equal
        /// </summary>
        /// <param name="input">Object to be compared</param>
        /// <returns>Boolean</returns>
        public override bool Equals(object input)
        {
            return this.Equals(input as DocumentFieldDetectorDetail);
        }

        /// <summary>
        /// Returns true if DocumentFieldDetectorDetail instances are equal
        /// </summary>
        /// <param name="input">Instance of DocumentFieldDetectorDetail to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(DocumentFieldDetectorDetail input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.Uid == input.Uid ||
                    (this.Uid != null &&
                    this.Uid.Equals(input.Uid))
                ) && 
                (
                    this.Category == input.Category ||
                    (this.Category != null &&
                    this.Category.Equals(input.Category))
                ) && 
                (
                    this.Field == input.Field ||
                    (this.Field != null &&
                    this.Field.Equals(input.Field))
                ) && 
                (
                    this.FieldCode == input.FieldCode ||
                    (this.FieldCode != null &&
                    this.FieldCode.Equals(input.FieldCode))
                ) && 
                (
                    this.FieldTitle == input.FieldTitle ||
                    (this.FieldTitle != null &&
                    this.FieldTitle.Equals(input.FieldTitle))
                ) && 
                (
                    this.FieldUid == input.FieldUid ||
                    (this.FieldUid != null &&
                    this.FieldUid.Equals(input.FieldUid))
                ) && 
                (
                    this.FieldType == input.FieldType ||
                    (this.FieldType != null &&
                    this.FieldType.Equals(input.FieldType))
                ) && 
                (
                    this.FieldDocumentTypeTitle == input.FieldDocumentTypeTitle ||
                    (this.FieldDocumentTypeTitle != null &&
                    this.FieldDocumentTypeTitle.Equals(input.FieldDocumentTypeTitle))
                ) && 
                (
                    this.ExcludeRegexps == input.ExcludeRegexps ||
                    (this.ExcludeRegexps != null &&
                    this.ExcludeRegexps.Equals(input.ExcludeRegexps))
                ) && 
                (
                    this.DefinitionWords == input.DefinitionWords ||
                    (this.DefinitionWords != null &&
                    this.DefinitionWords.Equals(input.DefinitionWords))
                ) && 
                (
                    this.IncludeRegexps == input.IncludeRegexps ||
                    this.IncludeRegexps != null &&
                    input.IncludeRegexps != null &&
                    this.IncludeRegexps.SequenceEqual(input.IncludeRegexps)
                ) && 
                (
                    this.RegexpsPreProcessLower == input.RegexpsPreProcessLower ||
                    (this.RegexpsPreProcessLower != null &&
                    this.RegexpsPreProcessLower.Equals(input.RegexpsPreProcessLower))
                ) && 
                (
                    this.DetectedValue == input.DetectedValue ||
                    (this.DetectedValue != null &&
                    this.DetectedValue.Equals(input.DetectedValue))
                ) && 
                (
                    this.ExtractionHint == input.ExtractionHint ||
                    (this.ExtractionHint != null &&
                    this.ExtractionHint.Equals(input.ExtractionHint))
                ) && 
                (
                    this.TextPart == input.TextPart ||
                    (this.TextPart != null &&
                    this.TextPart.Equals(input.TextPart))
                ) && 
                (
                    this.DetectLimitUnit == input.DetectLimitUnit ||
                    (this.DetectLimitUnit != null &&
                    this.DetectLimitUnit.Equals(input.DetectLimitUnit))
                ) && 
                (
                    this.DetectLimitCount == input.DetectLimitCount ||
                    (this.DetectLimitCount != null &&
                    this.DetectLimitCount.Equals(input.DetectLimitCount))
                );
        }

        /// <summary>
        /// Gets the hash code
        /// </summary>
        /// <returns>Hash code</returns>
        public override int GetHashCode()
        {
            unchecked // Overflow is fine, just wrap
            {
                int hashCode = 41;
                if (this.Uid != null)
                    hashCode = hashCode * 59 + this.Uid.GetHashCode();
                if (this.Category != null)
                    hashCode = hashCode * 59 + this.Category.GetHashCode();
                if (this.Field != null)
                    hashCode = hashCode * 59 + this.Field.GetHashCode();
                if (this.FieldCode != null)
                    hashCode = hashCode * 59 + this.FieldCode.GetHashCode();
                if (this.FieldTitle != null)
                    hashCode = hashCode * 59 + this.FieldTitle.GetHashCode();
                if (this.FieldUid != null)
                    hashCode = hashCode * 59 + this.FieldUid.GetHashCode();
                if (this.FieldType != null)
                    hashCode = hashCode * 59 + this.FieldType.GetHashCode();
                if (this.FieldDocumentTypeTitle != null)
                    hashCode = hashCode * 59 + this.FieldDocumentTypeTitle.GetHashCode();
                if (this.ExcludeRegexps != null)
                    hashCode = hashCode * 59 + this.ExcludeRegexps.GetHashCode();
                if (this.DefinitionWords != null)
                    hashCode = hashCode * 59 + this.DefinitionWords.GetHashCode();
                if (this.IncludeRegexps != null)
                    hashCode = hashCode * 59 + this.IncludeRegexps.GetHashCode();
                if (this.RegexpsPreProcessLower != null)
                    hashCode = hashCode * 59 + this.RegexpsPreProcessLower.GetHashCode();
                if (this.DetectedValue != null)
                    hashCode = hashCode * 59 + this.DetectedValue.GetHashCode();
                if (this.ExtractionHint != null)
                    hashCode = hashCode * 59 + this.ExtractionHint.GetHashCode();
                if (this.TextPart != null)
                    hashCode = hashCode * 59 + this.TextPart.GetHashCode();
                if (this.DetectLimitUnit != null)
                    hashCode = hashCode * 59 + this.DetectLimitUnit.GetHashCode();
                if (this.DetectLimitCount != null)
                    hashCode = hashCode * 59 + this.DetectLimitCount.GetHashCode();
                return hashCode;
            }
        }

        /// <summary>
        /// To validate all properties of the instance
        /// </summary>
        /// <param name="validationContext">Validation context</param>
        /// <returns>Validation Result</returns>
        IEnumerable<System.ComponentModel.DataAnnotations.ValidationResult> IValidatableObject.Validate(ValidationContext validationContext)
        {
            // DetectedValue (string) maxLength
            if(this.DetectedValue != null && this.DetectedValue.Length > 256)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for DetectedValue, length must be less than 256.", new [] { "DetectedValue" });
            }

 

 
            // DetectLimitCount (int) maximum
            if(this.DetectLimitCount > (int)2147483647)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for DetectLimitCount, must be a value less than or equal to 2147483647.", new [] { "DetectLimitCount" });
            }

            // DetectLimitCount (int) minimum
            if(this.DetectLimitCount < (int)-2147483648)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for DetectLimitCount, must be a value greater than or equal to -2147483648.", new [] { "DetectLimitCount" });
            }

            yield break;
        }
    }

}
