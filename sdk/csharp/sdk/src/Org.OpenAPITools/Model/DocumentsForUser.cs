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
    /// DocumentsForUser
    /// </summary>
    [DataContract]
    public partial class DocumentsForUser :  IEquatable<DocumentsForUser>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="DocumentsForUser" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected DocumentsForUser() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="DocumentsForUser" /> class.
        /// </summary>
        /// <param name="name">name.</param>
        /// <param name="documentType">documentType.</param>
        /// <param name="project">project.</param>
        /// <param name="statusName">statusName (required).</param>
        public DocumentsForUser(string name = default(string), string documentType = default(string), int? project = default(int?), string statusName = default(string))
        {
            this.Name = name;
            this.DocumentType = documentType;
            this.Project = project;
            // to ensure "statusName" is required (not null)
            if (statusName == null)
            {
                throw new InvalidDataException("statusName is a required property for DocumentsForUser and cannot be null");
            }
            else
            {
                this.StatusName = statusName;
            }

            this.Name = name;
            this.DocumentType = documentType;
            this.Project = project;
        }

        /// <summary>
        /// Gets or Sets Pk
        /// </summary>
        [DataMember(Name="pk", EmitDefaultValue=false)]
        public int Pk { get; private set; }

        /// <summary>
        /// Gets or Sets Name
        /// </summary>
        [DataMember(Name="name", EmitDefaultValue=true)]
        public string Name { get; set; }

        /// <summary>
        /// Gets or Sets DocumentType
        /// </summary>
        [DataMember(Name="document_type", EmitDefaultValue=true)]
        public string DocumentType { get; set; }

        /// <summary>
        /// Gets or Sets Project
        /// </summary>
        [DataMember(Name="project", EmitDefaultValue=true)]
        public int? Project { get; set; }

        /// <summary>
        /// Gets or Sets StatusName
        /// </summary>
        [DataMember(Name="status_name", EmitDefaultValue=true)]
        public string StatusName { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class DocumentsForUser {\n");
            sb.Append("  Pk: ").Append(Pk).Append("\n");
            sb.Append("  Name: ").Append(Name).Append("\n");
            sb.Append("  DocumentType: ").Append(DocumentType).Append("\n");
            sb.Append("  Project: ").Append(Project).Append("\n");
            sb.Append("  StatusName: ").Append(StatusName).Append("\n");
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
            return this.Equals(input as DocumentsForUser);
        }

        /// <summary>
        /// Returns true if DocumentsForUser instances are equal
        /// </summary>
        /// <param name="input">Instance of DocumentsForUser to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(DocumentsForUser input)
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
                    this.Name == input.Name ||
                    (this.Name != null &&
                    this.Name.Equals(input.Name))
                ) && 
                (
                    this.DocumentType == input.DocumentType ||
                    (this.DocumentType != null &&
                    this.DocumentType.Equals(input.DocumentType))
                ) && 
                (
                    this.Project == input.Project ||
                    (this.Project != null &&
                    this.Project.Equals(input.Project))
                ) && 
                (
                    this.StatusName == input.StatusName ||
                    (this.StatusName != null &&
                    this.StatusName.Equals(input.StatusName))
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
                if (this.Name != null)
                    hashCode = hashCode * 59 + this.Name.GetHashCode();
                if (this.DocumentType != null)
                    hashCode = hashCode * 59 + this.DocumentType.GetHashCode();
                if (this.Project != null)
                    hashCode = hashCode * 59 + this.Project.GetHashCode();
                if (this.StatusName != null)
                    hashCode = hashCode * 59 + this.StatusName.GetHashCode();
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
            // Name (string) maxLength
            if(this.Name != null && this.Name.Length > 1024)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for Name, length must be less than 1024.", new [] { "Name" });
            }

 
            yield break;
        }
    }

}
