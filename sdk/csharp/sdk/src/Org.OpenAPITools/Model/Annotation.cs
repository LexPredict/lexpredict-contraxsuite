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
    /// Annotation
    /// </summary>
    [DataContract]
    public partial class Annotation :  IEquatable<Annotation>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="Annotation" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected Annotation() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="Annotation" /> class.
        /// </summary>
        /// <param name="document">document (required).</param>
        /// <param name="field">field (required).</param>
        /// <param name="value">value (required).</param>
        /// <param name="locationStart">locationStart (required).</param>
        /// <param name="locationEnd">locationEnd (required).</param>
        /// <param name="locationText">locationText.</param>
        /// <param name="modifiedBy">modifiedBy.</param>
        public Annotation(int document = default(int), string field = default(string), Object value = default(Object), int? locationStart = default(int?), int? locationEnd = default(int?), string locationText = default(string), int? modifiedBy = default(int?))
        {
            // to ensure "document" is required (not null)
            if (document == null)
            {
                throw new InvalidDataException("document is a required property for Annotation and cannot be null");
            }
            else
            {
                this.Document = document;
            }

            // to ensure "field" is required (not null)
            if (field == null)
            {
                throw new InvalidDataException("field is a required property for Annotation and cannot be null");
            }
            else
            {
                this.Field = field;
            }

            // to ensure "value" is required (not null)
            if (value == null)
            {
                throw new InvalidDataException("value is a required property for Annotation and cannot be null");
            }
            else
            {
                this.Value = value;
            }

            this.Value = value;
            // to ensure "locationStart" is required (not null)
            if (locationStart == null)
            {
                throw new InvalidDataException("locationStart is a required property for Annotation and cannot be null");
            }
            else
            {
                this.LocationStart = locationStart;
            }

            this.LocationStart = locationStart;
            // to ensure "locationEnd" is required (not null)
            if (locationEnd == null)
            {
                throw new InvalidDataException("locationEnd is a required property for Annotation and cannot be null");
            }
            else
            {
                this.LocationEnd = locationEnd;
            }

            this.LocationEnd = locationEnd;
            this.LocationText = locationText;
            this.ModifiedBy = modifiedBy;
            this.LocationText = locationText;
            this.ModifiedBy = modifiedBy;
        }

        /// <summary>
        /// Gets or Sets Pk
        /// </summary>
        [DataMember(Name="pk", EmitDefaultValue=false)]
        public int Pk { get; private set; }

        /// <summary>
        /// Gets or Sets Document
        /// </summary>
        [DataMember(Name="document", EmitDefaultValue=true)]
        public int Document { get; set; }

        /// <summary>
        /// Gets or Sets Field
        /// </summary>
        [DataMember(Name="field", EmitDefaultValue=true)]
        public string Field { get; set; }

        /// <summary>
        /// Gets or Sets Value
        /// </summary>
        [DataMember(Name="value", EmitDefaultValue=true)]
        public Object Value { get; set; }

        /// <summary>
        /// Gets or Sets LocationStart
        /// </summary>
        [DataMember(Name="location_start", EmitDefaultValue=true)]
        public int? LocationStart { get; set; }

        /// <summary>
        /// Gets or Sets LocationEnd
        /// </summary>
        [DataMember(Name="location_end", EmitDefaultValue=true)]
        public int? LocationEnd { get; set; }

        /// <summary>
        /// Gets or Sets LocationText
        /// </summary>
        [DataMember(Name="location_text", EmitDefaultValue=true)]
        public string LocationText { get; set; }

        /// <summary>
        /// Gets or Sets ModifiedBy
        /// </summary>
        [DataMember(Name="modified_by", EmitDefaultValue=true)]
        public int? ModifiedBy { get; set; }

        /// <summary>
        /// Gets or Sets ModifiedDate
        /// </summary>
        [DataMember(Name="modified_date", EmitDefaultValue=false)]
        public DateTime ModifiedDate { get; private set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class Annotation {\n");
            sb.Append("  Pk: ").Append(Pk).Append("\n");
            sb.Append("  Document: ").Append(Document).Append("\n");
            sb.Append("  Field: ").Append(Field).Append("\n");
            sb.Append("  Value: ").Append(Value).Append("\n");
            sb.Append("  LocationStart: ").Append(LocationStart).Append("\n");
            sb.Append("  LocationEnd: ").Append(LocationEnd).Append("\n");
            sb.Append("  LocationText: ").Append(LocationText).Append("\n");
            sb.Append("  ModifiedBy: ").Append(ModifiedBy).Append("\n");
            sb.Append("  ModifiedDate: ").Append(ModifiedDate).Append("\n");
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
            return this.Equals(input as Annotation);
        }

        /// <summary>
        /// Returns true if Annotation instances are equal
        /// </summary>
        /// <param name="input">Instance of Annotation to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(Annotation input)
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
                    this.Document == input.Document ||
                    (this.Document != null &&
                    this.Document.Equals(input.Document))
                ) && 
                (
                    this.Field == input.Field ||
                    (this.Field != null &&
                    this.Field.Equals(input.Field))
                ) && 
                (
                    this.Value == input.Value ||
                    (this.Value != null &&
                    this.Value.Equals(input.Value))
                ) && 
                (
                    this.LocationStart == input.LocationStart ||
                    (this.LocationStart != null &&
                    this.LocationStart.Equals(input.LocationStart))
                ) && 
                (
                    this.LocationEnd == input.LocationEnd ||
                    (this.LocationEnd != null &&
                    this.LocationEnd.Equals(input.LocationEnd))
                ) && 
                (
                    this.LocationText == input.LocationText ||
                    (this.LocationText != null &&
                    this.LocationText.Equals(input.LocationText))
                ) && 
                (
                    this.ModifiedBy == input.ModifiedBy ||
                    (this.ModifiedBy != null &&
                    this.ModifiedBy.Equals(input.ModifiedBy))
                ) && 
                (
                    this.ModifiedDate == input.ModifiedDate ||
                    (this.ModifiedDate != null &&
                    this.ModifiedDate.Equals(input.ModifiedDate))
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
                if (this.Document != null)
                    hashCode = hashCode * 59 + this.Document.GetHashCode();
                if (this.Field != null)
                    hashCode = hashCode * 59 + this.Field.GetHashCode();
                if (this.Value != null)
                    hashCode = hashCode * 59 + this.Value.GetHashCode();
                if (this.LocationStart != null)
                    hashCode = hashCode * 59 + this.LocationStart.GetHashCode();
                if (this.LocationEnd != null)
                    hashCode = hashCode * 59 + this.LocationEnd.GetHashCode();
                if (this.LocationText != null)
                    hashCode = hashCode * 59 + this.LocationText.GetHashCode();
                if (this.ModifiedBy != null)
                    hashCode = hashCode * 59 + this.ModifiedBy.GetHashCode();
                if (this.ModifiedDate != null)
                    hashCode = hashCode * 59 + this.ModifiedDate.GetHashCode();
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

 
            // LocationStart (int?) maximum
            if(this.LocationStart > (int?)2147483647)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for LocationStart, must be a value less than or equal to 2147483647.", new [] { "LocationStart" });
            }

            // LocationStart (int?) minimum
            if(this.LocationStart < (int?)0)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for LocationStart, must be a value greater than or equal to 0.", new [] { "LocationStart" });
            }


 
            // LocationEnd (int?) maximum
            if(this.LocationEnd > (int?)2147483647)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for LocationEnd, must be a value less than or equal to 2147483647.", new [] { "LocationEnd" });
            }

            // LocationEnd (int?) minimum
            if(this.LocationEnd < (int?)0)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for LocationEnd, must be a value greater than or equal to 0.", new [] { "LocationEnd" });
            }

            yield break;
        }
    }

}
