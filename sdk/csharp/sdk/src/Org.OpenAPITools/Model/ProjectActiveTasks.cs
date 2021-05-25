/*
 * Contraxsuite API
 *
 * Contraxsuite API
 *
 * The version of the OpenAPI document: 2.0.0
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
    /// ProjectActiveTasks
    /// </summary>
    [DataContract]
    public partial class ProjectActiveTasks :  IEquatable<ProjectActiveTasks>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="ProjectActiveTasks" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected ProjectActiveTasks() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="ProjectActiveTasks" /> class.
        /// </summary>
        /// <param name="tasks">tasks (required).</param>
        /// <param name="documentTransformerChangeInProgress">documentTransformerChangeInProgress (required).</param>
        /// <param name="textUnitTransformerChangeInProgress">textUnitTransformerChangeInProgress (required).</param>
        /// <param name="locateTermsInProgress">locateTermsInProgress (required).</param>
        /// <param name="locateCompaniesInProgress">locateCompaniesInProgress (required).</param>
        public ProjectActiveTasks(ProjectActiveTasksTasks tasks = default(ProjectActiveTasksTasks), bool documentTransformerChangeInProgress = default(bool), bool textUnitTransformerChangeInProgress = default(bool), bool locateTermsInProgress = default(bool), bool locateCompaniesInProgress = default(bool))
        {
            // to ensure "tasks" is required (not null)
            if (tasks == null)
            {
                throw new InvalidDataException("tasks is a required property for ProjectActiveTasks and cannot be null");
            }
            else
            {
                this.Tasks = tasks;
            }

            // to ensure "documentTransformerChangeInProgress" is required (not null)
            if (documentTransformerChangeInProgress == null)
            {
                throw new InvalidDataException("documentTransformerChangeInProgress is a required property for ProjectActiveTasks and cannot be null");
            }
            else
            {
                this.DocumentTransformerChangeInProgress = documentTransformerChangeInProgress;
            }

            // to ensure "textUnitTransformerChangeInProgress" is required (not null)
            if (textUnitTransformerChangeInProgress == null)
            {
                throw new InvalidDataException("textUnitTransformerChangeInProgress is a required property for ProjectActiveTasks and cannot be null");
            }
            else
            {
                this.TextUnitTransformerChangeInProgress = textUnitTransformerChangeInProgress;
            }

            // to ensure "locateTermsInProgress" is required (not null)
            if (locateTermsInProgress == null)
            {
                throw new InvalidDataException("locateTermsInProgress is a required property for ProjectActiveTasks and cannot be null");
            }
            else
            {
                this.LocateTermsInProgress = locateTermsInProgress;
            }

            // to ensure "locateCompaniesInProgress" is required (not null)
            if (locateCompaniesInProgress == null)
            {
                throw new InvalidDataException("locateCompaniesInProgress is a required property for ProjectActiveTasks and cannot be null");
            }
            else
            {
                this.LocateCompaniesInProgress = locateCompaniesInProgress;
            }

        }

        /// <summary>
        /// Gets or Sets Tasks
        /// </summary>
        [DataMember(Name="tasks", EmitDefaultValue=true)]
        public ProjectActiveTasksTasks Tasks { get; set; }

        /// <summary>
        /// Gets or Sets DocumentTransformerChangeInProgress
        /// </summary>
        [DataMember(Name="document_transformer_change_in_progress", EmitDefaultValue=true)]
        public bool DocumentTransformerChangeInProgress { get; set; }

        /// <summary>
        /// Gets or Sets TextUnitTransformerChangeInProgress
        /// </summary>
        [DataMember(Name="text_unit_transformer_change_in_progress", EmitDefaultValue=true)]
        public bool TextUnitTransformerChangeInProgress { get; set; }

        /// <summary>
        /// Gets or Sets LocateTermsInProgress
        /// </summary>
        [DataMember(Name="locate_terms_in_progress", EmitDefaultValue=true)]
        public bool LocateTermsInProgress { get; set; }

        /// <summary>
        /// Gets or Sets LocateCompaniesInProgress
        /// </summary>
        [DataMember(Name="locate_companies_in_progress", EmitDefaultValue=true)]
        public bool LocateCompaniesInProgress { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class ProjectActiveTasks {\n");
            sb.Append("  Tasks: ").Append(Tasks).Append("\n");
            sb.Append("  DocumentTransformerChangeInProgress: ").Append(DocumentTransformerChangeInProgress).Append("\n");
            sb.Append("  TextUnitTransformerChangeInProgress: ").Append(TextUnitTransformerChangeInProgress).Append("\n");
            sb.Append("  LocateTermsInProgress: ").Append(LocateTermsInProgress).Append("\n");
            sb.Append("  LocateCompaniesInProgress: ").Append(LocateCompaniesInProgress).Append("\n");
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
            return this.Equals(input as ProjectActiveTasks);
        }

        /// <summary>
        /// Returns true if ProjectActiveTasks instances are equal
        /// </summary>
        /// <param name="input">Instance of ProjectActiveTasks to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(ProjectActiveTasks input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.Tasks == input.Tasks ||
                    (this.Tasks != null &&
                    this.Tasks.Equals(input.Tasks))
                ) && 
                (
                    this.DocumentTransformerChangeInProgress == input.DocumentTransformerChangeInProgress ||
                    (this.DocumentTransformerChangeInProgress != null &&
                    this.DocumentTransformerChangeInProgress.Equals(input.DocumentTransformerChangeInProgress))
                ) && 
                (
                    this.TextUnitTransformerChangeInProgress == input.TextUnitTransformerChangeInProgress ||
                    (this.TextUnitTransformerChangeInProgress != null &&
                    this.TextUnitTransformerChangeInProgress.Equals(input.TextUnitTransformerChangeInProgress))
                ) && 
                (
                    this.LocateTermsInProgress == input.LocateTermsInProgress ||
                    (this.LocateTermsInProgress != null &&
                    this.LocateTermsInProgress.Equals(input.LocateTermsInProgress))
                ) && 
                (
                    this.LocateCompaniesInProgress == input.LocateCompaniesInProgress ||
                    (this.LocateCompaniesInProgress != null &&
                    this.LocateCompaniesInProgress.Equals(input.LocateCompaniesInProgress))
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
                if (this.Tasks != null)
                    hashCode = hashCode * 59 + this.Tasks.GetHashCode();
                if (this.DocumentTransformerChangeInProgress != null)
                    hashCode = hashCode * 59 + this.DocumentTransformerChangeInProgress.GetHashCode();
                if (this.TextUnitTransformerChangeInProgress != null)
                    hashCode = hashCode * 59 + this.TextUnitTransformerChangeInProgress.GetHashCode();
                if (this.LocateTermsInProgress != null)
                    hashCode = hashCode * 59 + this.LocateTermsInProgress.GetHashCode();
                if (this.LocateCompaniesInProgress != null)
                    hashCode = hashCode * 59 + this.LocateCompaniesInProgress.GetHashCode();
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