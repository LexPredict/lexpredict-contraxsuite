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
    /// CurrencyUsage
    /// </summary>
    [DataContract]
    public partial class CurrencyUsage :  IEquatable<CurrencyUsage>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="CurrencyUsage" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected CurrencyUsage() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="CurrencyUsage" /> class.
        /// </summary>
        /// <param name="usageType">usageType (required).</param>
        /// <param name="currency">currency (required).</param>
        /// <param name="amount">amount.</param>
        /// <param name="amountStr">amountStr.</param>
        public CurrencyUsage(string usageType = default(string), string currency = default(string), decimal? amount = default(decimal?), string amountStr = default(string))
        {
            // to ensure "usageType" is required (not null)
            if (usageType == null)
            {
                throw new InvalidDataException("usageType is a required property for CurrencyUsage and cannot be null");
            }
            else
            {
                this.UsageType = usageType;
            }
            
            // to ensure "currency" is required (not null)
            if (currency == null)
            {
                throw new InvalidDataException("currency is a required property for CurrencyUsage and cannot be null");
            }
            else
            {
                this.Currency = currency;
            }
            
            this.Amount = amount;
            this.AmountStr = amountStr;
            this.Amount = amount;
            this.AmountStr = amountStr;
        }
        
        /// <summary>
        /// Gets or Sets UsageType
        /// </summary>
        [DataMember(Name="usage_type", EmitDefaultValue=true)]
        public string UsageType { get; set; }

        /// <summary>
        /// Gets or Sets Currency
        /// </summary>
        [DataMember(Name="currency", EmitDefaultValue=true)]
        public string Currency { get; set; }

        /// <summary>
        /// Gets or Sets Amount
        /// </summary>
        [DataMember(Name="amount", EmitDefaultValue=true)]
        public decimal? Amount { get; set; }

        /// <summary>
        /// Gets or Sets AmountStr
        /// </summary>
        [DataMember(Name="amount_str", EmitDefaultValue=true)]
        public string AmountStr { get; set; }

        /// <summary>
        /// Gets or Sets Pk
        /// </summary>
        [DataMember(Name="pk", EmitDefaultValue=false)]
        public int Pk { get; private set; }

        /// <summary>
        /// Gets or Sets TextUnitPk
        /// </summary>
        [DataMember(Name="text_unit__pk", EmitDefaultValue=false)]
        public string TextUnitPk { get; private set; }

        /// <summary>
        /// Gets or Sets TextUnitUnitType
        /// </summary>
        [DataMember(Name="text_unit__unit_type", EmitDefaultValue=false)]
        public string TextUnitUnitType { get; private set; }

        /// <summary>
        /// Gets or Sets TextUnitLocationStart
        /// </summary>
        [DataMember(Name="text_unit__location_start", EmitDefaultValue=false)]
        public string TextUnitLocationStart { get; private set; }

        /// <summary>
        /// Gets or Sets TextUnitLocationEnd
        /// </summary>
        [DataMember(Name="text_unit__location_end", EmitDefaultValue=false)]
        public string TextUnitLocationEnd { get; private set; }

        /// <summary>
        /// Gets or Sets TextUnitDocumentPk
        /// </summary>
        [DataMember(Name="text_unit__document__pk", EmitDefaultValue=false)]
        public string TextUnitDocumentPk { get; private set; }

        /// <summary>
        /// Gets or Sets TextUnitDocumentName
        /// </summary>
        [DataMember(Name="text_unit__document__name", EmitDefaultValue=false)]
        public string TextUnitDocumentName { get; private set; }

        /// <summary>
        /// Gets or Sets TextUnitDocumentDescription
        /// </summary>
        [DataMember(Name="text_unit__document__description", EmitDefaultValue=false)]
        public string TextUnitDocumentDescription { get; private set; }

        /// <summary>
        /// Gets or Sets TextUnitDocumentDocumentType
        /// </summary>
        [DataMember(Name="text_unit__document__document_type", EmitDefaultValue=false)]
        public string TextUnitDocumentDocumentType { get; private set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class CurrencyUsage {\n");
            sb.Append("  UsageType: ").Append(UsageType).Append("\n");
            sb.Append("  Currency: ").Append(Currency).Append("\n");
            sb.Append("  Amount: ").Append(Amount).Append("\n");
            sb.Append("  AmountStr: ").Append(AmountStr).Append("\n");
            sb.Append("  Pk: ").Append(Pk).Append("\n");
            sb.Append("  TextUnitPk: ").Append(TextUnitPk).Append("\n");
            sb.Append("  TextUnitUnitType: ").Append(TextUnitUnitType).Append("\n");
            sb.Append("  TextUnitLocationStart: ").Append(TextUnitLocationStart).Append("\n");
            sb.Append("  TextUnitLocationEnd: ").Append(TextUnitLocationEnd).Append("\n");
            sb.Append("  TextUnitDocumentPk: ").Append(TextUnitDocumentPk).Append("\n");
            sb.Append("  TextUnitDocumentName: ").Append(TextUnitDocumentName).Append("\n");
            sb.Append("  TextUnitDocumentDescription: ").Append(TextUnitDocumentDescription).Append("\n");
            sb.Append("  TextUnitDocumentDocumentType: ").Append(TextUnitDocumentDocumentType).Append("\n");
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
            return this.Equals(input as CurrencyUsage);
        }

        /// <summary>
        /// Returns true if CurrencyUsage instances are equal
        /// </summary>
        /// <param name="input">Instance of CurrencyUsage to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(CurrencyUsage input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.UsageType == input.UsageType ||
                    (this.UsageType != null &&
                    this.UsageType.Equals(input.UsageType))
                ) && 
                (
                    this.Currency == input.Currency ||
                    (this.Currency != null &&
                    this.Currency.Equals(input.Currency))
                ) && 
                (
                    this.Amount == input.Amount ||
                    (this.Amount != null &&
                    this.Amount.Equals(input.Amount))
                ) && 
                (
                    this.AmountStr == input.AmountStr ||
                    (this.AmountStr != null &&
                    this.AmountStr.Equals(input.AmountStr))
                ) && 
                (
                    this.Pk == input.Pk ||
                    (this.Pk != null &&
                    this.Pk.Equals(input.Pk))
                ) && 
                (
                    this.TextUnitPk == input.TextUnitPk ||
                    (this.TextUnitPk != null &&
                    this.TextUnitPk.Equals(input.TextUnitPk))
                ) && 
                (
                    this.TextUnitUnitType == input.TextUnitUnitType ||
                    (this.TextUnitUnitType != null &&
                    this.TextUnitUnitType.Equals(input.TextUnitUnitType))
                ) && 
                (
                    this.TextUnitLocationStart == input.TextUnitLocationStart ||
                    (this.TextUnitLocationStart != null &&
                    this.TextUnitLocationStart.Equals(input.TextUnitLocationStart))
                ) && 
                (
                    this.TextUnitLocationEnd == input.TextUnitLocationEnd ||
                    (this.TextUnitLocationEnd != null &&
                    this.TextUnitLocationEnd.Equals(input.TextUnitLocationEnd))
                ) && 
                (
                    this.TextUnitDocumentPk == input.TextUnitDocumentPk ||
                    (this.TextUnitDocumentPk != null &&
                    this.TextUnitDocumentPk.Equals(input.TextUnitDocumentPk))
                ) && 
                (
                    this.TextUnitDocumentName == input.TextUnitDocumentName ||
                    (this.TextUnitDocumentName != null &&
                    this.TextUnitDocumentName.Equals(input.TextUnitDocumentName))
                ) && 
                (
                    this.TextUnitDocumentDescription == input.TextUnitDocumentDescription ||
                    (this.TextUnitDocumentDescription != null &&
                    this.TextUnitDocumentDescription.Equals(input.TextUnitDocumentDescription))
                ) && 
                (
                    this.TextUnitDocumentDocumentType == input.TextUnitDocumentDocumentType ||
                    (this.TextUnitDocumentDocumentType != null &&
                    this.TextUnitDocumentDocumentType.Equals(input.TextUnitDocumentDocumentType))
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
                if (this.UsageType != null)
                    hashCode = hashCode * 59 + this.UsageType.GetHashCode();
                if (this.Currency != null)
                    hashCode = hashCode * 59 + this.Currency.GetHashCode();
                if (this.Amount != null)
                    hashCode = hashCode * 59 + this.Amount.GetHashCode();
                if (this.AmountStr != null)
                    hashCode = hashCode * 59 + this.AmountStr.GetHashCode();
                if (this.Pk != null)
                    hashCode = hashCode * 59 + this.Pk.GetHashCode();
                if (this.TextUnitPk != null)
                    hashCode = hashCode * 59 + this.TextUnitPk.GetHashCode();
                if (this.TextUnitUnitType != null)
                    hashCode = hashCode * 59 + this.TextUnitUnitType.GetHashCode();
                if (this.TextUnitLocationStart != null)
                    hashCode = hashCode * 59 + this.TextUnitLocationStart.GetHashCode();
                if (this.TextUnitLocationEnd != null)
                    hashCode = hashCode * 59 + this.TextUnitLocationEnd.GetHashCode();
                if (this.TextUnitDocumentPk != null)
                    hashCode = hashCode * 59 + this.TextUnitDocumentPk.GetHashCode();
                if (this.TextUnitDocumentName != null)
                    hashCode = hashCode * 59 + this.TextUnitDocumentName.GetHashCode();
                if (this.TextUnitDocumentDescription != null)
                    hashCode = hashCode * 59 + this.TextUnitDocumentDescription.GetHashCode();
                if (this.TextUnitDocumentDocumentType != null)
                    hashCode = hashCode * 59 + this.TextUnitDocumentDocumentType.GetHashCode();
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
            // UsageType (string) maxLength
            if(this.UsageType != null && this.UsageType.Length > 1024)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for UsageType, length must be less than 1024.", new [] { "UsageType" });
            }

            
            // Currency (string) maxLength
            if(this.Currency != null && this.Currency.Length > 1024)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for Currency, length must be less than 1024.", new [] { "Currency" });
            }

            
            // AmountStr (string) maxLength
            if(this.AmountStr != null && this.AmountStr.Length > 300)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for AmountStr, length must be less than 300.", new [] { "AmountStr" });
            }

            
            yield break;
        }
    }

}
