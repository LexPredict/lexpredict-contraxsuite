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
    /// Upload
    /// </summary>
    [DataContract]
    public partial class Upload :  IEquatable<Upload>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="Upload" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected Upload() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="Upload" /> class.
        /// </summary>
        /// <param name="guid">guid.</param>
        /// <param name="state">state.</param>
        /// <param name="uploadOffset">uploadOffset.</param>
        /// <param name="uploadLength">uploadLength.</param>
        /// <param name="uploadMetadata">uploadMetadata (required).</param>
        /// <param name="filename">filename.</param>
        /// <param name="temporaryFilePath">temporaryFilePath.</param>
        /// <param name="expires">expires.</param>
        /// <param name="uploadedFile">uploadedFile.</param>
        public Upload(Guid guid = default(Guid), string state = default(string), long uploadOffset = default(long), long uploadLength = default(long), string uploadMetadata = default(string), string filename = default(string), string temporaryFilePath = default(string), DateTime? expires = default(DateTime?), System.IO.Stream uploadedFile = default(System.IO.Stream))
        {
            // to ensure "uploadMetadata" is required (not null)
            if (uploadMetadata == null)
            {
                throw new InvalidDataException("uploadMetadata is a required property for Upload and cannot be null");
            }
            else
            {
                this.UploadMetadata = uploadMetadata;
            }

            this.TemporaryFilePath = temporaryFilePath;
            this.Expires = expires;
            this.UploadedFile = uploadedFile;
            this.Guid = guid;
            this.State = state;
            this.UploadOffset = uploadOffset;
            this.UploadLength = uploadLength;
            this.Filename = filename;
            this.TemporaryFilePath = temporaryFilePath;
            this.Expires = expires;
            this.UploadedFile = uploadedFile;
        }

        /// <summary>
        /// Gets or Sets Id
        /// </summary>
        [DataMember(Name="id", EmitDefaultValue=false)]
        public int Id { get; private set; }

        /// <summary>
        /// Gets or Sets Guid
        /// </summary>
        [DataMember(Name="guid", EmitDefaultValue=false)]
        public Guid Guid { get; set; }

        /// <summary>
        /// Gets or Sets State
        /// </summary>
        [DataMember(Name="state", EmitDefaultValue=false)]
        public string State { get; set; }

        /// <summary>
        /// Gets or Sets UploadOffset
        /// </summary>
        [DataMember(Name="upload_offset", EmitDefaultValue=false)]
        public long UploadOffset { get; set; }

        /// <summary>
        /// Gets or Sets UploadLength
        /// </summary>
        [DataMember(Name="upload_length", EmitDefaultValue=false)]
        public long UploadLength { get; set; }

        /// <summary>
        /// Gets or Sets UploadMetadata
        /// </summary>
        [DataMember(Name="upload_metadata", EmitDefaultValue=true)]
        public string UploadMetadata { get; set; }

        /// <summary>
        /// Gets or Sets Filename
        /// </summary>
        [DataMember(Name="filename", EmitDefaultValue=false)]
        public string Filename { get; set; }

        /// <summary>
        /// Gets or Sets TemporaryFilePath
        /// </summary>
        [DataMember(Name="temporary_file_path", EmitDefaultValue=true)]
        public string TemporaryFilePath { get; set; }

        /// <summary>
        /// Gets or Sets Expires
        /// </summary>
        [DataMember(Name="expires", EmitDefaultValue=true)]
        public DateTime? Expires { get; set; }

        /// <summary>
        /// Gets or Sets UploadedFile
        /// </summary>
        [DataMember(Name="uploaded_file", EmitDefaultValue=true)]
        public System.IO.Stream UploadedFile { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class Upload {\n");
            sb.Append("  Id: ").Append(Id).Append("\n");
            sb.Append("  Guid: ").Append(Guid).Append("\n");
            sb.Append("  State: ").Append(State).Append("\n");
            sb.Append("  UploadOffset: ").Append(UploadOffset).Append("\n");
            sb.Append("  UploadLength: ").Append(UploadLength).Append("\n");
            sb.Append("  UploadMetadata: ").Append(UploadMetadata).Append("\n");
            sb.Append("  Filename: ").Append(Filename).Append("\n");
            sb.Append("  TemporaryFilePath: ").Append(TemporaryFilePath).Append("\n");
            sb.Append("  Expires: ").Append(Expires).Append("\n");
            sb.Append("  UploadedFile: ").Append(UploadedFile).Append("\n");
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
            return this.Equals(input as Upload);
        }

        /// <summary>
        /// Returns true if Upload instances are equal
        /// </summary>
        /// <param name="input">Instance of Upload to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(Upload input)
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
                    this.Guid == input.Guid ||
                    (this.Guid != null &&
                    this.Guid.Equals(input.Guid))
                ) && 
                (
                    this.State == input.State ||
                    (this.State != null &&
                    this.State.Equals(input.State))
                ) && 
                (
                    this.UploadOffset == input.UploadOffset ||
                    (this.UploadOffset != null &&
                    this.UploadOffset.Equals(input.UploadOffset))
                ) && 
                (
                    this.UploadLength == input.UploadLength ||
                    (this.UploadLength != null &&
                    this.UploadLength.Equals(input.UploadLength))
                ) && 
                (
                    this.UploadMetadata == input.UploadMetadata ||
                    (this.UploadMetadata != null &&
                    this.UploadMetadata.Equals(input.UploadMetadata))
                ) && 
                (
                    this.Filename == input.Filename ||
                    (this.Filename != null &&
                    this.Filename.Equals(input.Filename))
                ) && 
                (
                    this.TemporaryFilePath == input.TemporaryFilePath ||
                    (this.TemporaryFilePath != null &&
                    this.TemporaryFilePath.Equals(input.TemporaryFilePath))
                ) && 
                (
                    this.Expires == input.Expires ||
                    (this.Expires != null &&
                    this.Expires.Equals(input.Expires))
                ) && 
                (
                    this.UploadedFile == input.UploadedFile ||
                    (this.UploadedFile != null &&
                    this.UploadedFile.Equals(input.UploadedFile))
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
                if (this.Guid != null)
                    hashCode = hashCode * 59 + this.Guid.GetHashCode();
                if (this.State != null)
                    hashCode = hashCode * 59 + this.State.GetHashCode();
                if (this.UploadOffset != null)
                    hashCode = hashCode * 59 + this.UploadOffset.GetHashCode();
                if (this.UploadLength != null)
                    hashCode = hashCode * 59 + this.UploadLength.GetHashCode();
                if (this.UploadMetadata != null)
                    hashCode = hashCode * 59 + this.UploadMetadata.GetHashCode();
                if (this.Filename != null)
                    hashCode = hashCode * 59 + this.Filename.GetHashCode();
                if (this.TemporaryFilePath != null)
                    hashCode = hashCode * 59 + this.TemporaryFilePath.GetHashCode();
                if (this.Expires != null)
                    hashCode = hashCode * 59 + this.Expires.GetHashCode();
                if (this.UploadedFile != null)
                    hashCode = hashCode * 59 + this.UploadedFile.GetHashCode();
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
            // State (string) maxLength
            if(this.State != null && this.State.Length > 50)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for State, length must be less than 50.", new [] { "State" });
            }

 

 
            // UploadOffset (long) maximum
            if(this.UploadOffset > (long)9223372036854775807)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for UploadOffset, must be a value less than or equal to 9223372036854775807.", new [] { "UploadOffset" });
            }

            // UploadOffset (long) minimum
            if(this.UploadOffset < (long)-9223372036854775808)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for UploadOffset, must be a value greater than or equal to -9223372036854775808.", new [] { "UploadOffset" });
            }


 
            // UploadLength (long) maximum
            if(this.UploadLength > (long)9223372036854775807)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for UploadLength, must be a value less than or equal to 9223372036854775807.", new [] { "UploadLength" });
            }

            // UploadLength (long) minimum
            if(this.UploadLength < (long)-9223372036854775808)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for UploadLength, must be a value greater than or equal to -9223372036854775808.", new [] { "UploadLength" });
            }

            // Filename (string) maxLength
            if(this.Filename != null && this.Filename.Length > 255)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for Filename, length must be less than 255.", new [] { "Filename" });
            }

 
            // TemporaryFilePath (string) maxLength
            if(this.TemporaryFilePath != null && this.TemporaryFilePath.Length > 4096)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for TemporaryFilePath, length must be less than 4096.", new [] { "TemporaryFilePath" });
            }

 
            yield break;
        }
    }

}
