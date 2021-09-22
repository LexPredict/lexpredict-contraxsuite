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
    /// TextUnitSimilarity
    /// </summary>
    [DataContract]
    public partial class TextUnitSimilarity :  IEquatable<TextUnitSimilarity>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="TextUnitSimilarity" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected TextUnitSimilarity() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="TextUnitSimilarity" /> class.
        /// </summary>
        /// <param name="similarity">similarity (required).</param>
        /// <param name="run">run.</param>
        public TextUnitSimilarity(decimal similarity = default(decimal), DocumentSimilarityRun run = default(DocumentSimilarityRun))
        {
            // to ensure "similarity" is required (not null)
            if (similarity == null)
            {
                throw new InvalidDataException("similarity is a required property for TextUnitSimilarity and cannot be null");
            }
            else
            {
                this.Similarity = similarity;
            }

            this.Run = run;
        }

        /// <summary>
        /// Gets or Sets TextUnitAId
        /// </summary>
        [DataMember(Name="text_unit_a_id", EmitDefaultValue=false)]
        public string TextUnitAId { get; private set; }

        /// <summary>
        /// Gets or Sets TextUnitAUnitType
        /// </summary>
        [DataMember(Name="text_unit_a__unit_type", EmitDefaultValue=false)]
        public string TextUnitAUnitType { get; private set; }

        /// <summary>
        /// Gets or Sets TextUnitALanguage
        /// </summary>
        [DataMember(Name="text_unit_a__language", EmitDefaultValue=false)]
        public string TextUnitALanguage { get; private set; }

        /// <summary>
        /// Gets or Sets TextUnitATextunittextText
        /// </summary>
        [DataMember(Name="text_unit_a__textunittext__text", EmitDefaultValue=false)]
        public string TextUnitATextunittextText { get; private set; }

        /// <summary>
        /// Gets or Sets DocumentAId
        /// </summary>
        [DataMember(Name="document_a_id", EmitDefaultValue=false)]
        public string DocumentAId { get; private set; }

        /// <summary>
        /// Gets or Sets DocumentAName
        /// </summary>
        [DataMember(Name="document_a__name", EmitDefaultValue=false)]
        public string DocumentAName { get; private set; }

        /// <summary>
        /// Gets or Sets TextUnitBId
        /// </summary>
        [DataMember(Name="text_unit_b_id", EmitDefaultValue=false)]
        public string TextUnitBId { get; private set; }

        /// <summary>
        /// Gets or Sets TextUnitBUnitType
        /// </summary>
        [DataMember(Name="text_unit_b__unit_type", EmitDefaultValue=false)]
        public string TextUnitBUnitType { get; private set; }

        /// <summary>
        /// Gets or Sets TextUnitBLanguage
        /// </summary>
        [DataMember(Name="text_unit_b__language", EmitDefaultValue=false)]
        public string TextUnitBLanguage { get; private set; }

        /// <summary>
        /// Gets or Sets TextUnitBTextunittextText
        /// </summary>
        [DataMember(Name="text_unit_b__textunittext__text", EmitDefaultValue=false)]
        public string TextUnitBTextunittextText { get; private set; }

        /// <summary>
        /// Gets or Sets DocumentBId
        /// </summary>
        [DataMember(Name="document_b_id", EmitDefaultValue=false)]
        public string DocumentBId { get; private set; }

        /// <summary>
        /// Gets or Sets DocumentBName
        /// </summary>
        [DataMember(Name="document_b__name", EmitDefaultValue=false)]
        public string DocumentBName { get; private set; }

        /// <summary>
        /// Gets or Sets Similarity
        /// </summary>
        [DataMember(Name="similarity", EmitDefaultValue=true)]
        public decimal Similarity { get; set; }

        /// <summary>
        /// Gets or Sets Run
        /// </summary>
        [DataMember(Name="run", EmitDefaultValue=false)]
        public DocumentSimilarityRun Run { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class TextUnitSimilarity {\n");
            sb.Append("  TextUnitAId: ").Append(TextUnitAId).Append("\n");
            sb.Append("  TextUnitAUnitType: ").Append(TextUnitAUnitType).Append("\n");
            sb.Append("  TextUnitALanguage: ").Append(TextUnitALanguage).Append("\n");
            sb.Append("  TextUnitATextunittextText: ").Append(TextUnitATextunittextText).Append("\n");
            sb.Append("  DocumentAId: ").Append(DocumentAId).Append("\n");
            sb.Append("  DocumentAName: ").Append(DocumentAName).Append("\n");
            sb.Append("  TextUnitBId: ").Append(TextUnitBId).Append("\n");
            sb.Append("  TextUnitBUnitType: ").Append(TextUnitBUnitType).Append("\n");
            sb.Append("  TextUnitBLanguage: ").Append(TextUnitBLanguage).Append("\n");
            sb.Append("  TextUnitBTextunittextText: ").Append(TextUnitBTextunittextText).Append("\n");
            sb.Append("  DocumentBId: ").Append(DocumentBId).Append("\n");
            sb.Append("  DocumentBName: ").Append(DocumentBName).Append("\n");
            sb.Append("  Similarity: ").Append(Similarity).Append("\n");
            sb.Append("  Run: ").Append(Run).Append("\n");
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
            return this.Equals(input as TextUnitSimilarity);
        }

        /// <summary>
        /// Returns true if TextUnitSimilarity instances are equal
        /// </summary>
        /// <param name="input">Instance of TextUnitSimilarity to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(TextUnitSimilarity input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.TextUnitAId == input.TextUnitAId ||
                    (this.TextUnitAId != null &&
                    this.TextUnitAId.Equals(input.TextUnitAId))
                ) && 
                (
                    this.TextUnitAUnitType == input.TextUnitAUnitType ||
                    (this.TextUnitAUnitType != null &&
                    this.TextUnitAUnitType.Equals(input.TextUnitAUnitType))
                ) && 
                (
                    this.TextUnitALanguage == input.TextUnitALanguage ||
                    (this.TextUnitALanguage != null &&
                    this.TextUnitALanguage.Equals(input.TextUnitALanguage))
                ) && 
                (
                    this.TextUnitATextunittextText == input.TextUnitATextunittextText ||
                    (this.TextUnitATextunittextText != null &&
                    this.TextUnitATextunittextText.Equals(input.TextUnitATextunittextText))
                ) && 
                (
                    this.DocumentAId == input.DocumentAId ||
                    (this.DocumentAId != null &&
                    this.DocumentAId.Equals(input.DocumentAId))
                ) && 
                (
                    this.DocumentAName == input.DocumentAName ||
                    (this.DocumentAName != null &&
                    this.DocumentAName.Equals(input.DocumentAName))
                ) && 
                (
                    this.TextUnitBId == input.TextUnitBId ||
                    (this.TextUnitBId != null &&
                    this.TextUnitBId.Equals(input.TextUnitBId))
                ) && 
                (
                    this.TextUnitBUnitType == input.TextUnitBUnitType ||
                    (this.TextUnitBUnitType != null &&
                    this.TextUnitBUnitType.Equals(input.TextUnitBUnitType))
                ) && 
                (
                    this.TextUnitBLanguage == input.TextUnitBLanguage ||
                    (this.TextUnitBLanguage != null &&
                    this.TextUnitBLanguage.Equals(input.TextUnitBLanguage))
                ) && 
                (
                    this.TextUnitBTextunittextText == input.TextUnitBTextunittextText ||
                    (this.TextUnitBTextunittextText != null &&
                    this.TextUnitBTextunittextText.Equals(input.TextUnitBTextunittextText))
                ) && 
                (
                    this.DocumentBId == input.DocumentBId ||
                    (this.DocumentBId != null &&
                    this.DocumentBId.Equals(input.DocumentBId))
                ) && 
                (
                    this.DocumentBName == input.DocumentBName ||
                    (this.DocumentBName != null &&
                    this.DocumentBName.Equals(input.DocumentBName))
                ) && 
                (
                    this.Similarity == input.Similarity ||
                    (this.Similarity != null &&
                    this.Similarity.Equals(input.Similarity))
                ) && 
                (
                    this.Run == input.Run ||
                    (this.Run != null &&
                    this.Run.Equals(input.Run))
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
                if (this.TextUnitAId != null)
                    hashCode = hashCode * 59 + this.TextUnitAId.GetHashCode();
                if (this.TextUnitAUnitType != null)
                    hashCode = hashCode * 59 + this.TextUnitAUnitType.GetHashCode();
                if (this.TextUnitALanguage != null)
                    hashCode = hashCode * 59 + this.TextUnitALanguage.GetHashCode();
                if (this.TextUnitATextunittextText != null)
                    hashCode = hashCode * 59 + this.TextUnitATextunittextText.GetHashCode();
                if (this.DocumentAId != null)
                    hashCode = hashCode * 59 + this.DocumentAId.GetHashCode();
                if (this.DocumentAName != null)
                    hashCode = hashCode * 59 + this.DocumentAName.GetHashCode();
                if (this.TextUnitBId != null)
                    hashCode = hashCode * 59 + this.TextUnitBId.GetHashCode();
                if (this.TextUnitBUnitType != null)
                    hashCode = hashCode * 59 + this.TextUnitBUnitType.GetHashCode();
                if (this.TextUnitBLanguage != null)
                    hashCode = hashCode * 59 + this.TextUnitBLanguage.GetHashCode();
                if (this.TextUnitBTextunittextText != null)
                    hashCode = hashCode * 59 + this.TextUnitBTextunittextText.GetHashCode();
                if (this.DocumentBId != null)
                    hashCode = hashCode * 59 + this.DocumentBId.GetHashCode();
                if (this.DocumentBName != null)
                    hashCode = hashCode * 59 + this.DocumentBName.GetHashCode();
                if (this.Similarity != null)
                    hashCode = hashCode * 59 + this.Similarity.GetHashCode();
                if (this.Run != null)
                    hashCode = hashCode * 59 + this.Run.GetHashCode();
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
