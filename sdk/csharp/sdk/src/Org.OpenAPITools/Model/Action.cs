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
    /// Action
    /// </summary>
    [DataContract]
    public partial class Action :  IEquatable<Action>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="Action" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected Action() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="Action" /> class.
        /// </summary>
        /// <param name="name">name.</param>
        /// <param name="user">user (required).</param>
        /// <param name="contentType">contentType (required).</param>
        /// <param name="objectPk">objectPk.</param>
        /// <param name="appLabel">appLabel.</param>
        /// <param name="modelName">modelName.</param>
        /// <param name="objectStr">objectStr.</param>
        public Action(string name = default(string), ProjectDetailOwnersData user = default(ProjectDetailOwnersData), int contentType = default(int), string objectPk = default(string), string appLabel = default(string), string modelName = default(string), string objectStr = default(string))
        {
            // to ensure "user" is required (not null)
            if (user == null)
            {
                throw new InvalidDataException("user is a required property for Action and cannot be null");
            }
            else
            {
                this.User = user;
            }
            
            // to ensure "contentType" is required (not null)
            if (contentType == null)
            {
                throw new InvalidDataException("contentType is a required property for Action and cannot be null");
            }
            else
            {
                this.ContentType = contentType;
            }
            
            this.ObjectPk = objectPk;
            this.AppLabel = appLabel;
            this.ModelName = modelName;
            this.ObjectStr = objectStr;
            this.Name = name;
            this.ObjectPk = objectPk;
            this.AppLabel = appLabel;
            this.ModelName = modelName;
            this.ObjectStr = objectStr;
        }
        
        /// <summary>
        /// Gets or Sets Pk
        /// </summary>
        [DataMember(Name="pk", EmitDefaultValue=false)]
        public int Pk { get; private set; }

        /// <summary>
        /// Gets or Sets Name
        /// </summary>
        [DataMember(Name="name", EmitDefaultValue=false)]
        public string Name { get; set; }

        /// <summary>
        /// Gets or Sets User
        /// </summary>
        [DataMember(Name="user", EmitDefaultValue=true)]
        public ProjectDetailOwnersData User { get; set; }

        /// <summary>
        /// Gets or Sets ContentType
        /// </summary>
        [DataMember(Name="content_type", EmitDefaultValue=true)]
        public int ContentType { get; set; }

        /// <summary>
        /// Gets or Sets ObjectPk
        /// </summary>
        [DataMember(Name="object_pk", EmitDefaultValue=true)]
        public string ObjectPk { get; set; }

        /// <summary>
        /// Gets or Sets Date
        /// </summary>
        [DataMember(Name="date", EmitDefaultValue=false)]
        public DateTime Date { get; private set; }

        /// <summary>
        /// Gets or Sets AppLabel
        /// </summary>
        [DataMember(Name="app_label", EmitDefaultValue=true)]
        public string AppLabel { get; set; }

        /// <summary>
        /// Gets or Sets ModelName
        /// </summary>
        [DataMember(Name="model_name", EmitDefaultValue=true)]
        public string ModelName { get; set; }

        /// <summary>
        /// Gets or Sets ObjectStr
        /// </summary>
        [DataMember(Name="object_str", EmitDefaultValue=true)]
        public string ObjectStr { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class Action {\n");
            sb.Append("  Pk: ").Append(Pk).Append("\n");
            sb.Append("  Name: ").Append(Name).Append("\n");
            sb.Append("  User: ").Append(User).Append("\n");
            sb.Append("  ContentType: ").Append(ContentType).Append("\n");
            sb.Append("  ObjectPk: ").Append(ObjectPk).Append("\n");
            sb.Append("  Date: ").Append(Date).Append("\n");
            sb.Append("  AppLabel: ").Append(AppLabel).Append("\n");
            sb.Append("  ModelName: ").Append(ModelName).Append("\n");
            sb.Append("  ObjectStr: ").Append(ObjectStr).Append("\n");
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
            return this.Equals(input as Action);
        }

        /// <summary>
        /// Returns true if Action instances are equal
        /// </summary>
        /// <param name="input">Instance of Action to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(Action input)
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
                    this.User == input.User ||
                    (this.User != null &&
                    this.User.Equals(input.User))
                ) && 
                (
                    this.ContentType == input.ContentType ||
                    (this.ContentType != null &&
                    this.ContentType.Equals(input.ContentType))
                ) && 
                (
                    this.ObjectPk == input.ObjectPk ||
                    (this.ObjectPk != null &&
                    this.ObjectPk.Equals(input.ObjectPk))
                ) && 
                (
                    this.Date == input.Date ||
                    (this.Date != null &&
                    this.Date.Equals(input.Date))
                ) && 
                (
                    this.AppLabel == input.AppLabel ||
                    (this.AppLabel != null &&
                    this.AppLabel.Equals(input.AppLabel))
                ) && 
                (
                    this.ModelName == input.ModelName ||
                    (this.ModelName != null &&
                    this.ModelName.Equals(input.ModelName))
                ) && 
                (
                    this.ObjectStr == input.ObjectStr ||
                    (this.ObjectStr != null &&
                    this.ObjectStr.Equals(input.ObjectStr))
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
                if (this.User != null)
                    hashCode = hashCode * 59 + this.User.GetHashCode();
                if (this.ContentType != null)
                    hashCode = hashCode * 59 + this.ContentType.GetHashCode();
                if (this.ObjectPk != null)
                    hashCode = hashCode * 59 + this.ObjectPk.GetHashCode();
                if (this.Date != null)
                    hashCode = hashCode * 59 + this.Date.GetHashCode();
                if (this.AppLabel != null)
                    hashCode = hashCode * 59 + this.AppLabel.GetHashCode();
                if (this.ModelName != null)
                    hashCode = hashCode * 59 + this.ModelName.GetHashCode();
                if (this.ObjectStr != null)
                    hashCode = hashCode * 59 + this.ObjectStr.GetHashCode();
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
            // Name (string) maxLength
            if(this.Name != null && this.Name.Length > 50)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for Name, length must be less than 50.", new [] { "Name" });
            }

            
            // ObjectPk (string) maxLength
            if(this.ObjectPk != null && this.ObjectPk.Length > 36)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for ObjectPk, length must be less than 36.", new [] { "ObjectPk" });
            }

            
            // AppLabel (string) maxLength
            if(this.AppLabel != null && this.AppLabel.Length > 20)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for AppLabel, length must be less than 20.", new [] { "AppLabel" });
            }

            
            // ModelName (string) maxLength
            if(this.ModelName != null && this.ModelName.Length > 50)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for ModelName, length must be less than 50.", new [] { "ModelName" });
            }

            
            // ObjectStr (string) maxLength
            if(this.ObjectStr != null && this.ObjectStr.Length > 200)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for ObjectStr, length must be less than 200.", new [] { "ObjectStr" });
            }

            
            yield break;
        }
    }

}
