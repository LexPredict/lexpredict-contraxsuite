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
    /// ProjectDetail
    /// </summary>
    [DataContract]
    public partial class ProjectDetail :  IEquatable<ProjectDetail>, IValidatableObject
    {
        /// <summary>
        /// Initializes a new instance of the <see cref="ProjectDetail" /> class.
        /// </summary>
        [JsonConstructorAttribute]
        protected ProjectDetail() { }
        /// <summary>
        /// Initializes a new instance of the <see cref="ProjectDetail" /> class.
        /// </summary>
        /// <param name="name">name (required).</param>
        /// <param name="description">description.</param>
        /// <param name="createdDate">createdDate.</param>
        /// <param name="createdByName">createdByName (required).</param>
        /// <param name="modifiedDate">modifiedDate.</param>
        /// <param name="modifiedByName">modifiedByName (required).</param>
        /// <param name="sendEmailNotification">sendEmailNotification.</param>
        /// <param name="hideClauseReview">hideClauseReview.</param>
        /// <param name="status">status.</param>
        /// <param name="statusData">statusData.</param>
        /// <param name="owners">owners.</param>
        /// <param name="reviewers">reviewers.</param>
        /// <param name="superReviewers">superReviewers.</param>
        /// <param name="juniorReviewers">juniorReviewers.</param>
        /// <param name="type">type.</param>
        /// <param name="typeData">typeData (required).</param>
        /// <param name="termTags">termTags.</param>
        /// <param name="documentTransformer">documentTransformer.</param>
        /// <param name="textUnitTransformer">textUnitTransformer.</param>
        /// <param name="companytypeTags">companytypeTags.</param>
        public ProjectDetail(string name = default(string), string description = default(string), DateTime? createdDate = default(DateTime?), string createdByName = default(string), DateTime? modifiedDate = default(DateTime?), string modifiedByName = default(string), bool sendEmailNotification = default(bool), bool hideClauseReview = default(bool), int status = default(int), ProjectListStatusData statusData = default(ProjectListStatusData), List<int> owners = default(List<int>), List<int> reviewers = default(List<int>), List<int> superReviewers = default(List<int>), List<int> juniorReviewers = default(List<int>), string type = default(string), ProjectListTypeData typeData = default(ProjectListTypeData), List<int> termTags = default(List<int>), int? documentTransformer = default(int?), int? textUnitTransformer = default(int?), List<int> companytypeTags = default(List<int>))
        {
            // to ensure "name" is required (not null)
            if (name == null)
            {
                throw new InvalidDataException("name is a required property for ProjectDetail and cannot be null");
            }
            else
            {
                this.Name = name;
            }

            this.Description = description;
            this.CreatedDate = createdDate;
            // to ensure "createdByName" is required (not null)
            if (createdByName == null)
            {
                throw new InvalidDataException("createdByName is a required property for ProjectDetail and cannot be null");
            }
            else
            {
                this.CreatedByName = createdByName;
            }

            this.ModifiedDate = modifiedDate;
            // to ensure "modifiedByName" is required (not null)
            if (modifiedByName == null)
            {
                throw new InvalidDataException("modifiedByName is a required property for ProjectDetail and cannot be null");
            }
            else
            {
                this.ModifiedByName = modifiedByName;
            }

            // to ensure "typeData" is required (not null)
            if (typeData == null)
            {
                throw new InvalidDataException("typeData is a required property for ProjectDetail and cannot be null");
            }
            else
            {
                this.TypeData = typeData;
            }

            this.DocumentTransformer = documentTransformer;
            this.TextUnitTransformer = textUnitTransformer;
            this.Description = description;
            this.CreatedDate = createdDate;
            this.ModifiedDate = modifiedDate;
            this.SendEmailNotification = sendEmailNotification;
            this.HideClauseReview = hideClauseReview;
            this.Status = status;
            this.StatusData = statusData;
            this.Owners = owners;
            this.Reviewers = reviewers;
            this.SuperReviewers = superReviewers;
            this.JuniorReviewers = juniorReviewers;
            this.Type = type;
            this.TermTags = termTags;
            this.DocumentTransformer = documentTransformer;
            this.TextUnitTransformer = textUnitTransformer;
            this.CompanytypeTags = companytypeTags;
        }

        /// <summary>
        /// Gets or Sets Pk
        /// </summary>
        [DataMember(Name="pk", EmitDefaultValue=false)]
        public int Pk { get; private set; }

        /// <summary>
        /// Gets or Sets Name
        /// </summary>
        [DataMember(Name="name", EmitDefaultValue=true)]
        public string Name { get; set; }

        /// <summary>
        /// Gets or Sets Description
        /// </summary>
        [DataMember(Name="description", EmitDefaultValue=true)]
        public string Description { get; set; }

        /// <summary>
        /// Gets or Sets CreatedDate
        /// </summary>
        [DataMember(Name="created_date", EmitDefaultValue=true)]
        public DateTime? CreatedDate { get; set; }

        /// <summary>
        /// Gets or Sets CreatedByName
        /// </summary>
        [DataMember(Name="created_by_name", EmitDefaultValue=true)]
        public string CreatedByName { get; set; }

        /// <summary>
        /// Gets or Sets ModifiedDate
        /// </summary>
        [DataMember(Name="modified_date", EmitDefaultValue=true)]
        public DateTime? ModifiedDate { get; set; }

        /// <summary>
        /// Gets or Sets ModifiedByName
        /// </summary>
        [DataMember(Name="modified_by_name", EmitDefaultValue=true)]
        public string ModifiedByName { get; set; }

        /// <summary>
        /// Gets or Sets SendEmailNotification
        /// </summary>
        [DataMember(Name="send_email_notification", EmitDefaultValue=false)]
        public bool SendEmailNotification { get; set; }

        /// <summary>
        /// Gets or Sets HideClauseReview
        /// </summary>
        [DataMember(Name="hide_clause_review", EmitDefaultValue=false)]
        public bool HideClauseReview { get; set; }

        /// <summary>
        /// Gets or Sets Status
        /// </summary>
        [DataMember(Name="status", EmitDefaultValue=false)]
        public int Status { get; set; }

        /// <summary>
        /// Gets or Sets StatusData
        /// </summary>
        [DataMember(Name="status_data", EmitDefaultValue=false)]
        public ProjectListStatusData StatusData { get; set; }

        /// <summary>
        /// Gets or Sets Owners
        /// </summary>
        [DataMember(Name="owners", EmitDefaultValue=false)]
        public List<int> Owners { get; set; }

        /// <summary>
        /// Gets or Sets OwnersData
        /// </summary>
        [DataMember(Name="owners_data", EmitDefaultValue=false)]
        public List<ProjectDetailOwnersData> OwnersData { get; private set; }

        /// <summary>
        /// Gets or Sets Reviewers
        /// </summary>
        [DataMember(Name="reviewers", EmitDefaultValue=false)]
        public List<int> Reviewers { get; set; }

        /// <summary>
        /// Gets or Sets ReviewersData
        /// </summary>
        [DataMember(Name="reviewers_data", EmitDefaultValue=false)]
        public List<ProjectDetailOwnersData> ReviewersData { get; private set; }

        /// <summary>
        /// Gets or Sets SuperReviewers
        /// </summary>
        [DataMember(Name="super_reviewers", EmitDefaultValue=false)]
        public List<int> SuperReviewers { get; set; }

        /// <summary>
        /// Gets or Sets SuperReviewersData
        /// </summary>
        [DataMember(Name="super_reviewers_data", EmitDefaultValue=false)]
        public List<ProjectDetailOwnersData> SuperReviewersData { get; private set; }

        /// <summary>
        /// Gets or Sets JuniorReviewers
        /// </summary>
        [DataMember(Name="junior_reviewers", EmitDefaultValue=false)]
        public List<int> JuniorReviewers { get; set; }

        /// <summary>
        /// Gets or Sets JuniorReviewersData
        /// </summary>
        [DataMember(Name="junior_reviewers_data", EmitDefaultValue=false)]
        public List<ProjectDetailOwnersData> JuniorReviewersData { get; private set; }

        /// <summary>
        /// Gets or Sets Type
        /// </summary>
        [DataMember(Name="type", EmitDefaultValue=false)]
        public string Type { get; set; }

        /// <summary>
        /// Gets or Sets TypeData
        /// </summary>
        [DataMember(Name="type_data", EmitDefaultValue=true)]
        public ProjectListTypeData TypeData { get; set; }

        /// <summary>
        /// Gets or Sets Progress
        /// </summary>
        [DataMember(Name="progress", EmitDefaultValue=false)]
        public string Progress { get; private set; }

        /// <summary>
        /// Gets or Sets UserPermissions
        /// </summary>
        [DataMember(Name="user_permissions", EmitDefaultValue=false)]
        public string UserPermissions { get; private set; }

        /// <summary>
        /// Gets or Sets TermTags
        /// </summary>
        [DataMember(Name="term_tags", EmitDefaultValue=false)]
        public List<int> TermTags { get; set; }

        /// <summary>
        /// Gets or Sets DocumentTransformer
        /// </summary>
        [DataMember(Name="document_transformer", EmitDefaultValue=true)]
        public int? DocumentTransformer { get; set; }

        /// <summary>
        /// Gets or Sets TextUnitTransformer
        /// </summary>
        [DataMember(Name="text_unit_transformer", EmitDefaultValue=true)]
        public int? TextUnitTransformer { get; set; }

        /// <summary>
        /// Gets or Sets CompanytypeTags
        /// </summary>
        [DataMember(Name="companytype_tags", EmitDefaultValue=false)]
        public List<int> CompanytypeTags { get; set; }

        /// <summary>
        /// Gets or Sets AppVars
        /// </summary>
        [DataMember(Name="app_vars", EmitDefaultValue=false)]
        public string AppVars { get; private set; }

        /// <summary>
        /// Gets or Sets DocumentSimilarityRunParams
        /// </summary>
        [DataMember(Name="document_similarity_run_params", EmitDefaultValue=false)]
        public string DocumentSimilarityRunParams { get; private set; }

        /// <summary>
        /// Gets or Sets TextUnitSimilarityRunParams
        /// </summary>
        [DataMember(Name="text_unit_similarity_run_params", EmitDefaultValue=true)]
        public string TextUnitSimilarityRunParams { get; private set; }

        /// <summary>
        /// Gets or Sets DocumentSimilarityProcessAllowed
        /// </summary>
        [DataMember(Name="document_similarity_process_allowed", EmitDefaultValue=false)]
        public string DocumentSimilarityProcessAllowed { get; private set; }

        /// <summary>
        /// Gets or Sets TextUnitSimilarityProcessAllowed
        /// </summary>
        [DataMember(Name="text_unit_similarity_process_allowed", EmitDefaultValue=false)]
        public string TextUnitSimilarityProcessAllowed { get; private set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class ProjectDetail {\n");
            sb.Append("  Pk: ").Append(Pk).Append("\n");
            sb.Append("  Name: ").Append(Name).Append("\n");
            sb.Append("  Description: ").Append(Description).Append("\n");
            sb.Append("  CreatedDate: ").Append(CreatedDate).Append("\n");
            sb.Append("  CreatedByName: ").Append(CreatedByName).Append("\n");
            sb.Append("  ModifiedDate: ").Append(ModifiedDate).Append("\n");
            sb.Append("  ModifiedByName: ").Append(ModifiedByName).Append("\n");
            sb.Append("  SendEmailNotification: ").Append(SendEmailNotification).Append("\n");
            sb.Append("  HideClauseReview: ").Append(HideClauseReview).Append("\n");
            sb.Append("  Status: ").Append(Status).Append("\n");
            sb.Append("  StatusData: ").Append(StatusData).Append("\n");
            sb.Append("  Owners: ").Append(Owners).Append("\n");
            sb.Append("  OwnersData: ").Append(OwnersData).Append("\n");
            sb.Append("  Reviewers: ").Append(Reviewers).Append("\n");
            sb.Append("  ReviewersData: ").Append(ReviewersData).Append("\n");
            sb.Append("  SuperReviewers: ").Append(SuperReviewers).Append("\n");
            sb.Append("  SuperReviewersData: ").Append(SuperReviewersData).Append("\n");
            sb.Append("  JuniorReviewers: ").Append(JuniorReviewers).Append("\n");
            sb.Append("  JuniorReviewersData: ").Append(JuniorReviewersData).Append("\n");
            sb.Append("  Type: ").Append(Type).Append("\n");
            sb.Append("  TypeData: ").Append(TypeData).Append("\n");
            sb.Append("  Progress: ").Append(Progress).Append("\n");
            sb.Append("  UserPermissions: ").Append(UserPermissions).Append("\n");
            sb.Append("  TermTags: ").Append(TermTags).Append("\n");
            sb.Append("  DocumentTransformer: ").Append(DocumentTransformer).Append("\n");
            sb.Append("  TextUnitTransformer: ").Append(TextUnitTransformer).Append("\n");
            sb.Append("  CompanytypeTags: ").Append(CompanytypeTags).Append("\n");
            sb.Append("  AppVars: ").Append(AppVars).Append("\n");
            sb.Append("  DocumentSimilarityRunParams: ").Append(DocumentSimilarityRunParams).Append("\n");
            sb.Append("  TextUnitSimilarityRunParams: ").Append(TextUnitSimilarityRunParams).Append("\n");
            sb.Append("  DocumentSimilarityProcessAllowed: ").Append(DocumentSimilarityProcessAllowed).Append("\n");
            sb.Append("  TextUnitSimilarityProcessAllowed: ").Append(TextUnitSimilarityProcessAllowed).Append("\n");
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
            return this.Equals(input as ProjectDetail);
        }

        /// <summary>
        /// Returns true if ProjectDetail instances are equal
        /// </summary>
        /// <param name="input">Instance of ProjectDetail to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(ProjectDetail input)
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
                    this.Description == input.Description ||
                    (this.Description != null &&
                    this.Description.Equals(input.Description))
                ) && 
                (
                    this.CreatedDate == input.CreatedDate ||
                    (this.CreatedDate != null &&
                    this.CreatedDate.Equals(input.CreatedDate))
                ) && 
                (
                    this.CreatedByName == input.CreatedByName ||
                    (this.CreatedByName != null &&
                    this.CreatedByName.Equals(input.CreatedByName))
                ) && 
                (
                    this.ModifiedDate == input.ModifiedDate ||
                    (this.ModifiedDate != null &&
                    this.ModifiedDate.Equals(input.ModifiedDate))
                ) && 
                (
                    this.ModifiedByName == input.ModifiedByName ||
                    (this.ModifiedByName != null &&
                    this.ModifiedByName.Equals(input.ModifiedByName))
                ) && 
                (
                    this.SendEmailNotification == input.SendEmailNotification ||
                    (this.SendEmailNotification != null &&
                    this.SendEmailNotification.Equals(input.SendEmailNotification))
                ) && 
                (
                    this.HideClauseReview == input.HideClauseReview ||
                    (this.HideClauseReview != null &&
                    this.HideClauseReview.Equals(input.HideClauseReview))
                ) && 
                (
                    this.Status == input.Status ||
                    (this.Status != null &&
                    this.Status.Equals(input.Status))
                ) && 
                (
                    this.StatusData == input.StatusData ||
                    (this.StatusData != null &&
                    this.StatusData.Equals(input.StatusData))
                ) && 
                (
                    this.Owners == input.Owners ||
                    this.Owners != null &&
                    input.Owners != null &&
                    this.Owners.SequenceEqual(input.Owners)
                ) && 
                (
                    this.OwnersData == input.OwnersData ||
                    this.OwnersData != null &&
                    input.OwnersData != null &&
                    this.OwnersData.SequenceEqual(input.OwnersData)
                ) && 
                (
                    this.Reviewers == input.Reviewers ||
                    this.Reviewers != null &&
                    input.Reviewers != null &&
                    this.Reviewers.SequenceEqual(input.Reviewers)
                ) && 
                (
                    this.ReviewersData == input.ReviewersData ||
                    this.ReviewersData != null &&
                    input.ReviewersData != null &&
                    this.ReviewersData.SequenceEqual(input.ReviewersData)
                ) && 
                (
                    this.SuperReviewers == input.SuperReviewers ||
                    this.SuperReviewers != null &&
                    input.SuperReviewers != null &&
                    this.SuperReviewers.SequenceEqual(input.SuperReviewers)
                ) && 
                (
                    this.SuperReviewersData == input.SuperReviewersData ||
                    this.SuperReviewersData != null &&
                    input.SuperReviewersData != null &&
                    this.SuperReviewersData.SequenceEqual(input.SuperReviewersData)
                ) && 
                (
                    this.JuniorReviewers == input.JuniorReviewers ||
                    this.JuniorReviewers != null &&
                    input.JuniorReviewers != null &&
                    this.JuniorReviewers.SequenceEqual(input.JuniorReviewers)
                ) && 
                (
                    this.JuniorReviewersData == input.JuniorReviewersData ||
                    this.JuniorReviewersData != null &&
                    input.JuniorReviewersData != null &&
                    this.JuniorReviewersData.SequenceEqual(input.JuniorReviewersData)
                ) && 
                (
                    this.Type == input.Type ||
                    (this.Type != null &&
                    this.Type.Equals(input.Type))
                ) && 
                (
                    this.TypeData == input.TypeData ||
                    (this.TypeData != null &&
                    this.TypeData.Equals(input.TypeData))
                ) && 
                (
                    this.Progress == input.Progress ||
                    (this.Progress != null &&
                    this.Progress.Equals(input.Progress))
                ) && 
                (
                    this.UserPermissions == input.UserPermissions ||
                    (this.UserPermissions != null &&
                    this.UserPermissions.Equals(input.UserPermissions))
                ) && 
                (
                    this.TermTags == input.TermTags ||
                    this.TermTags != null &&
                    input.TermTags != null &&
                    this.TermTags.SequenceEqual(input.TermTags)
                ) && 
                (
                    this.DocumentTransformer == input.DocumentTransformer ||
                    (this.DocumentTransformer != null &&
                    this.DocumentTransformer.Equals(input.DocumentTransformer))
                ) && 
                (
                    this.TextUnitTransformer == input.TextUnitTransformer ||
                    (this.TextUnitTransformer != null &&
                    this.TextUnitTransformer.Equals(input.TextUnitTransformer))
                ) && 
                (
                    this.CompanytypeTags == input.CompanytypeTags ||
                    this.CompanytypeTags != null &&
                    input.CompanytypeTags != null &&
                    this.CompanytypeTags.SequenceEqual(input.CompanytypeTags)
                ) && 
                (
                    this.AppVars == input.AppVars ||
                    (this.AppVars != null &&
                    this.AppVars.Equals(input.AppVars))
                ) && 
                (
                    this.DocumentSimilarityRunParams == input.DocumentSimilarityRunParams ||
                    (this.DocumentSimilarityRunParams != null &&
                    this.DocumentSimilarityRunParams.Equals(input.DocumentSimilarityRunParams))
                ) && 
                (
                    this.TextUnitSimilarityRunParams == input.TextUnitSimilarityRunParams ||
                    (this.TextUnitSimilarityRunParams != null &&
                    this.TextUnitSimilarityRunParams.Equals(input.TextUnitSimilarityRunParams))
                ) && 
                (
                    this.DocumentSimilarityProcessAllowed == input.DocumentSimilarityProcessAllowed ||
                    (this.DocumentSimilarityProcessAllowed != null &&
                    this.DocumentSimilarityProcessAllowed.Equals(input.DocumentSimilarityProcessAllowed))
                ) && 
                (
                    this.TextUnitSimilarityProcessAllowed == input.TextUnitSimilarityProcessAllowed ||
                    (this.TextUnitSimilarityProcessAllowed != null &&
                    this.TextUnitSimilarityProcessAllowed.Equals(input.TextUnitSimilarityProcessAllowed))
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
                if (this.Description != null)
                    hashCode = hashCode * 59 + this.Description.GetHashCode();
                if (this.CreatedDate != null)
                    hashCode = hashCode * 59 + this.CreatedDate.GetHashCode();
                if (this.CreatedByName != null)
                    hashCode = hashCode * 59 + this.CreatedByName.GetHashCode();
                if (this.ModifiedDate != null)
                    hashCode = hashCode * 59 + this.ModifiedDate.GetHashCode();
                if (this.ModifiedByName != null)
                    hashCode = hashCode * 59 + this.ModifiedByName.GetHashCode();
                if (this.SendEmailNotification != null)
                    hashCode = hashCode * 59 + this.SendEmailNotification.GetHashCode();
                if (this.HideClauseReview != null)
                    hashCode = hashCode * 59 + this.HideClauseReview.GetHashCode();
                if (this.Status != null)
                    hashCode = hashCode * 59 + this.Status.GetHashCode();
                if (this.StatusData != null)
                    hashCode = hashCode * 59 + this.StatusData.GetHashCode();
                if (this.Owners != null)
                    hashCode = hashCode * 59 + this.Owners.GetHashCode();
                if (this.OwnersData != null)
                    hashCode = hashCode * 59 + this.OwnersData.GetHashCode();
                if (this.Reviewers != null)
                    hashCode = hashCode * 59 + this.Reviewers.GetHashCode();
                if (this.ReviewersData != null)
                    hashCode = hashCode * 59 + this.ReviewersData.GetHashCode();
                if (this.SuperReviewers != null)
                    hashCode = hashCode * 59 + this.SuperReviewers.GetHashCode();
                if (this.SuperReviewersData != null)
                    hashCode = hashCode * 59 + this.SuperReviewersData.GetHashCode();
                if (this.JuniorReviewers != null)
                    hashCode = hashCode * 59 + this.JuniorReviewers.GetHashCode();
                if (this.JuniorReviewersData != null)
                    hashCode = hashCode * 59 + this.JuniorReviewersData.GetHashCode();
                if (this.Type != null)
                    hashCode = hashCode * 59 + this.Type.GetHashCode();
                if (this.TypeData != null)
                    hashCode = hashCode * 59 + this.TypeData.GetHashCode();
                if (this.Progress != null)
                    hashCode = hashCode * 59 + this.Progress.GetHashCode();
                if (this.UserPermissions != null)
                    hashCode = hashCode * 59 + this.UserPermissions.GetHashCode();
                if (this.TermTags != null)
                    hashCode = hashCode * 59 + this.TermTags.GetHashCode();
                if (this.DocumentTransformer != null)
                    hashCode = hashCode * 59 + this.DocumentTransformer.GetHashCode();
                if (this.TextUnitTransformer != null)
                    hashCode = hashCode * 59 + this.TextUnitTransformer.GetHashCode();
                if (this.CompanytypeTags != null)
                    hashCode = hashCode * 59 + this.CompanytypeTags.GetHashCode();
                if (this.AppVars != null)
                    hashCode = hashCode * 59 + this.AppVars.GetHashCode();
                if (this.DocumentSimilarityRunParams != null)
                    hashCode = hashCode * 59 + this.DocumentSimilarityRunParams.GetHashCode();
                if (this.TextUnitSimilarityRunParams != null)
                    hashCode = hashCode * 59 + this.TextUnitSimilarityRunParams.GetHashCode();
                if (this.DocumentSimilarityProcessAllowed != null)
                    hashCode = hashCode * 59 + this.DocumentSimilarityProcessAllowed.GetHashCode();
                if (this.TextUnitSimilarityProcessAllowed != null)
                    hashCode = hashCode * 59 + this.TextUnitSimilarityProcessAllowed.GetHashCode();
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
            if(this.Name != null && this.Name.Length > 100)
            {
                yield return new System.ComponentModel.DataAnnotations.ValidationResult("Invalid value for Name, length must be less than 100.", new [] { "Name" });
            }

 
            yield break;
        }
    }

}