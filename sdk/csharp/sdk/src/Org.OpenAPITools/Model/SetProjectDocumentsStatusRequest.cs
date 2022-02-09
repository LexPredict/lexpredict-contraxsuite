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
    /// SetProjectDocumentsStatusRequest
    /// </summary>
    [DataContract]
    public partial class SetProjectDocumentsStatusRequest :  IEquatable<SetProjectDocumentsStatusRequest>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="SetProjectDocumentsStatusRequest" /> class.
        /// </summary>
        /// <param name="statusId">statusId.</param>
        /// <param name="all">all.</param>
        /// <param name="documentIds">documentIds.</param>
        /// <param name="noDocumentIds">noDocumentIds.</param>
        public SetProjectDocumentsStatusRequest(int? statusId = default(int?), bool all = default(bool), List<int> documentIds = default(List<int>), List<int> noDocumentIds = default(List<int>))
        {
            this.StatusId = statusId;
            this.StatusId = statusId;
            this.All = all;
            this.DocumentIds = documentIds;
            this.NoDocumentIds = noDocumentIds;
        }

        /// <summary>
        /// Gets or Sets StatusId
        /// </summary>
        [DataMember(Name="status_id", EmitDefaultValue=true)]
        public int? StatusId { get; set; }

        /// <summary>
        /// Gets or Sets All
        /// </summary>
        [DataMember(Name="all", EmitDefaultValue=false)]
        public bool All { get; set; }

        /// <summary>
        /// Gets or Sets DocumentIds
        /// </summary>
        [DataMember(Name="document_ids", EmitDefaultValue=false)]
        public List<int> DocumentIds { get; set; }

        /// <summary>
        /// Gets or Sets NoDocumentIds
        /// </summary>
        [DataMember(Name="no_document_ids", EmitDefaultValue=false)]
        public List<int> NoDocumentIds { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class SetProjectDocumentsStatusRequest {\n");
            sb.Append("  StatusId: ").Append(StatusId).Append("\n");
            sb.Append("  All: ").Append(All).Append("\n");
            sb.Append("  DocumentIds: ").Append(DocumentIds).Append("\n");
            sb.Append("  NoDocumentIds: ").Append(NoDocumentIds).Append("\n");
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
            return this.Equals(input as SetProjectDocumentsStatusRequest);
        }

        /// <summary>
        /// Returns true if SetProjectDocumentsStatusRequest instances are equal
        /// </summary>
        /// <param name="input">Instance of SetProjectDocumentsStatusRequest to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(SetProjectDocumentsStatusRequest input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.StatusId == input.StatusId ||
                    (this.StatusId != null &&
                    this.StatusId.Equals(input.StatusId))
                ) && 
                (
                    this.All == input.All ||
                    (this.All != null &&
                    this.All.Equals(input.All))
                ) && 
                (
                    this.DocumentIds == input.DocumentIds ||
                    this.DocumentIds != null &&
                    input.DocumentIds != null &&
                    this.DocumentIds.SequenceEqual(input.DocumentIds)
                ) && 
                (
                    this.NoDocumentIds == input.NoDocumentIds ||
                    this.NoDocumentIds != null &&
                    input.NoDocumentIds != null &&
                    this.NoDocumentIds.SequenceEqual(input.NoDocumentIds)
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
                if (this.StatusId != null)
                    hashCode = hashCode * 59 + this.StatusId.GetHashCode();
                if (this.All != null)
                    hashCode = hashCode * 59 + this.All.GetHashCode();
                if (this.DocumentIds != null)
                    hashCode = hashCode * 59 + this.DocumentIds.GetHashCode();
                if (this.NoDocumentIds != null)
                    hashCode = hashCode * 59 + this.NoDocumentIds.GetHashCode();
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
