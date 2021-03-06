/* 
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 1.0.0
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
    /// DocumentTypeCreate
    /// </summary>
    [DataContract]
    public partial class DocumentTypeCreate :  IEquatable<DocumentTypeCreate>, IValidatableObject
    {
        /// <summary>
        /// Defines EditorType
        /// </summary>
        [JsonConverter(typeof(StringEnumConverter))]
        public enum EditorTypeEnum
        {
            /// <summary>
            /// Enum Savebyfield for value: save_by_field
            /// </summary>
            [EnumMember(Value = "save_by_field")]
            Savebyfield = 1,

            /// <summary>
            /// Enum Saveallfieldsatonce for value: save_all_fields_at_once
            /// </summary>
            [EnumMember(Value = "save_all_fields_at_once")]
            Saveallfieldsatonce = 2,

            /// <summary>
            /// Enum Notext for value: no_text
            /// </summary>
            [EnumMember(Value = "no_text")]
            Notext = 3

        }

        /// <summary>
        /// Gets or Sets EditorType
        /// </summary>
        [DataMember(Name="editor_type", EmitDefaultValue=true)]
        public EditorTypeEnum? EditorType { get; set; }
        /// <summary>
        /// Initializes a new instance of the <see cref="DocumentTypeCreate" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected DocumentTypeCreate() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="DocumentTypeCreate" /> class.
        /// </summary>
        /// <param name="title">title (required).</param>
        /// <param name="code">Field codes must be lowercase, should start with a Latin letter, and contain  only Latin letters, digits, and underscores. (required).</param>
        /// <param name="managers">managers.</param>
        /// <param name="searchFields">searchFields.</param>
        /// <param name="editorType">editorType.</param>
        /// <param name="fieldCodeAliases">fieldCodeAliases.</param>
        /// <param name="metadata">metadata.</param>
        public DocumentTypeCreate(string title = default(string), string code = default(string), List<int> managers = default(List<int>), List<string> searchFields = default(List<string>), EditorTypeEnum? editorType = default(EditorTypeEnum?), Object fieldCodeAliases = default(Object), Object metadata = default(Object))
        {
            // to ensure "title" is required (not null)
            if (title == null)
            {
                throw new InvalidDataException("title is a required property for DocumentTypeCreate and cannot be null");
            }
            else
            {
                this.Title = title;
            }
            
            // to ensure "code" is required (not null)
            if (code == null)
            {
                throw new InvalidDataException("code is a required property for DocumentTypeCreate and cannot be null");
            }
            else
            {
                this.Code = code;
            }
            
            this.EditorType = editorType;
            this.FieldCodeAliases = fieldCodeAliases;
            this.Metadata = metadata;
            this.Managers = managers;
            this.SearchFields = searchFields;
            this.EditorType = editorType;
            this.FieldCodeAliases = fieldCodeAliases;
            this.Metadata = metadata;
        }
        
        /// <summary>
        /// Gets or Sets Uid
        /// </summary>
        [DataMember(Name="uid", EmitDefaultValue=false)]
        public Guid Uid { get; private set; }

        /// <summary>
        /// Gets or Sets Title
        /// </summary>
        [DataMember(Name="title", EmitDefaultValue=true)]
        public string Title { get; set; }

        /// <summary>
        /// Field codes must be lowercase, should start with a Latin letter, and contain  only Latin letters, digits, and underscores.
        /// </summary>
        /// <value>Field codes must be lowercase, should start with a Latin letter, and contain  only Latin letters, digits, and underscores.</value>
        [DataMember(Name="code", EmitDefaultValue=true)]
        public string Code { get; set; }

        /// <summary>
        /// Gets or Sets Categories
        /// </summary>
        [DataMember(Name="categories", EmitDefaultValue=false)]
        public List<DocumentTypeDetailCategories> Categories { get; private set; }

        /// <summary>
        /// Gets or Sets Managers
        /// </summary>
        [DataMember(Name="managers", EmitDefaultValue=false)]
        public List<int> Managers { get; set; }

        /// <summary>
        /// Gets or Sets Fields
        /// </summary>
        [DataMember(Name="fields", EmitDefaultValue=false)]
        public List<DocumentFieldCategoryListFields> Fields { get; private set; }

        /// <summary>
        /// Gets or Sets SearchFields
        /// </summary>
        [DataMember(Name="search_fields", EmitDefaultValue=false)]
        public List<string> SearchFields { get; set; }


        /// <summary>
        /// Gets or Sets FieldCodeAliases
        /// </summary>
        [DataMember(Name="field_code_aliases", EmitDefaultValue=true)]
        public Object FieldCodeAliases { get; set; }

        /// <summary>
        /// Gets or Sets Metadata
        /// </summary>
        [DataMember(Name="metadata", EmitDefaultValue=true)]
        public Object Metadata { get; set; }

        /// <summary>
        /// Gets or Sets WarningMessage
        /// </summary>
        [DataMember(Name="warning_message", EmitDefaultValue=false)]
        public string WarningMessage { get; private set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class DocumentTypeCreate {\n");
            sb.Append("  Uid: ").Append(Uid).Append("\n");
            sb.Append("  Title: ").Append(Title).Append("\n");
            sb.Append("  Code: ").Append(Code).Append("\n");
            sb.Append("  Categories: ").Append(Categories).Append("\n");
            sb.Append("  Managers: ").Append(Managers).Append("\n");
            sb.Append("  Fields: ").Append(Fields).Append("\n");
            sb.Append("  SearchFields: ").Append(SearchFields).Append("\n");
            sb.Append("  EditorType: ").Append(EditorType).Append("\n");
            sb.Append("  FieldCodeAliases: ").Append(FieldCodeAliases).Append("\n");
            sb.Append("  Metadata: ").Append(Metadata).Append("\n");
            sb.Append("  WarningMessage: ").Append(WarningMessage).Append("\n");
            sb.Append("}\n");
            return sb.ToString();
        }
  
        /// <summary>
        /// Returns the JSON string presentation of the object
        /// </summary>
        /// <returns>JSON string presentation of the object</returns>
        public virtual string ToJson()
        {
            return JsonConvert.SerializeObject(this, Formatting.Indented);
        }

        /// <summary>
        /// Returns true if objects are equal
        /// </summary>
        /// <param name="input">Object to be compared</param>
        /// <returns>Boolean</returns>
        public override bool Equals(object input)
        {
            return this.Equals(input as DocumentTypeCreate);
        }

        /// <summary>
        /// Returns true if DocumentTypeCreate instances are equal
        /// </summary>
        /// <param name="input">Instance of DocumentTypeCreate to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(DocumentTypeCreate input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.Uid == input.Uid ||
                    (this.Uid != null &&
                    this.Uid.Equals(input.Uid))
                ) && 
                (
                    this.Title == input.Title ||
                    (this.Title != null &&
                    this.Title.Equals(input.Title))
                ) && 
                (
                    this.Code == input.Code ||
                    (this.Code != null &&
                    this.Code.Equals(input.Code))
                ) && 
                (
                    this.Categories == input.Categories ||
                    this.Categories != null &&
                    input.Categories != null &&
                    this.Categories.SequenceEqual(input.Categories)
                ) && 
                (
                    this.Managers == input.Managers ||
                    this.Managers != null &&
                    input.Managers != null &&
                    this.Managers.SequenceEqual(input.Managers)
                ) && 
                (
                    this.Fields == input.Fields ||
                    this.Fields != null &&
                    input.Fields != null &&
                    this.Fields.SequenceEqual(input.Fields)
                ) && 
                (
                    this.SearchFields == input.SearchFields ||
                    this.SearchFields != null &&
                    input.SearchFields != null &&
                    this.SearchFields.SequenceEqual(input.SearchFields)
                ) && 
                (
                    this.EditorType == input.EditorType ||
                    (this.EditorType != null &&
                    this.EditorType.Equals(input.EditorType))
                ) && 
                (
                    this.FieldCodeAliases == input.FieldCodeAliases ||
                    (this.FieldCodeAliases != null &&
                    this.FieldCodeAliases.Equals(input.FieldCodeAliases))
                ) && 
                (
                    this.Metadata == input.Metadata ||
                    (this.Metadata != null &&
                    this.Metadata.Equals(input.Metadata))
                ) && 
                (
                    this.WarningMessage == input.WarningMessage ||
                    (this.WarningMessage != null &&
                    this.WarningMessage.Equals(input.WarningMessage))
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
                if (this.Uid != null)
                    hashCode = hashCode * 59 + this.Uid.GetHashCode();
                if (this.Title != null)
                    hashCode = hashCode * 59 + this.Title.GetHashCode();
                if (this.Code != null)
                    hashCode = hashCode * 59 + this.Code.GetHashCode();
                if (this.Categories != null)
                    hashCode = hashCode * 59 + this.Categories.GetHashCode();
                if (this.Managers != null)
                    hashCode = hashCode * 59 + this.Managers.GetHashCode();
                if (this.Fields != null)
                    hashCode = hashCode * 59 + this.Fields.GetHashCode();
                if (this.SearchFields != null)
                    hashCode = hashCode * 59 + this.SearchFields.GetHashCode();
                if (this.EditorType != null)
                    hashCode = hashCode * 59 + this.EditorType.GetHashCode();
                if (this.FieldCodeAliases != null)
                    hashCode = hashCode * 59 + this.FieldCodeAliases.GetHashCode();
                if (this.Metadata != null)
                    hashCode = hashCode * 59 + this.Metadata.GetHashCode();
                if (this.WarningMessage != null)
                    hashCode = hashCode * 59 + this.WarningMessage.GetHashCode();
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
            // Title (string) maxLength
            if(this.Title != null && this.Title.Length > 100)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for Title, length must be less than 100.", new [] { "Title" });
            }

            
            // Code (string) maxLength
            if(this.Code != null && this.Code.Length > 50)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for Code, length must be less than 50.", new [] { "Code" });
            }

            
            yield break;
        }
    }

}
