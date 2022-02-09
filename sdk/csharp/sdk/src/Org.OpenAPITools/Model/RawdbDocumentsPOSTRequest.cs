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
    /// RawdbDocumentsPOSTRequest
    /// </summary>
    [DataContract]
    public partial class RawdbDocumentsPOSTRequest :  IEquatable<RawdbDocumentsPOSTRequest>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="RawdbDocumentsPOSTRequest" /> class.
        /// </summary>
        /// <param name="projectIds">projectIds.</param>
        /// <param name="columns">columns.</param>
        /// <param name="associatedText">associatedText.</param>
        /// <param name="asZip">asZip.</param>
        /// <param name="fmt">fmt.</param>
        /// <param name="limit">limit.</param>
        /// <param name="orderBy">orderBy.</param>
        /// <param name="savedFilters">savedFilters.</param>
        /// <param name="saveFilter">saveFilter.</param>
        /// <param name="returnReviewed">returnReviewed.</param>
        /// <param name="returnTotal">returnTotal.</param>
        /// <param name="returnData">returnData.</param>
        /// <param name="ignoreErrors">ignoreErrors.</param>
        /// <param name="filters">filters.</param>
        public RawdbDocumentsPOSTRequest(string projectIds = default(string), string columns = default(string), bool associatedText = default(bool), bool asZip = default(bool), string fmt = default(string), int limit = default(int), string orderBy = default(string), string savedFilters = default(string), bool saveFilter = default(bool), bool returnReviewed = default(bool), bool returnTotal = default(bool), bool returnData = default(bool), bool ignoreErrors = default(bool), Dictionary<string, string> filters = default(Dictionary<string, string>))
        {
            this.ProjectIds = projectIds;
            this.Columns = columns;
            this.AssociatedText = associatedText;
            this.AsZip = asZip;
            this.Fmt = fmt;
            this.Limit = limit;
            this.OrderBy = orderBy;
            this.SavedFilters = savedFilters;
            this.SaveFilter = saveFilter;
            this.ReturnReviewed = returnReviewed;
            this.ReturnTotal = returnTotal;
            this.ReturnData = returnData;
            this.IgnoreErrors = ignoreErrors;
            this.Filters = filters;
        }

        /// <summary>
        /// Gets or Sets ProjectIds
        /// </summary>
        [DataMember(Name="project_ids", EmitDefaultValue=false)]
        public string ProjectIds { get; set; }

        /// <summary>
        /// Gets or Sets Columns
        /// </summary>
        [DataMember(Name="columns", EmitDefaultValue=false)]
        public string Columns { get; set; }

        /// <summary>
        /// Gets or Sets AssociatedText
        /// </summary>
        [DataMember(Name="associated_text", EmitDefaultValue=false)]
        public bool AssociatedText { get; set; }

        /// <summary>
        /// Gets or Sets AsZip
        /// </summary>
        [DataMember(Name="as_zip", EmitDefaultValue=false)]
        public bool AsZip { get; set; }

        /// <summary>
        /// Gets or Sets Fmt
        /// </summary>
        [DataMember(Name="fmt", EmitDefaultValue=false)]
        public string Fmt { get; set; }

        /// <summary>
        /// Gets or Sets Limit
        /// </summary>
        [DataMember(Name="limit", EmitDefaultValue=false)]
        public int Limit { get; set; }

        /// <summary>
        /// Gets or Sets OrderBy
        /// </summary>
        [DataMember(Name="order_by", EmitDefaultValue=false)]
        public string OrderBy { get; set; }

        /// <summary>
        /// Gets or Sets SavedFilters
        /// </summary>
        [DataMember(Name="saved_filters", EmitDefaultValue=false)]
        public string SavedFilters { get; set; }

        /// <summary>
        /// Gets or Sets SaveFilter
        /// </summary>
        [DataMember(Name="save_filter", EmitDefaultValue=false)]
        public bool SaveFilter { get; set; }

        /// <summary>
        /// Gets or Sets ReturnReviewed
        /// </summary>
        [DataMember(Name="return_reviewed", EmitDefaultValue=false)]
        public bool ReturnReviewed { get; set; }

        /// <summary>
        /// Gets or Sets ReturnTotal
        /// </summary>
        [DataMember(Name="return_total", EmitDefaultValue=false)]
        public bool ReturnTotal { get; set; }

        /// <summary>
        /// Gets or Sets ReturnData
        /// </summary>
        [DataMember(Name="return_data", EmitDefaultValue=false)]
        public bool ReturnData { get; set; }

        /// <summary>
        /// Gets or Sets IgnoreErrors
        /// </summary>
        [DataMember(Name="ignore_errors", EmitDefaultValue=false)]
        public bool IgnoreErrors { get; set; }

        /// <summary>
        /// Gets or Sets Filters
        /// </summary>
        [DataMember(Name="filters", EmitDefaultValue=false)]
        public Dictionary<string, string> Filters { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class RawdbDocumentsPOSTRequest {\n");
            sb.Append("  ProjectIds: ").Append(ProjectIds).Append("\n");
            sb.Append("  Columns: ").Append(Columns).Append("\n");
            sb.Append("  AssociatedText: ").Append(AssociatedText).Append("\n");
            sb.Append("  AsZip: ").Append(AsZip).Append("\n");
            sb.Append("  Fmt: ").Append(Fmt).Append("\n");
            sb.Append("  Limit: ").Append(Limit).Append("\n");
            sb.Append("  OrderBy: ").Append(OrderBy).Append("\n");
            sb.Append("  SavedFilters: ").Append(SavedFilters).Append("\n");
            sb.Append("  SaveFilter: ").Append(SaveFilter).Append("\n");
            sb.Append("  ReturnReviewed: ").Append(ReturnReviewed).Append("\n");
            sb.Append("  ReturnTotal: ").Append(ReturnTotal).Append("\n");
            sb.Append("  ReturnData: ").Append(ReturnData).Append("\n");
            sb.Append("  IgnoreErrors: ").Append(IgnoreErrors).Append("\n");
            sb.Append("  Filters: ").Append(Filters).Append("\n");
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
            return this.Equals(input as RawdbDocumentsPOSTRequest);
        }

        /// <summary>
        /// Returns true if RawdbDocumentsPOSTRequest instances are equal
        /// </summary>
        /// <param name="input">Instance of RawdbDocumentsPOSTRequest to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(RawdbDocumentsPOSTRequest input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.ProjectIds == input.ProjectIds ||
                    (this.ProjectIds != null &&
                    this.ProjectIds.Equals(input.ProjectIds))
                ) && 
                (
                    this.Columns == input.Columns ||
                    (this.Columns != null &&
                    this.Columns.Equals(input.Columns))
                ) && 
                (
                    this.AssociatedText == input.AssociatedText ||
                    (this.AssociatedText != null &&
                    this.AssociatedText.Equals(input.AssociatedText))
                ) && 
                (
                    this.AsZip == input.AsZip ||
                    (this.AsZip != null &&
                    this.AsZip.Equals(input.AsZip))
                ) && 
                (
                    this.Fmt == input.Fmt ||
                    (this.Fmt != null &&
                    this.Fmt.Equals(input.Fmt))
                ) && 
                (
                    this.Limit == input.Limit ||
                    (this.Limit != null &&
                    this.Limit.Equals(input.Limit))
                ) && 
                (
                    this.OrderBy == input.OrderBy ||
                    (this.OrderBy != null &&
                    this.OrderBy.Equals(input.OrderBy))
                ) && 
                (
                    this.SavedFilters == input.SavedFilters ||
                    (this.SavedFilters != null &&
                    this.SavedFilters.Equals(input.SavedFilters))
                ) && 
                (
                    this.SaveFilter == input.SaveFilter ||
                    (this.SaveFilter != null &&
                    this.SaveFilter.Equals(input.SaveFilter))
                ) && 
                (
                    this.ReturnReviewed == input.ReturnReviewed ||
                    (this.ReturnReviewed != null &&
                    this.ReturnReviewed.Equals(input.ReturnReviewed))
                ) && 
                (
                    this.ReturnTotal == input.ReturnTotal ||
                    (this.ReturnTotal != null &&
                    this.ReturnTotal.Equals(input.ReturnTotal))
                ) && 
                (
                    this.ReturnData == input.ReturnData ||
                    (this.ReturnData != null &&
                    this.ReturnData.Equals(input.ReturnData))
                ) && 
                (
                    this.IgnoreErrors == input.IgnoreErrors ||
                    (this.IgnoreErrors != null &&
                    this.IgnoreErrors.Equals(input.IgnoreErrors))
                ) && 
                (
                    this.Filters == input.Filters ||
                    this.Filters != null &&
                    input.Filters != null &&
                    this.Filters.SequenceEqual(input.Filters)
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
                if (this.ProjectIds != null)
                    hashCode = hashCode * 59 + this.ProjectIds.GetHashCode();
                if (this.Columns != null)
                    hashCode = hashCode * 59 + this.Columns.GetHashCode();
                if (this.AssociatedText != null)
                    hashCode = hashCode * 59 + this.AssociatedText.GetHashCode();
                if (this.AsZip != null)
                    hashCode = hashCode * 59 + this.AsZip.GetHashCode();
                if (this.Fmt != null)
                    hashCode = hashCode * 59 + this.Fmt.GetHashCode();
                if (this.Limit != null)
                    hashCode = hashCode * 59 + this.Limit.GetHashCode();
                if (this.OrderBy != null)
                    hashCode = hashCode * 59 + this.OrderBy.GetHashCode();
                if (this.SavedFilters != null)
                    hashCode = hashCode * 59 + this.SavedFilters.GetHashCode();
                if (this.SaveFilter != null)
                    hashCode = hashCode * 59 + this.SaveFilter.GetHashCode();
                if (this.ReturnReviewed != null)
                    hashCode = hashCode * 59 + this.ReturnReviewed.GetHashCode();
                if (this.ReturnTotal != null)
                    hashCode = hashCode * 59 + this.ReturnTotal.GetHashCode();
                if (this.ReturnData != null)
                    hashCode = hashCode * 59 + this.ReturnData.GetHashCode();
                if (this.IgnoreErrors != null)
                    hashCode = hashCode * 59 + this.IgnoreErrors.GetHashCode();
                if (this.Filters != null)
                    hashCode = hashCode * 59 + this.Filters.GetHashCode();
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
