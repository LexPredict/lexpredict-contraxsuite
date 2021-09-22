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
    /// TextUnitDjangoQL
    /// </summary>
    [DataContract]
    public partial class TextUnitDjangoQL :  IEquatable<TextUnitDjangoQL>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="TextUnitDjangoQL" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected TextUnitDjangoQL() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="TextUnitDjangoQL" /> class.
        /// </summary>
        /// <param name="unitType">unitType (required).</param>
        /// <param name="projectName">projectName (required).</param>
        /// <param name="documentName">documentName (required).</param>
        public TextUnitDjangoQL(string unitType = default(string), string projectName = default(string), string documentName = default(string))
        {
            // to ensure "unitType" is required (not null)
            if (unitType == null)
            {
                throw new InvalidDataException("unitType is a required property for TextUnitDjangoQL and cannot be null");
            }
            else
            {
                this.UnitType = unitType;
            }

            // to ensure "projectName" is required (not null)
            if (projectName == null)
            {
                throw new InvalidDataException("projectName is a required property for TextUnitDjangoQL and cannot be null");
            }
            else
            {
                this.ProjectName = projectName;
            }

            // to ensure "documentName" is required (not null)
            if (documentName == null)
            {
                throw new InvalidDataException("documentName is a required property for TextUnitDjangoQL and cannot be null");
            }
            else
            {
                this.DocumentName = documentName;
            }

        }

        /// <summary>
        /// Gets or Sets Id
        /// </summary>
        [DataMember(Name="id", EmitDefaultValue=false)]
        public int Id { get; private set; }

        /// <summary>
        /// Gets or Sets UnitType
        /// </summary>
        [DataMember(Name="unit_type", EmitDefaultValue=true)]
        public string UnitType { get; set; }

        /// <summary>
        /// Gets or Sets Text
        /// </summary>
        [DataMember(Name="text", EmitDefaultValue=false)]
        public string Text { get; private set; }

        /// <summary>
        /// Gets or Sets ProjectId
        /// </summary>
        [DataMember(Name="project_id", EmitDefaultValue=false)]
        public string ProjectId { get; private set; }

        /// <summary>
        /// Gets or Sets ProjectName
        /// </summary>
        [DataMember(Name="project_name", EmitDefaultValue=true)]
        public string ProjectName { get; set; }

        /// <summary>
        /// Gets or Sets DocumentId
        /// </summary>
        [DataMember(Name="document_id", EmitDefaultValue=false)]
        public string DocumentId { get; private set; }

        /// <summary>
        /// Gets or Sets DocumentName
        /// </summary>
        [DataMember(Name="document_name", EmitDefaultValue=true)]
        public string DocumentName { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class TextUnitDjangoQL {\n");
            sb.Append("  Id: ").Append(Id).Append("\n");
            sb.Append("  UnitType: ").Append(UnitType).Append("\n");
            sb.Append("  Text: ").Append(Text).Append("\n");
            sb.Append("  ProjectId: ").Append(ProjectId).Append("\n");
            sb.Append("  ProjectName: ").Append(ProjectName).Append("\n");
            sb.Append("  DocumentId: ").Append(DocumentId).Append("\n");
            sb.Append("  DocumentName: ").Append(DocumentName).Append("\n");
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
            return this.Equals(input as TextUnitDjangoQL);
        }

        /// <summary>
        /// Returns true if TextUnitDjangoQL instances are equal
        /// </summary>
        /// <param name="input">Instance of TextUnitDjangoQL to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(TextUnitDjangoQL input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.Id == input.Id ||
                    (this.Id != null &&
                    this.Id.Equals(input.Id))
                ) && 
                (
                    this.UnitType == input.UnitType ||
                    (this.UnitType != null &&
                    this.UnitType.Equals(input.UnitType))
                ) && 
                (
                    this.Text == input.Text ||
                    (this.Text != null &&
                    this.Text.Equals(input.Text))
                ) && 
                (
                    this.ProjectId == input.ProjectId ||
                    (this.ProjectId != null &&
                    this.ProjectId.Equals(input.ProjectId))
                ) && 
                (
                    this.ProjectName == input.ProjectName ||
                    (this.ProjectName != null &&
                    this.ProjectName.Equals(input.ProjectName))
                ) && 
                (
                    this.DocumentId == input.DocumentId ||
                    (this.DocumentId != null &&
                    this.DocumentId.Equals(input.DocumentId))
                ) && 
                (
                    this.DocumentName == input.DocumentName ||
                    (this.DocumentName != null &&
                    this.DocumentName.Equals(input.DocumentName))
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
                if (this.Id != null)
                    hashCode = hashCode * 59 + this.Id.GetHashCode();
                if (this.UnitType != null)
                    hashCode = hashCode * 59 + this.UnitType.GetHashCode();
                if (this.Text != null)
                    hashCode = hashCode * 59 + this.Text.GetHashCode();
                if (this.ProjectId != null)
                    hashCode = hashCode * 59 + this.ProjectId.GetHashCode();
                if (this.ProjectName != null)
                    hashCode = hashCode * 59 + this.ProjectName.GetHashCode();
                if (this.DocumentId != null)
                    hashCode = hashCode * 59 + this.DocumentId.GetHashCode();
                if (this.DocumentName != null)
                    hashCode = hashCode * 59 + this.DocumentName.GetHashCode();
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
            // UnitType (string) maxLength
            if(this.UnitType != null && this.UnitType.Length > 128)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for UnitType, length must be less than 128.", new [] { "UnitType" });
            }

 
            yield break;
        }
    }

}
