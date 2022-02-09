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
    /// MarkUnmarkForDeleteDocumentsResponse
    /// </summary>
    [DataContract]
    public partial class MarkUnmarkForDeleteDocumentsResponse :  IEquatable<MarkUnmarkForDeleteDocumentsResponse>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="MarkUnmarkForDeleteDocumentsResponse" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected MarkUnmarkForDeleteDocumentsResponse() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="MarkUnmarkForDeleteDocumentsResponse" /> class.
        /// </summary>
        /// <param name="countDeleted">countDeleted (required).</param>
        public MarkUnmarkForDeleteDocumentsResponse(int countDeleted = default(int))
        {
            // to ensure "countDeleted" is required (not null)
            if (countDeleted == null)
            {
                throw new InvalidDataException("countDeleted is a required property for MarkUnmarkForDeleteDocumentsResponse and cannot be null");
            }
            else
            {
                this.CountDeleted = countDeleted;
            }

        }

        /// <summary>
        /// Gets or Sets CountDeleted
        /// </summary>
        [DataMember(Name="count_deleted", EmitDefaultValue=true)]
        public int CountDeleted { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class MarkUnmarkForDeleteDocumentsResponse {\n");
            sb.Append("  CountDeleted: ").Append(CountDeleted).Append("\n");
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
            return this.Equals(input as MarkUnmarkForDeleteDocumentsResponse);
        }

        /// <summary>
        /// Returns true if MarkUnmarkForDeleteDocumentsResponse instances are equal
        /// </summary>
        /// <param name="input">Instance of MarkUnmarkForDeleteDocumentsResponse to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(MarkUnmarkForDeleteDocumentsResponse input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.CountDeleted == input.CountDeleted ||
                    (this.CountDeleted != null &&
                    this.CountDeleted.Equals(input.CountDeleted))
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
                if (this.CountDeleted != null)
                    hashCode = hashCode * 59 + this.CountDeleted.GetHashCode();
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
