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
    /// MarkForSeenWebNotificationRequest
    /// </summary>
    [DataContract]
    public partial class MarkForSeenWebNotificationRequest :  IEquatable<MarkForSeenWebNotificationRequest>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="MarkForSeenWebNotificationRequest" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected MarkForSeenWebNotificationRequest() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="MarkForSeenWebNotificationRequest" /> class.
        /// </summary>
        /// <param name="notificationIds">notificationIds (required).</param>
        /// <param name="isSeen">isSeen (required).</param>
        public MarkForSeenWebNotificationRequest(List<int> notificationIds = default(List<int>), bool isSeen = default(bool))
        {
            // to ensure "notificationIds" is required (not null)
            if (notificationIds == null)
            {
                throw new InvalidDataException("notificationIds is a required property for MarkForSeenWebNotificationRequest and cannot be null");
            }
            else
            {
                this.NotificationIds = notificationIds;
            }

            // to ensure "isSeen" is required (not null)
            if (isSeen == null)
            {
                throw new InvalidDataException("isSeen is a required property for MarkForSeenWebNotificationRequest and cannot be null");
            }
            else
            {
                this.IsSeen = isSeen;
            }

        }

        /// <summary>
        /// Gets or Sets NotificationIds
        /// </summary>
        [DataMember(Name="notification_ids", EmitDefaultValue=true)]
        public List<int> NotificationIds { get; set; }

        /// <summary>
        /// Gets or Sets IsSeen
        /// </summary>
        [DataMember(Name="is_seen", EmitDefaultValue=true)]
        public bool IsSeen { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class MarkForSeenWebNotificationRequest {\n");
            sb.Append("  NotificationIds: ").Append(NotificationIds).Append("\n");
            sb.Append("  IsSeen: ").Append(IsSeen).Append("\n");
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
            return this.Equals(input as MarkForSeenWebNotificationRequest);
        }

        /// <summary>
        /// Returns true if MarkForSeenWebNotificationRequest instances are equal
        /// </summary>
        /// <param name="input">Instance of MarkForSeenWebNotificationRequest to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(MarkForSeenWebNotificationRequest input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.NotificationIds == input.NotificationIds ||
                    this.NotificationIds != null &&
                    input.NotificationIds != null &&
                    this.NotificationIds.SequenceEqual(input.NotificationIds)
                ) && 
                (
                    this.IsSeen == input.IsSeen ||
                    (this.IsSeen != null &&
                    this.IsSeen.Equals(input.IsSeen))
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
                if (this.NotificationIds != null)
                    hashCode = hashCode * 59 + this.NotificationIds.GetHashCode();
                if (this.IsSeen != null)
                    hashCode = hashCode * 59 + this.IsSeen.GetHashCode();
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
