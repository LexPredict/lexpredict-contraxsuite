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
    /// WebNotificationDetailNotification
    /// </summary>
    [DataContract]
    public partial class WebNotificationDetailNotification :  IEquatable<WebNotificationDetailNotification>, IValidatableObject
    {
        /// <summary>
        /// Notification type
        /// </summary>
        /// <value>Notification type</value>
        [JsonConverter(typeof(StringEnumConverter))]
        public enum NotificationTypeEnum
        {
            /// <summary>
            /// Enum DOCUMENTASSIGNED for value: DOCUMENT_ASSIGNED
            /// </summary>
            [EnumMember(Value = "DOCUMENT_ASSIGNED")]
            DOCUMENTASSIGNED = 1,

            /// <summary>
            /// Enum DOCUMENTUNASSIGNED for value: DOCUMENT_UNASSIGNED
            /// </summary>
            [EnumMember(Value = "DOCUMENT_UNASSIGNED")]
            DOCUMENTUNASSIGNED = 2,

            /// <summary>
            /// Enum CLAUSESASSIGNED for value: CLAUSES_ASSIGNED
            /// </summary>
            [EnumMember(Value = "CLAUSES_ASSIGNED")]
            CLAUSESASSIGNED = 3,

            /// <summary>
            /// Enum CLAUSESUNASSIGNED for value: CLAUSES_UNASSIGNED
            /// </summary>
            [EnumMember(Value = "CLAUSES_UNASSIGNED")]
            CLAUSESUNASSIGNED = 4,

            /// <summary>
            /// Enum DOCUMENTSUPLOADED for value: DOCUMENTS_UPLOADED
            /// </summary>
            [EnumMember(Value = "DOCUMENTS_UPLOADED")]
            DOCUMENTSUPLOADED = 5,

            /// <summary>
            /// Enum DOCUMENTDELETED for value: DOCUMENT_DELETED
            /// </summary>
            [EnumMember(Value = "DOCUMENT_DELETED")]
            DOCUMENTDELETED = 6,

            /// <summary>
            /// Enum DOCUMENTADDED for value: DOCUMENT_ADDED
            /// </summary>
            [EnumMember(Value = "DOCUMENT_ADDED")]
            DOCUMENTADDED = 7,

            /// <summary>
            /// Enum DOCUMENTSTATUSCHANGED for value: DOCUMENT_STATUS_CHANGED
            /// </summary>
            [EnumMember(Value = "DOCUMENT_STATUS_CHANGED")]
            DOCUMENTSTATUSCHANGED = 8,

            /// <summary>
            /// Enum CLUSTERIMPORTED for value: CLUSTER_IMPORTED
            /// </summary>
            [EnumMember(Value = "CLUSTER_IMPORTED")]
            CLUSTERIMPORTED = 9,

            /// <summary>
            /// Enum FIELDVALUEDETECTIONCOMPLETED for value: FIELD_VALUE_DETECTION_COMPLETED
            /// </summary>
            [EnumMember(Value = "FIELD_VALUE_DETECTION_COMPLETED")]
            FIELDVALUEDETECTIONCOMPLETED = 10,

            /// <summary>
            /// Enum CUSTOMTERMSETSEARCHFINISHED for value: CUSTOM_TERM_SET_SEARCH_FINISHED
            /// </summary>
            [EnumMember(Value = "CUSTOM_TERM_SET_SEARCH_FINISHED")]
            CUSTOMTERMSETSEARCHFINISHED = 11,

            /// <summary>
            /// Enum CUSTOMCOMPANYTYPESEARCHFINISHED for value: CUSTOM_COMPANY_TYPE_SEARCH_FINISHED
            /// </summary>
            [EnumMember(Value = "CUSTOM_COMPANY_TYPE_SEARCH_FINISHED")]
            CUSTOMCOMPANYTYPESEARCHFINISHED = 12,

            /// <summary>
            /// Enum DOCUMENTSIMILARITYSEARCHFINISHED for value: DOCUMENT_SIMILARITY_SEARCH_FINISHED
            /// </summary>
            [EnumMember(Value = "DOCUMENT_SIMILARITY_SEARCH_FINISHED")]
            DOCUMENTSIMILARITYSEARCHFINISHED = 13,

            /// <summary>
            /// Enum TEXTUNITSIMILARITYSEARCHFINISHED for value: TEXT_UNIT_SIMILARITY_SEARCH_FINISHED
            /// </summary>
            [EnumMember(Value = "TEXT_UNIT_SIMILARITY_SEARCH_FINISHED")]
            TEXTUNITSIMILARITYSEARCHFINISHED = 14

        }

        /// <summary>
        /// Notification type
        /// </summary>
        /// <value>Notification type</value>
        [DataMember(Name="notification_type", EmitDefaultValue=true)]
        public NotificationTypeEnum? NotificationType { get; set; }
        /// <summary>
        /// Initializes a new instance of the <see cref="WebNotificationDetailNotification" /> class.
        /// </summary>
        /// <param name="messageData">messageData.</param>
        /// <param name="notificationType">Notification type.</param>
        /// <param name="redirectLink">redirectLink.</param>
        public WebNotificationDetailNotification(Object messageData = default(Object), NotificationTypeEnum? notificationType = default(NotificationTypeEnum?), Object redirectLink = default(Object))
        {
            this.MessageData = messageData;
            this.NotificationType = notificationType;
            this.RedirectLink = redirectLink;
            this.MessageData = messageData;
            this.NotificationType = notificationType;
            this.RedirectLink = redirectLink;
        }

        /// <summary>
        /// Gets or Sets Id
        /// </summary>
        [DataMember(Name="id", EmitDefaultValue=false)]
        public int Id { get; private set; }

        /// <summary>
        /// Gets or Sets MessageData
        /// </summary>
        [DataMember(Name="message_data", EmitDefaultValue=true)]
        public Object MessageData { get; set; }

        /// <summary>
        /// Gets or Sets MessageTemplate
        /// </summary>
        [DataMember(Name="message_template", EmitDefaultValue=false)]
        public string MessageTemplate { get; private set; }

        /// <summary>
        /// Gets or Sets CreatedDate
        /// </summary>
        [DataMember(Name="created_date", EmitDefaultValue=false)]
        public DateTime CreatedDate { get; private set; }


        /// <summary>
        /// Gets or Sets RedirectLink
        /// </summary>
        [DataMember(Name="redirect_link", EmitDefaultValue=true)]
        public Object RedirectLink { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class WebNotificationDetailNotification {\n");
            sb.Append("  Id: ").Append(Id).Append("\n");
            sb.Append("  MessageData: ").Append(MessageData).Append("\n");
            sb.Append("  MessageTemplate: ").Append(MessageTemplate).Append("\n");
            sb.Append("  CreatedDate: ").Append(CreatedDate).Append("\n");
            sb.Append("  NotificationType: ").Append(NotificationType).Append("\n");
            sb.Append("  RedirectLink: ").Append(RedirectLink).Append("\n");
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
            return this.Equals(input as WebNotificationDetailNotification);
        }

        /// <summary>
        /// Returns true if WebNotificationDetailNotification instances are equal
        /// </summary>
        /// <param name="input">Instance of WebNotificationDetailNotification to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(WebNotificationDetailNotification input)
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
                    this.MessageData == input.MessageData ||
                    (this.MessageData != null &&
                    this.MessageData.Equals(input.MessageData))
                ) && 
                (
                    this.MessageTemplate == input.MessageTemplate ||
                    (this.MessageTemplate != null &&
                    this.MessageTemplate.Equals(input.MessageTemplate))
                ) && 
                (
                    this.CreatedDate == input.CreatedDate ||
                    (this.CreatedDate != null &&
                    this.CreatedDate.Equals(input.CreatedDate))
                ) && 
                (
                    this.NotificationType == input.NotificationType ||
                    (this.NotificationType != null &&
                    this.NotificationType.Equals(input.NotificationType))
                ) && 
                (
                    this.RedirectLink == input.RedirectLink ||
                    (this.RedirectLink != null &&
                    this.RedirectLink.Equals(input.RedirectLink))
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
                if (this.MessageData != null)
                    hashCode = hashCode * 59 + this.MessageData.GetHashCode();
                if (this.MessageTemplate != null)
                    hashCode = hashCode * 59 + this.MessageTemplate.GetHashCode();
                if (this.CreatedDate != null)
                    hashCode = hashCode * 59 + this.CreatedDate.GetHashCode();
                if (this.NotificationType != null)
                    hashCode = hashCode * 59 + this.NotificationType.GetHashCode();
                if (this.RedirectLink != null)
                    hashCode = hashCode * 59 + this.RedirectLink.GetHashCode();
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
