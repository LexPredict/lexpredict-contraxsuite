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
    /// DetectProjectFieldValuesRequest
    /// </summary>
    [DataContract]
    public partial class DetectProjectFieldValuesRequest :  IEquatable<DetectProjectFieldValuesRequest>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="DetectProjectFieldValuesRequest" /> class.
        /// </summary>
        /// <param name="doNotUpdateModified">doNotUpdateModified.</param>
        /// <param name="doNotWrite">doNotWrite.</param>
        /// <param name="documentIds">documentIds.</param>
        public DetectProjectFieldValuesRequest(bool doNotUpdateModified = default(bool), bool doNotWrite = default(bool), List<int> documentIds = default(List<int>))
        {
            this.DoNotUpdateModified = doNotUpdateModified;
            this.DoNotWrite = doNotWrite;
            this.DocumentIds = documentIds;
        }

        /// <summary>
        /// Gets or Sets DoNotUpdateModified
        /// </summary>
        [DataMember(Name="do_not_update_modified", EmitDefaultValue=false)]
        public bool DoNotUpdateModified { get; set; }

        /// <summary>
        /// Gets or Sets DoNotWrite
        /// </summary>
        [DataMember(Name="do_not_write", EmitDefaultValue=false)]
        public bool DoNotWrite { get; set; }

        /// <summary>
        /// Gets or Sets DocumentIds
        /// </summary>
        [DataMember(Name="document_ids", EmitDefaultValue=false)]
        public List<int> DocumentIds { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class DetectProjectFieldValuesRequest {\n");
            sb.Append("  DoNotUpdateModified: ").Append(DoNotUpdateModified).Append("\n");
            sb.Append("  DoNotWrite: ").Append(DoNotWrite).Append("\n");
            sb.Append("  DocumentIds: ").Append(DocumentIds).Append("\n");
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
            return this.Equals(input as DetectProjectFieldValuesRequest);
        }

        /// <summary>
        /// Returns true if DetectProjectFieldValuesRequest instances are equal
        /// </summary>
        /// <param name="input">Instance of DetectProjectFieldValuesRequest to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(DetectProjectFieldValuesRequest input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.DoNotUpdateModified == input.DoNotUpdateModified ||
                    (this.DoNotUpdateModified != null &&
                    this.DoNotUpdateModified.Equals(input.DoNotUpdateModified))
                ) && 
                (
                    this.DoNotWrite == input.DoNotWrite ||
                    (this.DoNotWrite != null &&
                    this.DoNotWrite.Equals(input.DoNotWrite))
                ) && 
                (
                    this.DocumentIds == input.DocumentIds ||
                    this.DocumentIds != null &&
                    input.DocumentIds != null &&
                    this.DocumentIds.SequenceEqual(input.DocumentIds)
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
                if (this.DoNotUpdateModified != null)
                    hashCode = hashCode * 59 + this.DoNotUpdateModified.GetHashCode();
                if (this.DoNotWrite != null)
                    hashCode = hashCode * 59 + this.DoNotWrite.GetHashCode();
                if (this.DocumentIds != null)
                    hashCode = hashCode * 59 + this.DocumentIds.GetHashCode();
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
