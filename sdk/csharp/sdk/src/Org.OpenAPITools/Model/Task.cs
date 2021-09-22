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
    /// Task
    /// </summary>
    [DataContract]
    public partial class Task :  IEquatable<Task>, IValidatableObject
    {
        /// <summary>
        /// Defines Status
        /// </summary>
        [JsonConverter(typeof(StringEnumConverter))]
        public enum StatusEnum
        {
            /// <summary>
            /// Enum FAILURE for value: FAILURE
            /// </summary>
            [EnumMember(Value = "FAILURE")]
            FAILURE = 1,

            /// <summary>
            /// Enum PENDING for value: PENDING
            /// </summary>
            [EnumMember(Value = "PENDING")]
            PENDING = 2,

            /// <summary>
            /// Enum RECEIVED for value: RECEIVED
            /// </summary>
            [EnumMember(Value = "RECEIVED")]
            RECEIVED = 3,

            /// <summary>
            /// Enum RETRY for value: RETRY
            /// </summary>
            [EnumMember(Value = "RETRY")]
            RETRY = 4,

            /// <summary>
            /// Enum REVOKED for value: REVOKED
            /// </summary>
            [EnumMember(Value = "REVOKED")]
            REVOKED = 5,

            /// <summary>
            /// Enum STARTED for value: STARTED
            /// </summary>
            [EnumMember(Value = "STARTED")]
            STARTED = 6,

            /// <summary>
            /// Enum SUCCESS for value: SUCCESS
            /// </summary>
            [EnumMember(Value = "SUCCESS")]
            SUCCESS = 7

        }

        /// <summary>
        /// Gets or Sets Status
        /// </summary>
        [DataMember(Name="status", EmitDefaultValue=true)]
        public StatusEnum? Status { get; set; }
        /// <summary>
        /// Initializes a new instance of the <see cref="Task" /> class.
        /// </summary>
        /// <param name="pk">pk.</param>
        /// <param name="name">name.</param>
        /// <param name="dateStart">dateStart.</param>
        /// <param name="dateWorkStart">dateWorkStart.</param>
        /// <param name="dateDone">dateDone.</param>
        /// <param name="progress">progress.</param>
        /// <param name="status">status.</param>
        public Task(string pk = default(string), string name = default(string), DateTime dateStart = default(DateTime), DateTime? dateWorkStart = default(DateTime?), DateTime? dateDone = default(DateTime?), int? progress = default(int?), StatusEnum? status = default(StatusEnum?))
        {
            this.Name = name;
            this.DateWorkStart = dateWorkStart;
            this.DateDone = dateDone;
            this.Progress = progress;
            this.Status = status;
            this.Pk = pk;
            this.Name = name;
            this.DateStart = dateStart;
            this.DateWorkStart = dateWorkStart;
            this.DateDone = dateDone;
            this.Progress = progress;
            this.Status = status;
        }

        /// <summary>
        /// Gets or Sets Pk
        /// </summary>
        [DataMember(Name="pk", EmitDefaultValue=false)]
        public string Pk { get; set; }

        /// <summary>
        /// Gets or Sets Name
        /// </summary>
        [DataMember(Name="name", EmitDefaultValue=true)]
        public string Name { get; set; }

        /// <summary>
        /// Gets or Sets DateStart
        /// </summary>
        [DataMember(Name="date_start", EmitDefaultValue=false)]
        public DateTime DateStart { get; set; }

        /// <summary>
        /// Gets or Sets DateWorkStart
        /// </summary>
        [DataMember(Name="date_work_start", EmitDefaultValue=true)]
        public DateTime? DateWorkStart { get; set; }

        /// <summary>
        /// Gets or Sets UserUsername
        /// </summary>
        [DataMember(Name="user__username", EmitDefaultValue=false)]
        public string UserUsername { get; private set; }

        /// <summary>
        /// Gets or Sets DateDone
        /// </summary>
        [DataMember(Name="date_done", EmitDefaultValue=true)]
        public DateTime? DateDone { get; set; }

        /// <summary>
        /// Gets or Sets Duration
        /// </summary>
        [DataMember(Name="duration", EmitDefaultValue=false)]
        public string Duration { get; private set; }

        /// <summary>
        /// Gets or Sets Progress
        /// </summary>
        [DataMember(Name="progress", EmitDefaultValue=true)]
        public int? Progress { get; set; }


        /// <summary>
        /// Gets or Sets HasError
        /// </summary>
        [DataMember(Name="has_error", EmitDefaultValue=false)]
        public string HasError { get; private set; }

        /// <summary>
        /// Gets or Sets Description
        /// </summary>
        [DataMember(Name="description", EmitDefaultValue=false)]
        public string Description { get; private set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class Task {\n");
            sb.Append("  Pk: ").Append(Pk).Append("\n");
            sb.Append("  Name: ").Append(Name).Append("\n");
            sb.Append("  DateStart: ").Append(DateStart).Append("\n");
            sb.Append("  DateWorkStart: ").Append(DateWorkStart).Append("\n");
            sb.Append("  UserUsername: ").Append(UserUsername).Append("\n");
            sb.Append("  DateDone: ").Append(DateDone).Append("\n");
            sb.Append("  Duration: ").Append(Duration).Append("\n");
            sb.Append("  Progress: ").Append(Progress).Append("\n");
            sb.Append("  Status: ").Append(Status).Append("\n");
            sb.Append("  HasError: ").Append(HasError).Append("\n");
            sb.Append("  Description: ").Append(Description).Append("\n");
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
            return this.Equals(input as Task);
        }

        /// <summary>
        /// Returns true if Task instances are equal
        /// </summary>
        /// <param name="input">Instance of Task to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(Task input)
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
                    this.DateStart == input.DateStart ||
                    (this.DateStart != null &&
                    this.DateStart.Equals(input.DateStart))
                ) && 
                (
                    this.DateWorkStart == input.DateWorkStart ||
                    (this.DateWorkStart != null &&
                    this.DateWorkStart.Equals(input.DateWorkStart))
                ) && 
                (
                    this.UserUsername == input.UserUsername ||
                    (this.UserUsername != null &&
                    this.UserUsername.Equals(input.UserUsername))
                ) && 
                (
                    this.DateDone == input.DateDone ||
                    (this.DateDone != null &&
                    this.DateDone.Equals(input.DateDone))
                ) && 
                (
                    this.Duration == input.Duration ||
                    (this.Duration != null &&
                    this.Duration.Equals(input.Duration))
                ) && 
                (
                    this.Progress == input.Progress ||
                    (this.Progress != null &&
                    this.Progress.Equals(input.Progress))
                ) && 
                (
                    this.Status == input.Status ||
                    (this.Status != null &&
                    this.Status.Equals(input.Status))
                ) && 
                (
                    this.HasError == input.HasError ||
                    (this.HasError != null &&
                    this.HasError.Equals(input.HasError))
                ) && 
                (
                    this.Description == input.Description ||
                    (this.Description != null &&
                    this.Description.Equals(input.Description))
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
                if (this.DateStart != null)
                    hashCode = hashCode * 59 + this.DateStart.GetHashCode();
                if (this.DateWorkStart != null)
                    hashCode = hashCode * 59 + this.DateWorkStart.GetHashCode();
                if (this.UserUsername != null)
                    hashCode = hashCode * 59 + this.UserUsername.GetHashCode();
                if (this.DateDone != null)
                    hashCode = hashCode * 59 + this.DateDone.GetHashCode();
                if (this.Duration != null)
                    hashCode = hashCode * 59 + this.Duration.GetHashCode();
                if (this.Progress != null)
                    hashCode = hashCode * 59 + this.Progress.GetHashCode();
                if (this.Status != null)
                    hashCode = hashCode * 59 + this.Status.GetHashCode();
                if (this.HasError != null)
                    hashCode = hashCode * 59 + this.HasError.GetHashCode();
                if (this.Description != null)
                    hashCode = hashCode * 59 + this.Description.GetHashCode();
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
            // Pk (string) maxLength
            if(this.Pk != null && this.Pk.Length > 255)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for Pk, length must be less than 255.", new [] { "Pk" });
            }

 
            // Name (string) maxLength
            if(this.Name != null && this.Name.Length > 100)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for Name, length must be less than 100.", new [] { "Name" });
            }

 

 
            // Progress (int?) maximum
            if(this.Progress > (int?)2147483647)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for Progress, must be a value less than or equal to 2147483647.", new [] { "Progress" });
            }

            // Progress (int?) minimum
            if(this.Progress < (int?)0)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for Progress, must be a value greater than or equal to 0.", new [] { "Progress" });
            }

            yield break;
        }
    }

}
