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
    /// DumpPUTErrorResponse
    /// </summary>
    [DataContract]
    public partial class DumpPUTErrorResponse :  IEquatable<DumpPUTErrorResponse>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="DumpPUTErrorResponse" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected DumpPUTErrorResponse() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="DumpPUTErrorResponse" /> class.
        /// </summary>
        /// <param name="log">log (required).</param>
        /// <param name="exception">exception (required).</param>
        public DumpPUTErrorResponse(string log = default(string), string exception = default(string))
        {
            // to ensure "log" is required (not null)
            if (log == null)
            {
                throw new InvalidDataException("log is a required property for DumpPUTErrorResponse and cannot be null");
            }
            else
            {
                this.Log = log;
            }

            // to ensure "exception" is required (not null)
            if (exception == null)
            {
                throw new InvalidDataException("exception is a required property for DumpPUTErrorResponse and cannot be null");
            }
            else
            {
                this.Exception = exception;
            }

        }

        /// <summary>
        /// Gets or Sets Log
        /// </summary>
        [DataMember(Name="log", EmitDefaultValue=true)]
        public string Log { get; set; }

        /// <summary>
        /// Gets or Sets Exception
        /// </summary>
        [DataMember(Name="exception", EmitDefaultValue=true)]
        public string Exception { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class DumpPUTErrorResponse {\n");
            sb.Append("  Log: ").Append(Log).Append("\n");
            sb.Append("  Exception: ").Append(Exception).Append("\n");
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
            return this.Equals(input as DumpPUTErrorResponse);
        }

        /// <summary>
        /// Returns true if DumpPUTErrorResponse instances are equal
        /// </summary>
        /// <param name="input">Instance of DumpPUTErrorResponse to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(DumpPUTErrorResponse input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.Log == input.Log ||
                    (this.Log != null &&
                    this.Log.Equals(input.Log))
                ) && 
                (
                    this.Exception == input.Exception ||
                    (this.Exception != null &&
                    this.Exception.Equals(input.Exception))
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
                if (this.Log != null)
                    hashCode = hashCode * 59 + this.Log.GetHashCode();
                if (this.Exception != null)
                    hashCode = hashCode * 59 + this.Exception.GetHashCode();
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
