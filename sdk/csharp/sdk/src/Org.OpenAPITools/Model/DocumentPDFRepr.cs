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
    /// DocumentPDFRepr
    /// </summary>
    [DataContract]
    public partial class DocumentPDFRepr :  IEquatable<DocumentPDFRepr>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="DocumentPDFRepr" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        public DocumentPDFRepr()
        {
        }

        /// <summary>
        /// Gets or Sets CharBboxesList
        /// </summary>
        [DataMember(Name="char_bboxes_list", EmitDefaultValue=false)]
        public string CharBboxesList { get; private set; }

        /// <summary>
        /// Gets or Sets PagesList
        /// </summary>
        [DataMember(Name="pages_list", EmitDefaultValue=false)]
        public string PagesList { get; private set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class DocumentPDFRepr {\n");
            sb.Append("  CharBboxesList: ").Append(CharBboxesList).Append("\n");
            sb.Append("  PagesList: ").Append(PagesList).Append("\n");
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
            return this.Equals(input as DocumentPDFRepr);
        }

        /// <summary>
        /// Returns true if DocumentPDFRepr instances are equal
        /// </summary>
        /// <param name="input">Instance of DocumentPDFRepr to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(DocumentPDFRepr input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.CharBboxesList == input.CharBboxesList ||
                    (this.CharBboxesList != null &&
                    this.CharBboxesList.Equals(input.CharBboxesList))
                ) && 
                (
                    this.PagesList == input.PagesList ||
                    (this.PagesList != null &&
                    this.PagesList.Equals(input.PagesList))
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
                if (this.CharBboxesList != null)
                    hashCode = hashCode * 59 + this.CharBboxesList.GetHashCode();
                if (this.PagesList != null)
                    hashCode = hashCode * 59 + this.PagesList.GetHashCode();
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
