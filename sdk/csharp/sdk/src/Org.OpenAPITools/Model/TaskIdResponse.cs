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
    /// TaskIdResponse
    /// </summary>
    [DataContract]
    public partial class TaskIdResponse :  IEquatable<TaskIdResponse>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="TaskIdResponse" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected TaskIdResponse() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="TaskIdResponse" /> class.
        /// </summary>
        /// <param name="taskId">taskId (required).</param>
        public TaskIdResponse(Guid taskId = default(Guid))
        {
            // to ensure "taskId" is required (not null)
            if (taskId == null)
            {
                throw new InvalidDataException("taskId is a required property for TaskIdResponse and cannot be null");
            }
            else
            {
                this.TaskId = taskId;
            }

        }

        /// <summary>
        /// Gets or Sets TaskId
        /// </summary>
        [DataMember(Name="task_id", EmitDefaultValue=true)]
        public Guid TaskId { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class TaskIdResponse {\n");
            sb.Append("  TaskId: ").Append(TaskId).Append("\n");
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
            return this.Equals(input as TaskIdResponse);
        }

        /// <summary>
        /// Returns true if TaskIdResponse instances are equal
        /// </summary>
        /// <param name="input">Instance of TaskIdResponse to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(TaskIdResponse input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.TaskId == input.TaskId ||
                    (this.TaskId != null &&
                    this.TaskId.Equals(input.TaskId))
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
                if (this.TaskId != null)
                    hashCode = hashCode * 59 + this.TaskId.GetHashCode();
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