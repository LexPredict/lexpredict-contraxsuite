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
    /// Register
    /// </summary>
    [DataContract]
    public partial class Register :  IEquatable<Register>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="Register" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected Register() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="Register" /> class.
        /// </summary>
        /// <param name="username">username (required).</param>
        /// <param name="email">email (required).</param>
        /// <param name="password1">password1 (required).</param>
        /// <param name="password2">password2 (required).</param>
        public Register(string username = default(string), string email = default(string), string password1 = default(string), string password2 = default(string))
        {
            // to ensure "username" is required (not null)
            if (username == null)
            {
                throw new InvalidDataException("username is a required property for Register and cannot be null");
            }
            else
            {
                this.Username = username;
            }

            // to ensure "email" is required (not null)
            if (email == null)
            {
                throw new InvalidDataException("email is a required property for Register and cannot be null");
            }
            else
            {
                this.Email = email;
            }

            // to ensure "password1" is required (not null)
            if (password1 == null)
            {
                throw new InvalidDataException("password1 is a required property for Register and cannot be null");
            }
            else
            {
                this.Password1 = password1;
            }

            // to ensure "password2" is required (not null)
            if (password2 == null)
            {
                throw new InvalidDataException("password2 is a required property for Register and cannot be null");
            }
            else
            {
                this.Password2 = password2;
            }

        }

        /// <summary>
        /// Gets or Sets Username
        /// </summary>
        [DataMember(Name="username", EmitDefaultValue=true)]
        public string Username { get; set; }

        /// <summary>
        /// Gets or Sets Email
        /// </summary>
        [DataMember(Name="email", EmitDefaultValue=true)]
        public string Email { get; set; }

        /// <summary>
        /// Gets or Sets Password1
        /// </summary>
        [DataMember(Name="password1", EmitDefaultValue=true)]
        public string Password1 { get; set; }

        /// <summary>
        /// Gets or Sets Password2
        /// </summary>
        [DataMember(Name="password2", EmitDefaultValue=true)]
        public string Password2 { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class Register {\n");
            sb.Append("  Username: ").Append(Username).Append("\n");
            sb.Append("  Email: ").Append(Email).Append("\n");
            sb.Append("  Password1: ").Append(Password1).Append("\n");
            sb.Append("  Password2: ").Append(Password2).Append("\n");
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
            return this.Equals(input as Register);
        }

        /// <summary>
        /// Returns true if Register instances are equal
        /// </summary>
        /// <param name="input">Instance of Register to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(Register input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.Username == input.Username ||
                    (this.Username != null &&
                    this.Username.Equals(input.Username))
                ) && 
                (
                    this.Email == input.Email ||
                    (this.Email != null &&
                    this.Email.Equals(input.Email))
                ) && 
                (
                    this.Password1 == input.Password1 ||
                    (this.Password1 != null &&
                    this.Password1.Equals(input.Password1))
                ) && 
                (
                    this.Password2 == input.Password2 ||
                    (this.Password2 != null &&
                    this.Password2.Equals(input.Password2))
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
                if (this.Username != null)
                    hashCode = hashCode * 59 + this.Username.GetHashCode();
                if (this.Email != null)
                    hashCode = hashCode * 59 + this.Email.GetHashCode();
                if (this.Password1 != null)
                    hashCode = hashCode * 59 + this.Password1.GetHashCode();
                if (this.Password2 != null)
                    hashCode = hashCode * 59 + this.Password2.GetHashCode();
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
            // Username (string) maxLength
            if(this.Username != null && this.Username.Length > 150)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for Username, length must be less than 150.", new [] { "Username" });
            }

            // Username (string) minLength
            if(this.Username != null && this.Username.Length < 1)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for Username, length must be greater than 1.", new [] { "Username" });
            }
 
            yield break;
        }
    }

}
