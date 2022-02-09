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
    /// PartySimilarity
    /// </summary>
    [DataContract]
    public partial class PartySimilarity :  IEquatable<PartySimilarity>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="PartySimilarity" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected PartySimilarity() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="PartySimilarity" /> class.
        /// </summary>
        /// <param name="similarity">similarity (required).</param>
        /// <param name="run">run.</param>
        public PartySimilarity(decimal similarity = default(decimal), DocumentSimilarityRun run = default(DocumentSimilarityRun))
        {
            // to ensure "similarity" is required (not null)
            if (similarity == null)
            {
                throw new InvalidDataException("similarity is a required property for PartySimilarity and cannot be null");
            }
            else
            {
                this.Similarity = similarity;
            }

            this.Run = run;
        }

        /// <summary>
        /// Gets or Sets Pk
        /// </summary>
        [DataMember(Name="pk", EmitDefaultValue=false)]
        public int Pk { get; private set; }

        /// <summary>
        /// Gets or Sets PartyAName
        /// </summary>
        [DataMember(Name="party_a__name", EmitDefaultValue=false)]
        public string PartyAName { get; private set; }

        /// <summary>
        /// Gets or Sets PartyADescription
        /// </summary>
        [DataMember(Name="party_a__description", EmitDefaultValue=false)]
        public string PartyADescription { get; private set; }

        /// <summary>
        /// Gets or Sets PartyAPk
        /// </summary>
        [DataMember(Name="party_a__pk", EmitDefaultValue=false)]
        public string PartyAPk { get; private set; }

        /// <summary>
        /// Gets or Sets PartyATypeAbbr
        /// </summary>
        [DataMember(Name="party_a__type_abbr", EmitDefaultValue=false)]
        public string PartyATypeAbbr { get; private set; }

        /// <summary>
        /// Gets or Sets PartyBName
        /// </summary>
        [DataMember(Name="party_b__name", EmitDefaultValue=false)]
        public string PartyBName { get; private set; }

        /// <summary>
        /// Gets or Sets PartyBPk
        /// </summary>
        [DataMember(Name="party_b__pk", EmitDefaultValue=false)]
        public string PartyBPk { get; private set; }

        /// <summary>
        /// Gets or Sets PartyBTypeAbbr
        /// </summary>
        [DataMember(Name="party_b__type_abbr", EmitDefaultValue=false)]
        public string PartyBTypeAbbr { get; private set; }

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
            sb.Append("class PartySimilarity {\n");
            sb.Append("  Pk: ").Append(Pk).Append("\n");
            sb.Append("  PartyAName: ").Append(PartyAName).Append("\n");
            sb.Append("  PartyADescription: ").Append(PartyADescription).Append("\n");
            sb.Append("  PartyAPk: ").Append(PartyAPk).Append("\n");
            sb.Append("  PartyATypeAbbr: ").Append(PartyATypeAbbr).Append("\n");
            sb.Append("  PartyBName: ").Append(PartyBName).Append("\n");
            sb.Append("  PartyBPk: ").Append(PartyBPk).Append("\n");
            sb.Append("  PartyBTypeAbbr: ").Append(PartyBTypeAbbr).Append("\n");
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
            return this.Equals(input as PartySimilarity);
        }

        /// <summary>
        /// Returns true if PartySimilarity instances are equal
        /// </summary>
        /// <param name="input">Instance of PartySimilarity to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(PartySimilarity input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.Pk == input.Pk ||
                    (this.Pk != null &&
                    this.Pk.Equals(input.Pk))
                ) && 
                (
                    this.PartyAName == input.PartyAName ||
                    (this.PartyAName != null &&
                    this.PartyAName.Equals(input.PartyAName))
                ) && 
                (
                    this.PartyADescription == input.PartyADescription ||
                    (this.PartyADescription != null &&
                    this.PartyADescription.Equals(input.PartyADescription))
                ) && 
                (
                    this.PartyAPk == input.PartyAPk ||
                    (this.PartyAPk != null &&
                    this.PartyAPk.Equals(input.PartyAPk))
                ) && 
                (
                    this.PartyATypeAbbr == input.PartyATypeAbbr ||
                    (this.PartyATypeAbbr != null &&
                    this.PartyATypeAbbr.Equals(input.PartyATypeAbbr))
                ) && 
                (
                    this.PartyBName == input.PartyBName ||
                    (this.PartyBName != null &&
                    this.PartyBName.Equals(input.PartyBName))
                ) && 
                (
                    this.PartyBPk == input.PartyBPk ||
                    (this.PartyBPk != null &&
                    this.PartyBPk.Equals(input.PartyBPk))
                ) && 
                (
                    this.PartyBTypeAbbr == input.PartyBTypeAbbr ||
                    (this.PartyBTypeAbbr != null &&
                    this.PartyBTypeAbbr.Equals(input.PartyBTypeAbbr))
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
                if (this.Pk != null)
                    hashCode = hashCode * 59 + this.Pk.GetHashCode();
                if (this.PartyAName != null)
                    hashCode = hashCode * 59 + this.PartyAName.GetHashCode();
                if (this.PartyADescription != null)
                    hashCode = hashCode * 59 + this.PartyADescription.GetHashCode();
                if (this.PartyAPk != null)
                    hashCode = hashCode * 59 + this.PartyAPk.GetHashCode();
                if (this.PartyATypeAbbr != null)
                    hashCode = hashCode * 59 + this.PartyATypeAbbr.GetHashCode();
                if (this.PartyBName != null)
                    hashCode = hashCode * 59 + this.PartyBName.GetHashCode();
                if (this.PartyBPk != null)
                    hashCode = hashCode * 59 + this.PartyBPk.GetHashCode();
                if (this.PartyBTypeAbbr != null)
                    hashCode = hashCode * 59 + this.PartyBTypeAbbr.GetHashCode();
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
