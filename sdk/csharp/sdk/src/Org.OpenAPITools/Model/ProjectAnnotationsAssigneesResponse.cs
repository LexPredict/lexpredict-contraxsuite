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
    /// ProjectAnnotationsAssigneesResponse
    /// </summary>
    [DataContract]
    public partial class ProjectAnnotationsAssigneesResponse :  IEquatable<ProjectAnnotationsAssigneesResponse>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="ProjectAnnotationsAssigneesResponse" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected ProjectAnnotationsAssigneesResponse() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="ProjectAnnotationsAssigneesResponse" /> class.
        /// </summary>
        /// <param name="assigneeId">assigneeId (required).</param>
        /// <param name="assigneeName">assigneeName (required).</param>
        /// <param name="annotationsCount">annotationsCount (required).</param>
        /// <param name="annotationUids">annotationUids (required).</param>
        public ProjectAnnotationsAssigneesResponse(int assigneeId = default(int), string assigneeName = default(string), int annotationsCount = default(int), List<Guid> annotationUids = default(List<Guid>))
        {
            // to ensure "assigneeId" is required (not null)
            if (assigneeId == null)
            {
                throw new InvalidDataException("assigneeId is a required property for ProjectAnnotationsAssigneesResponse and cannot be null");
            }
            else
            {
                this.AssigneeId = assigneeId;
            }

            // to ensure "assigneeName" is required (not null)
            if (assigneeName == null)
            {
                throw new InvalidDataException("assigneeName is a required property for ProjectAnnotationsAssigneesResponse and cannot be null");
            }
            else
            {
                this.AssigneeName = assigneeName;
            }

            // to ensure "annotationsCount" is required (not null)
            if (annotationsCount == null)
            {
                throw new InvalidDataException("annotationsCount is a required property for ProjectAnnotationsAssigneesResponse and cannot be null");
            }
            else
            {
                this.AnnotationsCount = annotationsCount;
            }

            // to ensure "annotationUids" is required (not null)
            if (annotationUids == null)
            {
                throw new InvalidDataException("annotationUids is a required property for ProjectAnnotationsAssigneesResponse and cannot be null");
            }
            else
            {
                this.AnnotationUids = annotationUids;
            }

        }

        /// <summary>
        /// Gets or Sets AssigneeId
        /// </summary>
        [DataMember(Name="assignee_id", EmitDefaultValue=true)]
        public int AssigneeId { get; set; }

        /// <summary>
        /// Gets or Sets AssigneeName
        /// </summary>
        [DataMember(Name="assignee_name", EmitDefaultValue=true)]
        public string AssigneeName { get; set; }

        /// <summary>
        /// Gets or Sets AnnotationsCount
        /// </summary>
        [DataMember(Name="annotations_count", EmitDefaultValue=true)]
        public int AnnotationsCount { get; set; }

        /// <summary>
        /// Gets or Sets AnnotationUids
        /// </summary>
        [DataMember(Name="annotation_uids", EmitDefaultValue=true)]
        public List<Guid> AnnotationUids { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class ProjectAnnotationsAssigneesResponse {\n");
            sb.Append("  AssigneeId: ").Append(AssigneeId).Append("\n");
            sb.Append("  AssigneeName: ").Append(AssigneeName).Append("\n");
            sb.Append("  AnnotationsCount: ").Append(AnnotationsCount).Append("\n");
            sb.Append("  AnnotationUids: ").Append(AnnotationUids).Append("\n");
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
            return this.Equals(input as ProjectAnnotationsAssigneesResponse);
        }

        /// <summary>
        /// Returns true if ProjectAnnotationsAssigneesResponse instances are equal
        /// </summary>
        /// <param name="input">Instance of ProjectAnnotationsAssigneesResponse to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(ProjectAnnotationsAssigneesResponse input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.AssigneeId == input.AssigneeId ||
                    (this.AssigneeId != null &&
                    this.AssigneeId.Equals(input.AssigneeId))
                ) && 
                (
                    this.AssigneeName == input.AssigneeName ||
                    (this.AssigneeName != null &&
                    this.AssigneeName.Equals(input.AssigneeName))
                ) && 
                (
                    this.AnnotationsCount == input.AnnotationsCount ||
                    (this.AnnotationsCount != null &&
                    this.AnnotationsCount.Equals(input.AnnotationsCount))
                ) && 
                (
                    this.AnnotationUids == input.AnnotationUids ||
                    this.AnnotationUids != null &&
                    input.AnnotationUids != null &&
                    this.AnnotationUids.SequenceEqual(input.AnnotationUids)
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
                if (this.AssigneeId != null)
                    hashCode = hashCode * 59 + this.AssigneeId.GetHashCode();
                if (this.AssigneeName != null)
                    hashCode = hashCode * 59 + this.AssigneeName.GetHashCode();
                if (this.AnnotationsCount != null)
                    hashCode = hashCode * 59 + this.AnnotationsCount.GetHashCode();
                if (this.AnnotationUids != null)
                    hashCode = hashCode * 59 + this.AnnotationUids.GetHashCode();
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
