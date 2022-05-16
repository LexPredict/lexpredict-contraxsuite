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
    /// MarkForSeenWebNotificationResponse
    /// </summary>
    [DataContract]
    public partial class MarkForSeenWebNotificationResponse :  IEquatable<MarkForSeenWebNotificationResponse>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="MarkForSeenWebNotificationResponse" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected MarkForSeenWebNotificationResponse() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="MarkForSeenWebNotificationResponse" /> class.
        /// </summary>
        /// <param name="countProcessed">countProcessed (required).</param>
        public MarkForSeenWebNotificationResponse(int countProcessed = default(int))
        {
            // to ensure "countProcessed" is required (not null)
            if (countProcessed == null)
            {
                throw new InvalidDataException("countProcessed is a required property for MarkForSeenWebNotificationResponse and cannot be null");
            }
            else
            {
                this.CountProcessed = countProcessed;
            }

        }

        /// <summary>
        /// Gets or Sets CountProcessed
        /// </summary>
        [DataMember(Name="count_processed", EmitDefaultValue=true)]
        public int CountProcessed { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class MarkForSeenWebNotificationResponse {\n");
            sb.Append("  CountProcessed: ").Append(CountProcessed).Append("\n");
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
            return this.Equals(input as MarkForSeenWebNotificationResponse);
        }

        /// <summary>
        /// Returns true if MarkForSeenWebNotificationResponse instances are equal
        /// </summary>
        /// <param name="input">Instance of MarkForSeenWebNotificationResponse to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(MarkForSeenWebNotificationResponse input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.CountProcessed == input.CountProcessed ||
                    (this.CountProcessed != null &&
                    this.CountProcessed.Equals(input.CountProcessed))
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
                if (this.CountProcessed != null)
                    hashCode = hashCode * 59 + this.CountProcessed.GetHashCode();
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