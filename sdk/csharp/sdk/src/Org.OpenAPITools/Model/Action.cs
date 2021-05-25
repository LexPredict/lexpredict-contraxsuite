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
    /// Action
    /// </summary>
    [DataContract]
    public partial class Action :  IEquatable<Action>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="Action" /> class.
        /// </summary>
        /// <param name="name">name.</param>
        /// <param name="message">message.</param>
        /// <param name="viewAction">viewAction.</param>
        /// <param name="objectPk">objectPk.</param>
        /// <param name="modelName">modelName.</param>
        /// <param name="requestData">requestData.</param>
        public Action(string name = default(string), string message = default(string), string viewAction = default(string), string objectPk = default(string), string modelName = default(string), Object requestData = default(Object))
        {
            this.Message = message;
            this.ViewAction = viewAction;
            this.ObjectPk = objectPk;
            this.ModelName = modelName;
            this.RequestData = requestData;
            this.Name = name;
            this.Message = message;
            this.ViewAction = viewAction;
            this.ObjectPk = objectPk;
            this.ModelName = modelName;
            this.RequestData = requestData;
        }

        /// <summary>
        /// Gets or Sets Id
        /// </summary>
        [DataMember(Name="id", EmitDefaultValue=false)]
        public int Id { get; private set; }

        /// <summary>
        /// Gets or Sets Name
        /// </summary>
        [DataMember(Name="name", EmitDefaultValue=false)]
        public string Name { get; set; }

        /// <summary>
        /// Gets or Sets Message
        /// </summary>
        [DataMember(Name="message", EmitDefaultValue=true)]
        public string Message { get; set; }

        /// <summary>
        /// Gets or Sets ViewAction
        /// </summary>
        [DataMember(Name="view_action", EmitDefaultValue=true)]
        public string ViewAction { get; set; }

        /// <summary>
        /// Gets or Sets ObjectPk
        /// </summary>
        [DataMember(Name="object_pk", EmitDefaultValue=true)]
        public string ObjectPk { get; set; }

        /// <summary>
        /// Gets or Sets ModelName
        /// </summary>
        [DataMember(Name="model_name", EmitDefaultValue=true)]
        public string ModelName { get; set; }

        /// <summary>
        /// Gets or Sets Date
        /// </summary>
        [DataMember(Name="date", EmitDefaultValue=false)]
        public DateTime Date { get; private set; }

        /// <summary>
        /// Gets or Sets UserName
        /// </summary>
        [DataMember(Name="user__name", EmitDefaultValue=false)]
        public string UserName { get; private set; }

        /// <summary>
        /// Gets or Sets RequestData
        /// </summary>
        [DataMember(Name="request_data", EmitDefaultValue=true)]
        public Object RequestData { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class Action {\n");
            sb.Append("  Id: ").Append(Id).Append("\n");
            sb.Append("  Name: ").Append(Name).Append("\n");
            sb.Append("  Message: ").Append(Message).Append("\n");
            sb.Append("  ViewAction: ").Append(ViewAction).Append("\n");
            sb.Append("  ObjectPk: ").Append(ObjectPk).Append("\n");
            sb.Append("  ModelName: ").Append(ModelName).Append("\n");
            sb.Append("  Date: ").Append(Date).Append("\n");
            sb.Append("  UserName: ").Append(UserName).Append("\n");
            sb.Append("  RequestData: ").Append(RequestData).Append("\n");
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
                    this.Id == input.Id ||
                    (this.Id != null &&
                    this.Id.Equals(input.Id))
                ) && 
                (
                    this.Name == input.Name ||
                    (this.Name != null &&
                    this.Name.Equals(input.Name))
                ) && 
                (
                    this.Message == input.Message ||
                    (this.Message != null &&
                    this.Message.Equals(input.Message))
                ) && 
                (
                    this.ViewAction == input.ViewAction ||
                    (this.ViewAction != null &&
                    this.ViewAction.Equals(input.ViewAction))
                ) && 
                (
                    this.ObjectPk == input.ObjectPk ||
                    (this.ObjectPk != null &&
                    this.ObjectPk.Equals(input.ObjectPk))
                ) && 
                (
                    this.ModelName == input.ModelName ||
                    (this.ModelName != null &&
                    this.ModelName.Equals(input.ModelName))
                ) && 
                (
                    this.Date == input.Date ||
                    (this.Date != null &&
                    this.Date.Equals(input.Date))
                ) && 
                (
                    this.UserName == input.UserName ||
                    (this.UserName != null &&
                    this.UserName.Equals(input.UserName))
                ) && 
                (
                    this.RequestData == input.RequestData ||
                    (this.RequestData != null &&
                    this.RequestData.Equals(input.RequestData))
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
                if (this.Name != null)
                    hashCode = hashCode * 59 + this.Name.GetHashCode();
                if (this.Message != null)
                    hashCode = hashCode * 59 + this.Message.GetHashCode();
                if (this.ViewAction != null)
                    hashCode = hashCode * 59 + this.ViewAction.GetHashCode();
                if (this.ObjectPk != null)
                    hashCode = hashCode * 59 + this.ObjectPk.GetHashCode();
                if (this.ModelName != null)
                    hashCode = hashCode * 59 + this.ModelName.GetHashCode();
                if (this.Date != null)
                    hashCode = hashCode * 59 + this.Date.GetHashCode();
                if (this.UserName != null)
                    hashCode = hashCode * 59 + this.UserName.GetHashCode();
                if (this.RequestData != null)
                    hashCode = hashCode * 59 + this.RequestData.GetHashCode();
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

 
            // ViewAction (string) maxLength
            if(this.ViewAction != null && this.ViewAction.Length > 50)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for ViewAction, length must be less than 50.", new [] { "ViewAction" });
            }

 
            // ObjectPk (string) maxLength
            if(this.ObjectPk != null && this.ObjectPk.Length > 36)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for ObjectPk, length must be less than 36.", new [] { "ObjectPk" });
            }

 
            // ModelName (string) maxLength
            if(this.ModelName != null && this.ModelName.Length > 50)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for ModelName, length must be less than 50.", new [] { "ModelName" });
            }

 
            yield break;
        }
    }

}