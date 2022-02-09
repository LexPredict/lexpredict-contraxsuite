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
    /// DocumentTypeImportRequest
    /// </summary>
    [DataContract]
    public partial class DocumentTypeImportRequest :  IEquatable<DocumentTypeImportRequest>, IValidatableObject
    {
        /// <summary>
        /// Defines Action
        /// </summary>
        [JsonConverter(typeof(StringEnumConverter))]
        public enum ActionEnum
        {
            /// <summary>
            /// Enum Validate for value: validate
            /// </summary>
            [EnumMember(Value = "validate")]
            Validate = 1,

            /// <summary>
            /// Enum Validateimport for value: validate|import
            /// </summary>
            [EnumMember(Value = "validate|import")]
            Validateimport = 2,

            /// <summary>
            /// Enum Importautofixretainmissingobjects for value: import|auto_fix|retain_missing_objects
            /// </summary>
            [EnumMember(Value = "import|auto_fix|retain_missing_objects")]
            Importautofixretainmissingobjects = 3,

            /// <summary>
            /// Enum Importautofixremovemissingobjects for value: import|auto_fix|remove_missing_objects
            /// </summary>
            [EnumMember(Value = "import|auto_fix|remove_missing_objects")]
            Importautofixremovemissingobjects = 4

        }

        /// <summary>
        /// Gets or Sets Action
        /// </summary>
        [DataMember(Name="action", EmitDefaultValue=false)]
        public ActionEnum? Action { get; set; }
        /// <summary>
        /// Initializes a new instance of the <see cref="DocumentTypeImportRequest" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected DocumentTypeImportRequest() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="DocumentTypeImportRequest" /> class.
        /// </summary>
        /// <param name="file">file (required).</param>
        /// <param name="updateCache">updateCache.</param>
        /// <param name="action">action.</param>
        /// <param name="sourceVersion">sourceVersion.</param>
        public DocumentTypeImportRequest(System.IO.Stream file = default(System.IO.Stream), bool updateCache = default(bool), ActionEnum? action = default(ActionEnum?), string sourceVersion = default(string))
        {
            // to ensure "file" is required (not null)
            if (file == null)
            {
                throw new InvalidDataException("file is a required property for DocumentTypeImportRequest and cannot be null");
            }
            else
            {
                this.File = file;
            }

            this.UpdateCache = updateCache;
            this.Action = action;
            this.SourceVersion = sourceVersion;
        }

        /// <summary>
        /// Gets or Sets File
        /// </summary>
        [DataMember(Name="file", EmitDefaultValue=true)]
        public System.IO.Stream File { get; set; }

        /// <summary>
        /// Gets or Sets UpdateCache
        /// </summary>
        [DataMember(Name="update_cache", EmitDefaultValue=false)]
        public bool UpdateCache { get; set; }


        /// <summary>
        /// Gets or Sets SourceVersion
        /// </summary>
        [DataMember(Name="source_version", EmitDefaultValue=false)]
        public string SourceVersion { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class DocumentTypeImportRequest {\n");
            sb.Append("  File: ").Append(File).Append("\n");
            sb.Append("  UpdateCache: ").Append(UpdateCache).Append("\n");
            sb.Append("  Action: ").Append(Action).Append("\n");
            sb.Append("  SourceVersion: ").Append(SourceVersion).Append("\n");
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
            return this.Equals(input as DocumentTypeImportRequest);
        }

        /// <summary>
        /// Returns true if DocumentTypeImportRequest instances are equal
        /// </summary>
        /// <param name="input">Instance of DocumentTypeImportRequest to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(DocumentTypeImportRequest input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.File == input.File ||
                    (this.File != null &&
                    this.File.Equals(input.File))
                ) && 
                (
                    this.UpdateCache == input.UpdateCache ||
                    (this.UpdateCache != null &&
                    this.UpdateCache.Equals(input.UpdateCache))
                ) && 
                (
                    this.Action == input.Action ||
                    (this.Action != null &&
                    this.Action.Equals(input.Action))
                ) && 
                (
                    this.SourceVersion == input.SourceVersion ||
                    (this.SourceVersion != null &&
                    this.SourceVersion.Equals(input.SourceVersion))
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
                if (this.File != null)
                    hashCode = hashCode * 59 + this.File.GetHashCode();
                if (this.UpdateCache != null)
                    hashCode = hashCode * 59 + this.UpdateCache.GetHashCode();
                if (this.Action != null)
                    hashCode = hashCode * 59 + this.Action.GetHashCode();
                if (this.SourceVersion != null)
                    hashCode = hashCode * 59 + this.SourceVersion.GetHashCode();
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
