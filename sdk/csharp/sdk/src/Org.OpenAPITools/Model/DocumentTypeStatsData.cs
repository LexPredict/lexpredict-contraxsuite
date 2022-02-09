/*
 * Contraxsuite API
 *
 * Contraxsuite API
 *
 * The version of the OpenAPI document: 2.1.188
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
    /// DocumentTypeStatsData
    /// </summary>
    [DataContract]
    public partial class DocumentTypeStatsData :  IEquatable<DocumentTypeStatsData>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="DocumentTypeStatsData" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected DocumentTypeStatsData() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="DocumentTypeStatsData" /> class.
        /// </summary>
        /// <param name="uid">uid (required).</param>
        /// <param name="code">code (required).</param>
        /// <param name="title">title (required).</param>
        /// <param name="fieldsCount">fieldsCount (required).</param>
        /// <param name="detectorsCount">detectorsCount (required).</param>
        /// <param name="hideUntilPythonCount">hideUntilPythonCount (required).</param>
        /// <param name="hiddenAlwaysCount">hiddenAlwaysCount (required).</param>
        /// <param name="hideUntilPythonPcnt">hideUntilPythonPcnt (required).</param>
        /// <param name="hiddenAlwaysPcnt">hiddenAlwaysPcnt (required).</param>
        /// <param name="detectorDisabledCount">detectorDisabledCount (required).</param>
        /// <param name="detectorDisabledPcnt">detectorDisabledPcnt (required).</param>
        /// <param name="detectorUseRegexpsOnlyCount">detectorUseRegexpsOnlyCount (required).</param>
        /// <param name="detectorUseRegexpsOnlyPcnt">detectorUseRegexpsOnlyPcnt (required).</param>
        /// <param name="detectorUseFormulaOnlyCount">detectorUseFormulaOnlyCount (required).</param>
        /// <param name="detectorUseFormulaOnlyPcnt">detectorUseFormulaOnlyPcnt (required).</param>
        /// <param name="detectorRegexpTableCount">detectorRegexpTableCount (required).</param>
        /// <param name="detectorRegexpTablePcnt">detectorRegexpTablePcnt (required).</param>
        /// <param name="detectorTextBasedMlOnlyCount">detectorTextBasedMlOnlyCount (required).</param>
        /// <param name="detectorTextBasedMlOnlyPcnt">detectorTextBasedMlOnlyPcnt (required).</param>
        /// <param name="detectorFieldsBasedMlOnlyCount">detectorFieldsBasedMlOnlyCount (required).</param>
        /// <param name="detectorFieldsBasedMlOnlyPcnt">detectorFieldsBasedMlOnlyPcnt (required).</param>
        /// <param name="detectorFieldsBasedProbMlOnlyCount">detectorFieldsBasedProbMlOnlyCount (required).</param>
        /// <param name="detectorFieldsBasedProbMlOnlyPcnt">detectorFieldsBasedProbMlOnlyPcnt (required).</param>
        /// <param name="detectorFieldBasedRegexpsCount">detectorFieldBasedRegexpsCount (required).</param>
        /// <param name="detectorFieldBasedRegexpsPcnt">detectorFieldBasedRegexpsPcnt (required).</param>
        /// <param name="detectorMlflowModelCount">detectorMlflowModelCount (required).</param>
        /// <param name="detectorMlflowModelPcnt">detectorMlflowModelPcnt (required).</param>
        public DocumentTypeStatsData(Guid uid = default(Guid), string code = default(string), string title = default(string), int fieldsCount = default(int), int detectorsCount = default(int), int hideUntilPythonCount = default(int), int hiddenAlwaysCount = default(int), decimal hideUntilPythonPcnt = default(decimal), decimal hiddenAlwaysPcnt = default(decimal), decimal detectorDisabledCount = default(decimal), decimal detectorDisabledPcnt = default(decimal), decimal detectorUseRegexpsOnlyCount = default(decimal), decimal detectorUseRegexpsOnlyPcnt = default(decimal), decimal detectorUseFormulaOnlyCount = default(decimal), decimal detectorUseFormulaOnlyPcnt = default(decimal), decimal detectorRegexpTableCount = default(decimal), decimal detectorRegexpTablePcnt = default(decimal), decimal detectorTextBasedMlOnlyCount = default(decimal), decimal detectorTextBasedMlOnlyPcnt = default(decimal), decimal detectorFieldsBasedMlOnlyCount = default(decimal), decimal detectorFieldsBasedMlOnlyPcnt = default(decimal), decimal detectorFieldsBasedProbMlOnlyCount = default(decimal), decimal detectorFieldsBasedProbMlOnlyPcnt = default(decimal), decimal detectorFieldBasedRegexpsCount = default(decimal), decimal detectorFieldBasedRegexpsPcnt = default(decimal), decimal detectorMlflowModelCount = default(decimal), decimal detectorMlflowModelPcnt = default(decimal))
        {
            // to ensure "uid" is required (not null)
            if (uid == null)
            {
                throw new InvalidDataException("uid is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.Uid = uid;
            }

            // to ensure "code" is required (not null)
            if (code == null)
            {
                throw new InvalidDataException("code is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.Code = code;
            }

            // to ensure "title" is required (not null)
            if (title == null)
            {
                throw new InvalidDataException("title is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.Title = title;
            }

            // to ensure "fieldsCount" is required (not null)
            if (fieldsCount == null)
            {
                throw new InvalidDataException("fieldsCount is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.FieldsCount = fieldsCount;
            }

            // to ensure "detectorsCount" is required (not null)
            if (detectorsCount == null)
            {
                throw new InvalidDataException("detectorsCount is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorsCount = detectorsCount;
            }

            // to ensure "hideUntilPythonCount" is required (not null)
            if (hideUntilPythonCount == null)
            {
                throw new InvalidDataException("hideUntilPythonCount is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.HideUntilPythonCount = hideUntilPythonCount;
            }

            // to ensure "hiddenAlwaysCount" is required (not null)
            if (hiddenAlwaysCount == null)
            {
                throw new InvalidDataException("hiddenAlwaysCount is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.HiddenAlwaysCount = hiddenAlwaysCount;
            }

            // to ensure "hideUntilPythonPcnt" is required (not null)
            if (hideUntilPythonPcnt == null)
            {
                throw new InvalidDataException("hideUntilPythonPcnt is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.HideUntilPythonPcnt = hideUntilPythonPcnt;
            }

            // to ensure "hiddenAlwaysPcnt" is required (not null)
            if (hiddenAlwaysPcnt == null)
            {
                throw new InvalidDataException("hiddenAlwaysPcnt is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.HiddenAlwaysPcnt = hiddenAlwaysPcnt;
            }

            // to ensure "detectorDisabledCount" is required (not null)
            if (detectorDisabledCount == null)
            {
                throw new InvalidDataException("detectorDisabledCount is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorDisabledCount = detectorDisabledCount;
            }

            // to ensure "detectorDisabledPcnt" is required (not null)
            if (detectorDisabledPcnt == null)
            {
                throw new InvalidDataException("detectorDisabledPcnt is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorDisabledPcnt = detectorDisabledPcnt;
            }

            // to ensure "detectorUseRegexpsOnlyCount" is required (not null)
            if (detectorUseRegexpsOnlyCount == null)
            {
                throw new InvalidDataException("detectorUseRegexpsOnlyCount is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorUseRegexpsOnlyCount = detectorUseRegexpsOnlyCount;
            }

            // to ensure "detectorUseRegexpsOnlyPcnt" is required (not null)
            if (detectorUseRegexpsOnlyPcnt == null)
            {
                throw new InvalidDataException("detectorUseRegexpsOnlyPcnt is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorUseRegexpsOnlyPcnt = detectorUseRegexpsOnlyPcnt;
            }

            // to ensure "detectorUseFormulaOnlyCount" is required (not null)
            if (detectorUseFormulaOnlyCount == null)
            {
                throw new InvalidDataException("detectorUseFormulaOnlyCount is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorUseFormulaOnlyCount = detectorUseFormulaOnlyCount;
            }

            // to ensure "detectorUseFormulaOnlyPcnt" is required (not null)
            if (detectorUseFormulaOnlyPcnt == null)
            {
                throw new InvalidDataException("detectorUseFormulaOnlyPcnt is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorUseFormulaOnlyPcnt = detectorUseFormulaOnlyPcnt;
            }

            // to ensure "detectorRegexpTableCount" is required (not null)
            if (detectorRegexpTableCount == null)
            {
                throw new InvalidDataException("detectorRegexpTableCount is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorRegexpTableCount = detectorRegexpTableCount;
            }

            // to ensure "detectorRegexpTablePcnt" is required (not null)
            if (detectorRegexpTablePcnt == null)
            {
                throw new InvalidDataException("detectorRegexpTablePcnt is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorRegexpTablePcnt = detectorRegexpTablePcnt;
            }

            // to ensure "detectorTextBasedMlOnlyCount" is required (not null)
            if (detectorTextBasedMlOnlyCount == null)
            {
                throw new InvalidDataException("detectorTextBasedMlOnlyCount is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorTextBasedMlOnlyCount = detectorTextBasedMlOnlyCount;
            }

            // to ensure "detectorTextBasedMlOnlyPcnt" is required (not null)
            if (detectorTextBasedMlOnlyPcnt == null)
            {
                throw new InvalidDataException("detectorTextBasedMlOnlyPcnt is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorTextBasedMlOnlyPcnt = detectorTextBasedMlOnlyPcnt;
            }

            // to ensure "detectorFieldsBasedMlOnlyCount" is required (not null)
            if (detectorFieldsBasedMlOnlyCount == null)
            {
                throw new InvalidDataException("detectorFieldsBasedMlOnlyCount is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorFieldsBasedMlOnlyCount = detectorFieldsBasedMlOnlyCount;
            }

            // to ensure "detectorFieldsBasedMlOnlyPcnt" is required (not null)
            if (detectorFieldsBasedMlOnlyPcnt == null)
            {
                throw new InvalidDataException("detectorFieldsBasedMlOnlyPcnt is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorFieldsBasedMlOnlyPcnt = detectorFieldsBasedMlOnlyPcnt;
            }

            // to ensure "detectorFieldsBasedProbMlOnlyCount" is required (not null)
            if (detectorFieldsBasedProbMlOnlyCount == null)
            {
                throw new InvalidDataException("detectorFieldsBasedProbMlOnlyCount is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorFieldsBasedProbMlOnlyCount = detectorFieldsBasedProbMlOnlyCount;
            }

            // to ensure "detectorFieldsBasedProbMlOnlyPcnt" is required (not null)
            if (detectorFieldsBasedProbMlOnlyPcnt == null)
            {
                throw new InvalidDataException("detectorFieldsBasedProbMlOnlyPcnt is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorFieldsBasedProbMlOnlyPcnt = detectorFieldsBasedProbMlOnlyPcnt;
            }

            // to ensure "detectorFieldBasedRegexpsCount" is required (not null)
            if (detectorFieldBasedRegexpsCount == null)
            {
                throw new InvalidDataException("detectorFieldBasedRegexpsCount is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorFieldBasedRegexpsCount = detectorFieldBasedRegexpsCount;
            }

            // to ensure "detectorFieldBasedRegexpsPcnt" is required (not null)
            if (detectorFieldBasedRegexpsPcnt == null)
            {
                throw new InvalidDataException("detectorFieldBasedRegexpsPcnt is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorFieldBasedRegexpsPcnt = detectorFieldBasedRegexpsPcnt;
            }

            // to ensure "detectorMlflowModelCount" is required (not null)
            if (detectorMlflowModelCount == null)
            {
                throw new InvalidDataException("detectorMlflowModelCount is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorMlflowModelCount = detectorMlflowModelCount;
            }

            // to ensure "detectorMlflowModelPcnt" is required (not null)
            if (detectorMlflowModelPcnt == null)
            {
                throw new InvalidDataException("detectorMlflowModelPcnt is a required property for DocumentTypeStatsData and cannot be null");
            }
            else
            {
                this.DetectorMlflowModelPcnt = detectorMlflowModelPcnt;
            }

        }

        /// <summary>
        /// Gets or Sets Uid
        /// </summary>
        [DataMember(Name="uid", EmitDefaultValue=true)]
        public Guid Uid { get; set; }

        /// <summary>
        /// Gets or Sets Code
        /// </summary>
        [DataMember(Name="code", EmitDefaultValue=true)]
        public string Code { get; set; }

        /// <summary>
        /// Gets or Sets Title
        /// </summary>
        [DataMember(Name="title", EmitDefaultValue=true)]
        public string Title { get; set; }

        /// <summary>
        /// Gets or Sets FieldsCount
        /// </summary>
        [DataMember(Name="fields_count", EmitDefaultValue=true)]
        public int FieldsCount { get; set; }

        /// <summary>
        /// Gets or Sets DetectorsCount
        /// </summary>
        [DataMember(Name="detectors_count", EmitDefaultValue=true)]
        public int DetectorsCount { get; set; }

        /// <summary>
        /// Gets or Sets HideUntilPythonCount
        /// </summary>
        [DataMember(Name="hide_until_python_count", EmitDefaultValue=true)]
        public int HideUntilPythonCount { get; set; }

        /// <summary>
        /// Gets or Sets HiddenAlwaysCount
        /// </summary>
        [DataMember(Name="hidden_always_count", EmitDefaultValue=true)]
        public int HiddenAlwaysCount { get; set; }

        /// <summary>
        /// Gets or Sets HideUntilPythonPcnt
        /// </summary>
        [DataMember(Name="hide_until_python_pcnt", EmitDefaultValue=true)]
        public decimal HideUntilPythonPcnt { get; set; }

        /// <summary>
        /// Gets or Sets HiddenAlwaysPcnt
        /// </summary>
        [DataMember(Name="hidden_always_pcnt", EmitDefaultValue=true)]
        public decimal HiddenAlwaysPcnt { get; set; }

        /// <summary>
        /// Gets or Sets FieldsData
        /// </summary>
        [DataMember(Name="fields_data", EmitDefaultValue=false)]
        public List<Object> FieldsData { get; private set; }

        /// <summary>
        /// Gets or Sets DetectorDisabledCount
        /// </summary>
        [DataMember(Name="detector_disabled_count", EmitDefaultValue=true)]
        public decimal DetectorDisabledCount { get; set; }

        /// <summary>
        /// Gets or Sets DetectorDisabledPcnt
        /// </summary>
        [DataMember(Name="detector_disabled_pcnt", EmitDefaultValue=true)]
        public decimal DetectorDisabledPcnt { get; set; }

        /// <summary>
        /// Gets or Sets DetectorUseRegexpsOnlyCount
        /// </summary>
        [DataMember(Name="detector_use_regexps_only_count", EmitDefaultValue=true)]
        public decimal DetectorUseRegexpsOnlyCount { get; set; }

        /// <summary>
        /// Gets or Sets DetectorUseRegexpsOnlyPcnt
        /// </summary>
        [DataMember(Name="detector_use_regexps_only_pcnt", EmitDefaultValue=true)]
        public decimal DetectorUseRegexpsOnlyPcnt { get; set; }

        /// <summary>
        /// Gets or Sets DetectorUseFormulaOnlyCount
        /// </summary>
        [DataMember(Name="detector_use_formula_only_count", EmitDefaultValue=true)]
        public decimal DetectorUseFormulaOnlyCount { get; set; }

        /// <summary>
        /// Gets or Sets DetectorUseFormulaOnlyPcnt
        /// </summary>
        [DataMember(Name="detector_use_formula_only_pcnt", EmitDefaultValue=true)]
        public decimal DetectorUseFormulaOnlyPcnt { get; set; }

        /// <summary>
        /// Gets or Sets DetectorRegexpTableCount
        /// </summary>
        [DataMember(Name="detector_regexp_table_count", EmitDefaultValue=true)]
        public decimal DetectorRegexpTableCount { get; set; }

        /// <summary>
        /// Gets or Sets DetectorRegexpTablePcnt
        /// </summary>
        [DataMember(Name="detector_regexp_table_pcnt", EmitDefaultValue=true)]
        public decimal DetectorRegexpTablePcnt { get; set; }

        /// <summary>
        /// Gets or Sets DetectorTextBasedMlOnlyCount
        /// </summary>
        [DataMember(Name="detector_text_based_ml_only_count", EmitDefaultValue=true)]
        public decimal DetectorTextBasedMlOnlyCount { get; set; }

        /// <summary>
        /// Gets or Sets DetectorTextBasedMlOnlyPcnt
        /// </summary>
        [DataMember(Name="detector_text_based_ml_only_pcnt", EmitDefaultValue=true)]
        public decimal DetectorTextBasedMlOnlyPcnt { get; set; }

        /// <summary>
        /// Gets or Sets DetectorFieldsBasedMlOnlyCount
        /// </summary>
        [DataMember(Name="detector_fields_based_ml_only_count", EmitDefaultValue=true)]
        public decimal DetectorFieldsBasedMlOnlyCount { get; set; }

        /// <summary>
        /// Gets or Sets DetectorFieldsBasedMlOnlyPcnt
        /// </summary>
        [DataMember(Name="detector_fields_based_ml_only_pcnt", EmitDefaultValue=true)]
        public decimal DetectorFieldsBasedMlOnlyPcnt { get; set; }

        /// <summary>
        /// Gets or Sets DetectorFieldsBasedProbMlOnlyCount
        /// </summary>
        [DataMember(Name="detector_fields_based_prob_ml_only_count", EmitDefaultValue=true)]
        public decimal DetectorFieldsBasedProbMlOnlyCount { get; set; }

        /// <summary>
        /// Gets or Sets DetectorFieldsBasedProbMlOnlyPcnt
        /// </summary>
        [DataMember(Name="detector_fields_based_prob_ml_only_pcnt", EmitDefaultValue=true)]
        public decimal DetectorFieldsBasedProbMlOnlyPcnt { get; set; }

        /// <summary>
        /// Gets or Sets DetectorFieldBasedRegexpsCount
        /// </summary>
        [DataMember(Name="detector_field_based_regexps_count", EmitDefaultValue=true)]
        public decimal DetectorFieldBasedRegexpsCount { get; set; }

        /// <summary>
        /// Gets or Sets DetectorFieldBasedRegexpsPcnt
        /// </summary>
        [DataMember(Name="detector_field_based_regexps_pcnt", EmitDefaultValue=true)]
        public decimal DetectorFieldBasedRegexpsPcnt { get; set; }

        /// <summary>
        /// Gets or Sets DetectorMlflowModelCount
        /// </summary>
        [DataMember(Name="detector_mlflow_model_count", EmitDefaultValue=true)]
        public decimal DetectorMlflowModelCount { get; set; }

        /// <summary>
        /// Gets or Sets DetectorMlflowModelPcnt
        /// </summary>
        [DataMember(Name="detector_mlflow_model_pcnt", EmitDefaultValue=true)]
        public decimal DetectorMlflowModelPcnt { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class DocumentTypeStatsData {\n");
            sb.Append("  Uid: ").Append(Uid).Append("\n");
            sb.Append("  Code: ").Append(Code).Append("\n");
            sb.Append("  Title: ").Append(Title).Append("\n");
            sb.Append("  FieldsCount: ").Append(FieldsCount).Append("\n");
            sb.Append("  DetectorsCount: ").Append(DetectorsCount).Append("\n");
            sb.Append("  HideUntilPythonCount: ").Append(HideUntilPythonCount).Append("\n");
            sb.Append("  HiddenAlwaysCount: ").Append(HiddenAlwaysCount).Append("\n");
            sb.Append("  HideUntilPythonPcnt: ").Append(HideUntilPythonPcnt).Append("\n");
            sb.Append("  HiddenAlwaysPcnt: ").Append(HiddenAlwaysPcnt).Append("\n");
            sb.Append("  FieldsData: ").Append(FieldsData).Append("\n");
            sb.Append("  DetectorDisabledCount: ").Append(DetectorDisabledCount).Append("\n");
            sb.Append("  DetectorDisabledPcnt: ").Append(DetectorDisabledPcnt).Append("\n");
            sb.Append("  DetectorUseRegexpsOnlyCount: ").Append(DetectorUseRegexpsOnlyCount).Append("\n");
            sb.Append("  DetectorUseRegexpsOnlyPcnt: ").Append(DetectorUseRegexpsOnlyPcnt).Append("\n");
            sb.Append("  DetectorUseFormulaOnlyCount: ").Append(DetectorUseFormulaOnlyCount).Append("\n");
            sb.Append("  DetectorUseFormulaOnlyPcnt: ").Append(DetectorUseFormulaOnlyPcnt).Append("\n");
            sb.Append("  DetectorRegexpTableCount: ").Append(DetectorRegexpTableCount).Append("\n");
            sb.Append("  DetectorRegexpTablePcnt: ").Append(DetectorRegexpTablePcnt).Append("\n");
            sb.Append("  DetectorTextBasedMlOnlyCount: ").Append(DetectorTextBasedMlOnlyCount).Append("\n");
            sb.Append("  DetectorTextBasedMlOnlyPcnt: ").Append(DetectorTextBasedMlOnlyPcnt).Append("\n");
            sb.Append("  DetectorFieldsBasedMlOnlyCount: ").Append(DetectorFieldsBasedMlOnlyCount).Append("\n");
            sb.Append("  DetectorFieldsBasedMlOnlyPcnt: ").Append(DetectorFieldsBasedMlOnlyPcnt).Append("\n");
            sb.Append("  DetectorFieldsBasedProbMlOnlyCount: ").Append(DetectorFieldsBasedProbMlOnlyCount).Append("\n");
            sb.Append("  DetectorFieldsBasedProbMlOnlyPcnt: ").Append(DetectorFieldsBasedProbMlOnlyPcnt).Append("\n");
            sb.Append("  DetectorFieldBasedRegexpsCount: ").Append(DetectorFieldBasedRegexpsCount).Append("\n");
            sb.Append("  DetectorFieldBasedRegexpsPcnt: ").Append(DetectorFieldBasedRegexpsPcnt).Append("\n");
            sb.Append("  DetectorMlflowModelCount: ").Append(DetectorMlflowModelCount).Append("\n");
            sb.Append("  DetectorMlflowModelPcnt: ").Append(DetectorMlflowModelPcnt).Append("\n");
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
            return this.Equals(input as DocumentTypeStatsData);
        }

        /// <summary>
        /// Returns true if DocumentTypeStatsData instances are equal
        /// </summary>
        /// <param name="input">Instance of DocumentTypeStatsData to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(DocumentTypeStatsData input)
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
                    this.Code == input.Code ||
                    (this.Code != null &&
                    this.Code.Equals(input.Code))
                ) && 
                (
                    this.Title == input.Title ||
                    (this.Title != null &&
                    this.Title.Equals(input.Title))
                ) && 
                (
                    this.FieldsCount == input.FieldsCount ||
                    (this.FieldsCount != null &&
                    this.FieldsCount.Equals(input.FieldsCount))
                ) && 
                (
                    this.DetectorsCount == input.DetectorsCount ||
                    (this.DetectorsCount != null &&
                    this.DetectorsCount.Equals(input.DetectorsCount))
                ) && 
                (
                    this.HideUntilPythonCount == input.HideUntilPythonCount ||
                    (this.HideUntilPythonCount != null &&
                    this.HideUntilPythonCount.Equals(input.HideUntilPythonCount))
                ) && 
                (
                    this.HiddenAlwaysCount == input.HiddenAlwaysCount ||
                    (this.HiddenAlwaysCount != null &&
                    this.HiddenAlwaysCount.Equals(input.HiddenAlwaysCount))
                ) && 
                (
                    this.HideUntilPythonPcnt == input.HideUntilPythonPcnt ||
                    (this.HideUntilPythonPcnt != null &&
                    this.HideUntilPythonPcnt.Equals(input.HideUntilPythonPcnt))
                ) && 
                (
                    this.HiddenAlwaysPcnt == input.HiddenAlwaysPcnt ||
                    (this.HiddenAlwaysPcnt != null &&
                    this.HiddenAlwaysPcnt.Equals(input.HiddenAlwaysPcnt))
                ) && 
                (
                    this.FieldsData == input.FieldsData ||
                    this.FieldsData != null &&
                    input.FieldsData != null &&
                    this.FieldsData.SequenceEqual(input.FieldsData)
                ) && 
                (
                    this.DetectorDisabledCount == input.DetectorDisabledCount ||
                    (this.DetectorDisabledCount != null &&
                    this.DetectorDisabledCount.Equals(input.DetectorDisabledCount))
                ) && 
                (
                    this.DetectorDisabledPcnt == input.DetectorDisabledPcnt ||
                    (this.DetectorDisabledPcnt != null &&
                    this.DetectorDisabledPcnt.Equals(input.DetectorDisabledPcnt))
                ) && 
                (
                    this.DetectorUseRegexpsOnlyCount == input.DetectorUseRegexpsOnlyCount ||
                    (this.DetectorUseRegexpsOnlyCount != null &&
                    this.DetectorUseRegexpsOnlyCount.Equals(input.DetectorUseRegexpsOnlyCount))
                ) && 
                (
                    this.DetectorUseRegexpsOnlyPcnt == input.DetectorUseRegexpsOnlyPcnt ||
                    (this.DetectorUseRegexpsOnlyPcnt != null &&
                    this.DetectorUseRegexpsOnlyPcnt.Equals(input.DetectorUseRegexpsOnlyPcnt))
                ) && 
                (
                    this.DetectorUseFormulaOnlyCount == input.DetectorUseFormulaOnlyCount ||
                    (this.DetectorUseFormulaOnlyCount != null &&
                    this.DetectorUseFormulaOnlyCount.Equals(input.DetectorUseFormulaOnlyCount))
                ) && 
                (
                    this.DetectorUseFormulaOnlyPcnt == input.DetectorUseFormulaOnlyPcnt ||
                    (this.DetectorUseFormulaOnlyPcnt != null &&
                    this.DetectorUseFormulaOnlyPcnt.Equals(input.DetectorUseFormulaOnlyPcnt))
                ) && 
                (
                    this.DetectorRegexpTableCount == input.DetectorRegexpTableCount ||
                    (this.DetectorRegexpTableCount != null &&
                    this.DetectorRegexpTableCount.Equals(input.DetectorRegexpTableCount))
                ) && 
                (
                    this.DetectorRegexpTablePcnt == input.DetectorRegexpTablePcnt ||
                    (this.DetectorRegexpTablePcnt != null &&
                    this.DetectorRegexpTablePcnt.Equals(input.DetectorRegexpTablePcnt))
                ) && 
                (
                    this.DetectorTextBasedMlOnlyCount == input.DetectorTextBasedMlOnlyCount ||
                    (this.DetectorTextBasedMlOnlyCount != null &&
                    this.DetectorTextBasedMlOnlyCount.Equals(input.DetectorTextBasedMlOnlyCount))
                ) && 
                (
                    this.DetectorTextBasedMlOnlyPcnt == input.DetectorTextBasedMlOnlyPcnt ||
                    (this.DetectorTextBasedMlOnlyPcnt != null &&
                    this.DetectorTextBasedMlOnlyPcnt.Equals(input.DetectorTextBasedMlOnlyPcnt))
                ) && 
                (
                    this.DetectorFieldsBasedMlOnlyCount == input.DetectorFieldsBasedMlOnlyCount ||
                    (this.DetectorFieldsBasedMlOnlyCount != null &&
                    this.DetectorFieldsBasedMlOnlyCount.Equals(input.DetectorFieldsBasedMlOnlyCount))
                ) && 
                (
                    this.DetectorFieldsBasedMlOnlyPcnt == input.DetectorFieldsBasedMlOnlyPcnt ||
                    (this.DetectorFieldsBasedMlOnlyPcnt != null &&
                    this.DetectorFieldsBasedMlOnlyPcnt.Equals(input.DetectorFieldsBasedMlOnlyPcnt))
                ) && 
                (
                    this.DetectorFieldsBasedProbMlOnlyCount == input.DetectorFieldsBasedProbMlOnlyCount ||
                    (this.DetectorFieldsBasedProbMlOnlyCount != null &&
                    this.DetectorFieldsBasedProbMlOnlyCount.Equals(input.DetectorFieldsBasedProbMlOnlyCount))
                ) && 
                (
                    this.DetectorFieldsBasedProbMlOnlyPcnt == input.DetectorFieldsBasedProbMlOnlyPcnt ||
                    (this.DetectorFieldsBasedProbMlOnlyPcnt != null &&
                    this.DetectorFieldsBasedProbMlOnlyPcnt.Equals(input.DetectorFieldsBasedProbMlOnlyPcnt))
                ) && 
                (
                    this.DetectorFieldBasedRegexpsCount == input.DetectorFieldBasedRegexpsCount ||
                    (this.DetectorFieldBasedRegexpsCount != null &&
                    this.DetectorFieldBasedRegexpsCount.Equals(input.DetectorFieldBasedRegexpsCount))
                ) && 
                (
                    this.DetectorFieldBasedRegexpsPcnt == input.DetectorFieldBasedRegexpsPcnt ||
                    (this.DetectorFieldBasedRegexpsPcnt != null &&
                    this.DetectorFieldBasedRegexpsPcnt.Equals(input.DetectorFieldBasedRegexpsPcnt))
                ) && 
                (
                    this.DetectorMlflowModelCount == input.DetectorMlflowModelCount ||
                    (this.DetectorMlflowModelCount != null &&
                    this.DetectorMlflowModelCount.Equals(input.DetectorMlflowModelCount))
                ) && 
                (
                    this.DetectorMlflowModelPcnt == input.DetectorMlflowModelPcnt ||
                    (this.DetectorMlflowModelPcnt != null &&
                    this.DetectorMlflowModelPcnt.Equals(input.DetectorMlflowModelPcnt))
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
                if (this.Code != null)
                    hashCode = hashCode * 59 + this.Code.GetHashCode();
                if (this.Title != null)
                    hashCode = hashCode * 59 + this.Title.GetHashCode();
                if (this.FieldsCount != null)
                    hashCode = hashCode * 59 + this.FieldsCount.GetHashCode();
                if (this.DetectorsCount != null)
                    hashCode = hashCode * 59 + this.DetectorsCount.GetHashCode();
                if (this.HideUntilPythonCount != null)
                    hashCode = hashCode * 59 + this.HideUntilPythonCount.GetHashCode();
                if (this.HiddenAlwaysCount != null)
                    hashCode = hashCode * 59 + this.HiddenAlwaysCount.GetHashCode();
                if (this.HideUntilPythonPcnt != null)
                    hashCode = hashCode * 59 + this.HideUntilPythonPcnt.GetHashCode();
                if (this.HiddenAlwaysPcnt != null)
                    hashCode = hashCode * 59 + this.HiddenAlwaysPcnt.GetHashCode();
                if (this.FieldsData != null)
                    hashCode = hashCode * 59 + this.FieldsData.GetHashCode();
                if (this.DetectorDisabledCount != null)
                    hashCode = hashCode * 59 + this.DetectorDisabledCount.GetHashCode();
                if (this.DetectorDisabledPcnt != null)
                    hashCode = hashCode * 59 + this.DetectorDisabledPcnt.GetHashCode();
                if (this.DetectorUseRegexpsOnlyCount != null)
                    hashCode = hashCode * 59 + this.DetectorUseRegexpsOnlyCount.GetHashCode();
                if (this.DetectorUseRegexpsOnlyPcnt != null)
                    hashCode = hashCode * 59 + this.DetectorUseRegexpsOnlyPcnt.GetHashCode();
                if (this.DetectorUseFormulaOnlyCount != null)
                    hashCode = hashCode * 59 + this.DetectorUseFormulaOnlyCount.GetHashCode();
                if (this.DetectorUseFormulaOnlyPcnt != null)
                    hashCode = hashCode * 59 + this.DetectorUseFormulaOnlyPcnt.GetHashCode();
                if (this.DetectorRegexpTableCount != null)
                    hashCode = hashCode * 59 + this.DetectorRegexpTableCount.GetHashCode();
                if (this.DetectorRegexpTablePcnt != null)
                    hashCode = hashCode * 59 + this.DetectorRegexpTablePcnt.GetHashCode();
                if (this.DetectorTextBasedMlOnlyCount != null)
                    hashCode = hashCode * 59 + this.DetectorTextBasedMlOnlyCount.GetHashCode();
                if (this.DetectorTextBasedMlOnlyPcnt != null)
                    hashCode = hashCode * 59 + this.DetectorTextBasedMlOnlyPcnt.GetHashCode();
                if (this.DetectorFieldsBasedMlOnlyCount != null)
                    hashCode = hashCode * 59 + this.DetectorFieldsBasedMlOnlyCount.GetHashCode();
                if (this.DetectorFieldsBasedMlOnlyPcnt != null)
                    hashCode = hashCode * 59 + this.DetectorFieldsBasedMlOnlyPcnt.GetHashCode();
                if (this.DetectorFieldsBasedProbMlOnlyCount != null)
                    hashCode = hashCode * 59 + this.DetectorFieldsBasedProbMlOnlyCount.GetHashCode();
                if (this.DetectorFieldsBasedProbMlOnlyPcnt != null)
                    hashCode = hashCode * 59 + this.DetectorFieldsBasedProbMlOnlyPcnt.GetHashCode();
                if (this.DetectorFieldBasedRegexpsCount != null)
                    hashCode = hashCode * 59 + this.DetectorFieldBasedRegexpsCount.GetHashCode();
                if (this.DetectorFieldBasedRegexpsPcnt != null)
                    hashCode = hashCode * 59 + this.DetectorFieldBasedRegexpsPcnt.GetHashCode();
                if (this.DetectorMlflowModelCount != null)
                    hashCode = hashCode * 59 + this.DetectorMlflowModelCount.GetHashCode();
                if (this.DetectorMlflowModelPcnt != null)
                    hashCode = hashCode * 59 + this.DetectorMlflowModelPcnt.GetHashCode();
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
            yield break;
        }
    }

}
