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
    /// DocumentFieldValue
    /// </summary>
    [DataContract]
    public partial class DocumentFieldValue :  IEquatable<DocumentFieldValue>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="DocumentFieldValue" /> class.
        /// </summary>
        /// <param name="value">value.</param>
        public DocumentFieldValue(Object value = default(Object))
        {
            this.Value = value;
            this.Value = value;
        }

        /// <summary>
        /// Gets or Sets Pk
        /// </summary>
        [DataMember(Name="pk", EmitDefaultValue=false)]
        public int Pk { get; private set; }

        /// <summary>
        /// Gets or Sets ProjectId
        /// </summary>
        [DataMember(Name="project_id", EmitDefaultValue=false)]
        public int ProjectId { get; private set; }

        /// <summary>
        /// Gets or Sets Project
        /// </summary>
        [DataMember(Name="project", EmitDefaultValue=false)]
        public string Project { get; private set; }

        /// <summary>
        /// Gets or Sets DocumentId
        /// </summary>
        [DataMember(Name="document_id", EmitDefaultValue=false)]
        public string DocumentId { get; private set; }

        /// <summary>
        /// Gets or Sets DocumentName
        /// </summary>
        [DataMember(Name="document_name", EmitDefaultValue=false)]
        public string DocumentName { get; private set; }

        /// <summary>
        /// Gets or Sets DocumentStatus
        /// </summary>
        [DataMember(Name="document_status", EmitDefaultValue=false)]
        public string DocumentStatus { get; private set; }

        /// <summary>
        /// Gets or Sets FieldId
        /// </summary>
        [DataMember(Name="field_id", EmitDefaultValue=false)]
        public string FieldId { get; private set; }

        /// <summary>
        /// Gets or Sets FieldName
        /// </summary>
        [DataMember(Name="field_name", EmitDefaultValue=false)]
        public string FieldName { get; private set; }

        /// <summary>
        /// Gets or Sets Value
        /// </summary>
        [DataMember(Name="value", EmitDefaultValue=true)]
        public Object Value { get; set; }

        /// <summary>
        /// Gets or Sets PythonValue
        /// </summary>
        [DataMember(Name="python_value", EmitDefaultValue=false)]
        public string PythonValue { get; private set; }

        /// <summary>
        /// Gets or Sets LocationText
        /// </summary>
        [DataMember(Name="location_text", EmitDefaultValue=false)]
        public string LocationText { get; private set; }

        /// <summary>
        /// Gets or Sets ModifiedByUsername
        /// </summary>
        [DataMember(Name="modified_by_username", EmitDefaultValue=false)]
        public string ModifiedByUsername { get; private set; }

        /// <summary>
        /// Gets or Sets ModifiedById
        /// </summary>
        [DataMember(Name="modified_by_id", EmitDefaultValue=false)]
        public string ModifiedById { get; private set; }

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
            sb.Append("class DocumentFieldValue {\n");
            sb.Append("  Pk: ").Append(Pk).Append("\n");
            sb.Append("  ProjectId: ").Append(ProjectId).Append("\n");
            sb.Append("  Project: ").Append(Project).Append("\n");
            sb.Append("  DocumentId: ").Append(DocumentId).Append("\n");
            sb.Append("  DocumentName: ").Append(DocumentName).Append("\n");
            sb.Append("  DocumentStatus: ").Append(DocumentStatus).Append("\n");
            sb.Append("  FieldId: ").Append(FieldId).Append("\n");
            sb.Append("  FieldName: ").Append(FieldName).Append("\n");
            sb.Append("  Value: ").Append(Value).Append("\n");
            sb.Append("  PythonValue: ").Append(PythonValue).Append("\n");
            sb.Append("  LocationText: ").Append(LocationText).Append("\n");
            sb.Append("  ModifiedByUsername: ").Append(ModifiedByUsername).Append("\n");
            sb.Append("  ModifiedById: ").Append(ModifiedById).Append("\n");
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
            return this.Equals(input as DocumentFieldValue);
        }

        /// <summary>
        /// Returns true if DocumentFieldValue instances are equal
        /// </summary>
        /// <param name="input">Instance of DocumentFieldValue to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(DocumentFieldValue input)
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
                    this.ProjectId == input.ProjectId ||
                    (this.ProjectId != null &&
                    this.ProjectId.Equals(input.ProjectId))
                ) && 
                (
                    this.Project == input.Project ||
                    (this.Project != null &&
                    this.Project.Equals(input.Project))
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
                ) && 
                (
                    this.DocumentStatus == input.DocumentStatus ||
                    (this.DocumentStatus != null &&
                    this.DocumentStatus.Equals(input.DocumentStatus))
                ) && 
                (
                    this.FieldId == input.FieldId ||
                    (this.FieldId != null &&
                    this.FieldId.Equals(input.FieldId))
                ) && 
                (
                    this.FieldName == input.FieldName ||
                    (this.FieldName != null &&
                    this.FieldName.Equals(input.FieldName))
                ) && 
                (
                    this.Value == input.Value ||
                    (this.Value != null &&
                    this.Value.Equals(input.Value))
                ) && 
                (
                    this.PythonValue == input.PythonValue ||
                    (this.PythonValue != null &&
                    this.PythonValue.Equals(input.PythonValue))
                ) && 
                (
                    this.LocationText == input.LocationText ||
                    (this.LocationText != null &&
                    this.LocationText.Equals(input.LocationText))
                ) && 
                (
                    this.ModifiedByUsername == input.ModifiedByUsername ||
                    (this.ModifiedByUsername != null &&
                    this.ModifiedByUsername.Equals(input.ModifiedByUsername))
                ) && 
                (
                    this.ModifiedById == input.ModifiedById ||
                    (this.ModifiedById != null &&
                    this.ModifiedById.Equals(input.ModifiedById))
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
                if (this.ProjectId != null)
                    hashCode = hashCode * 59 + this.ProjectId.GetHashCode();
                if (this.Project != null)
                    hashCode = hashCode * 59 + this.Project.GetHashCode();
                if (this.DocumentId != null)
                    hashCode = hashCode * 59 + this.DocumentId.GetHashCode();
                if (this.DocumentName != null)
                    hashCode = hashCode * 59 + this.DocumentName.GetHashCode();
                if (this.DocumentStatus != null)
                    hashCode = hashCode * 59 + this.DocumentStatus.GetHashCode();
                if (this.FieldId != null)
                    hashCode = hashCode * 59 + this.FieldId.GetHashCode();
                if (this.FieldName != null)
                    hashCode = hashCode * 59 + this.FieldName.GetHashCode();
                if (this.Value != null)
                    hashCode = hashCode * 59 + this.Value.GetHashCode();
                if (this.PythonValue != null)
                    hashCode = hashCode * 59 + this.PythonValue.GetHashCode();
                if (this.LocationText != null)
                    hashCode = hashCode * 59 + this.LocationText.GetHashCode();
                if (this.ModifiedByUsername != null)
                    hashCode = hashCode * 59 + this.ModifiedByUsername.GetHashCode();
                if (this.ModifiedById != null)
                    hashCode = hashCode * 59 + this.ModifiedById.GetHashCode();
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
            yield break;
        }
    }

}
