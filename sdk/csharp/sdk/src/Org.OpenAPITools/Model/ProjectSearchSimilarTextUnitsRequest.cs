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
    /// ProjectSearchSimilarTextUnitsRequest
    /// </summary>
    [DataContract]
    public partial class ProjectSearchSimilarTextUnitsRequest :  IEquatable<ProjectSearchSimilarTextUnitsRequest>, IValidatableObject
    {
        /// <summary>
        /// Defines DistanceType
        /// </summary>
        [JsonConverter(typeof(StringEnumConverter))]
        public enum DistanceTypeEnum
        {
            /// <summary>
            /// Enum Braycurtis for value: braycurtis
            /// </summary>
            [EnumMember(Value = "braycurtis")]
            Braycurtis = 1,

            /// <summary>
            /// Enum Canberra for value: canberra
            /// </summary>
            [EnumMember(Value = "canberra")]
            Canberra = 2,

            /// <summary>
            /// Enum Chebyshev for value: chebyshev
            /// </summary>
            [EnumMember(Value = "chebyshev")]
            Chebyshev = 3,

            /// <summary>
            /// Enum Cityblock for value: cityblock
            /// </summary>
            [EnumMember(Value = "cityblock")]
            Cityblock = 4,

            /// <summary>
            /// Enum Correlation for value: correlation
            /// </summary>
            [EnumMember(Value = "correlation")]
            Correlation = 5,

            /// <summary>
            /// Enum Cosine for value: cosine
            /// </summary>
            [EnumMember(Value = "cosine")]
            Cosine = 6,

            /// <summary>
            /// Enum Dice for value: dice
            /// </summary>
            [EnumMember(Value = "dice")]
            Dice = 7,

            /// <summary>
            /// Enum Euclidean for value: euclidean
            /// </summary>
            [EnumMember(Value = "euclidean")]
            Euclidean = 8,

            /// <summary>
            /// Enum Hamming for value: hamming
            /// </summary>
            [EnumMember(Value = "hamming")]
            Hamming = 9,

            /// <summary>
            /// Enum Jaccard for value: jaccard
            /// </summary>
            [EnumMember(Value = "jaccard")]
            Jaccard = 10,

            /// <summary>
            /// Enum Jensenshannon for value: jensenshannon
            /// </summary>
            [EnumMember(Value = "jensenshannon")]
            Jensenshannon = 11,

            /// <summary>
            /// Enum Kulsinski for value: kulsinski
            /// </summary>
            [EnumMember(Value = "kulsinski")]
            Kulsinski = 12,

            /// <summary>
            /// Enum Mahalanobis for value: mahalanobis
            /// </summary>
            [EnumMember(Value = "mahalanobis")]
            Mahalanobis = 13,

            /// <summary>
            /// Enum Minkowski for value: minkowski
            /// </summary>
            [EnumMember(Value = "minkowski")]
            Minkowski = 14,

            /// <summary>
            /// Enum Rogerstanimoto for value: rogerstanimoto
            /// </summary>
            [EnumMember(Value = "rogerstanimoto")]
            Rogerstanimoto = 15,

            /// <summary>
            /// Enum Russellrao for value: russellrao
            /// </summary>
            [EnumMember(Value = "russellrao")]
            Russellrao = 16,

            /// <summary>
            /// Enum Seuclidean for value: seuclidean
            /// </summary>
            [EnumMember(Value = "seuclidean")]
            Seuclidean = 17,

            /// <summary>
            /// Enum Sokalmichener for value: sokalmichener
            /// </summary>
            [EnumMember(Value = "sokalmichener")]
            Sokalmichener = 18,

            /// <summary>
            /// Enum Sokalsneath for value: sokalsneath
            /// </summary>
            [EnumMember(Value = "sokalsneath")]
            Sokalsneath = 19,

            /// <summary>
            /// Enum Sqeuclidean for value: sqeuclidean
            /// </summary>
            [EnumMember(Value = "sqeuclidean")]
            Sqeuclidean = 20,

            /// <summary>
            /// Enum Wminkowski for value: wminkowski
            /// </summary>
            [EnumMember(Value = "wminkowski")]
            Wminkowski = 21,

            /// <summary>
            /// Enum Yule for value: yule
            /// </summary>
            [EnumMember(Value = "yule")]
            Yule = 22

        }

        /// <summary>
        /// Gets or Sets DistanceType
        /// </summary>
        [DataMember(Name="distance_type", EmitDefaultValue=false)]
        public DistanceTypeEnum? DistanceType { get; set; }
        /// <summary>
        /// Defines UnitType
        /// </summary>
        [JsonConverter(typeof(StringEnumConverter))]
        public enum UnitTypeEnum
        {
            /// <summary>
            /// Enum Sentence for value: sentence
            /// </summary>
            [EnumMember(Value = "sentence")]
            Sentence = 1,

            /// <summary>
            /// Enum Paragraph for value: paragraph
            /// </summary>
            [EnumMember(Value = "paragraph")]
            Paragraph = 2

        }

        /// <summary>
        /// Gets or Sets UnitType
        /// </summary>
        [DataMember(Name="unit_type", EmitDefaultValue=false)]
        public UnitTypeEnum? UnitType { get; set; }
        /// <summary>
        /// Initializes a new instance of the <see cref="ProjectSearchSimilarTextUnitsRequest" /> class.
        /// </summary>
        /// <param name="runName">runName.</param>
        /// <param name="distanceType">distanceType (default to DistanceTypeEnum.Cosine).</param>
        /// <param name="similarityThreshold">similarityThreshold (default to 75).</param>
        /// <param name="createReverseRelations">createReverseRelations (default to true).</param>
        /// <param name="useTfidf">useTfidf (default to false).</param>
        /// <param name="delete">delete (default to true).</param>
        /// <param name="itemId">itemId.</param>
        /// <param name="unitType">unitType (default to UnitTypeEnum.Sentence).</param>
        /// <param name="documentId">documentId.</param>
        /// <param name="locationStart">locationStart.</param>
        /// <param name="locationEnd">locationEnd.</param>
        public ProjectSearchSimilarTextUnitsRequest(string runName = default(string), DistanceTypeEnum? distanceType = DistanceTypeEnum.Cosine, int similarityThreshold = 75, bool createReverseRelations = true, bool useTfidf = false, bool delete = true, int itemId = default(int), UnitTypeEnum? unitType = UnitTypeEnum.Sentence, int documentId = default(int), int locationStart = default(int), int locationEnd = default(int))
        {
            this.RunName = runName;
            // use default value if no "distanceType" provided
            if (distanceType == null)
            {
                this.DistanceType = DistanceTypeEnum.Cosine;
            }
            else
            {
                this.DistanceType = distanceType;
            }
            // use default value if no "similarityThreshold" provided
            if (similarityThreshold == null)
            {
                this.SimilarityThreshold = 75;
            }
            else
            {
                this.SimilarityThreshold = similarityThreshold;
            }
            // use default value if no "createReverseRelations" provided
            if (createReverseRelations == null)
            {
                this.CreateReverseRelations = true;
            }
            else
            {
                this.CreateReverseRelations = createReverseRelations;
            }
            // use default value if no "useTfidf" provided
            if (useTfidf == null)
            {
                this.UseTfidf = false;
            }
            else
            {
                this.UseTfidf = useTfidf;
            }
            // use default value if no "delete" provided
            if (delete == null)
            {
                this.Delete = true;
            }
            else
            {
                this.Delete = delete;
            }
            this.ItemId = itemId;
            // use default value if no "unitType" provided
            if (unitType == null)
            {
                this.UnitType = UnitTypeEnum.Sentence;
            }
            else
            {
                this.UnitType = unitType;
            }
            this.DocumentId = documentId;
            this.LocationStart = locationStart;
            this.LocationEnd = locationEnd;
        }

        /// <summary>
        /// Gets or Sets RunName
        /// </summary>
        [DataMember(Name="run_name", EmitDefaultValue=false)]
        public string RunName { get; set; }


        /// <summary>
        /// Gets or Sets SimilarityThreshold
        /// </summary>
        [DataMember(Name="similarity_threshold", EmitDefaultValue=false)]
        public int SimilarityThreshold { get; set; }

        /// <summary>
        /// Gets or Sets CreateReverseRelations
        /// </summary>
        [DataMember(Name="create_reverse_relations", EmitDefaultValue=false)]
        public bool CreateReverseRelations { get; set; }

        /// <summary>
        /// Gets or Sets UseTfidf
        /// </summary>
        [DataMember(Name="use_tfidf", EmitDefaultValue=false)]
        public bool UseTfidf { get; set; }

        /// <summary>
        /// Gets or Sets Delete
        /// </summary>
        [DataMember(Name="delete", EmitDefaultValue=false)]
        public bool Delete { get; set; }

        /// <summary>
        /// Gets or Sets ItemId
        /// </summary>
        [DataMember(Name="item_id", EmitDefaultValue=false)]
        public int ItemId { get; set; }


        /// <summary>
        /// Gets or Sets DocumentId
        /// </summary>
        [DataMember(Name="document_id", EmitDefaultValue=false)]
        public int DocumentId { get; set; }

        /// <summary>
        /// Gets or Sets LocationStart
        /// </summary>
        [DataMember(Name="location_start", EmitDefaultValue=false)]
        public int LocationStart { get; set; }

        /// <summary>
        /// Gets or Sets LocationEnd
        /// </summary>
        [DataMember(Name="location_end", EmitDefaultValue=false)]
        public int LocationEnd { get; set; }

        /// <summary>
        /// Returns the string presentation of the object
        /// </summary>
        /// <returns>String presentation of the object</returns>
        public override string ToString()
        {
            var sb = new StringBuilder();
            sb.Append("class ProjectSearchSimilarTextUnitsRequest {\n");
            sb.Append("  RunName: ").Append(RunName).Append("\n");
            sb.Append("  DistanceType: ").Append(DistanceType).Append("\n");
            sb.Append("  SimilarityThreshold: ").Append(SimilarityThreshold).Append("\n");
            sb.Append("  CreateReverseRelations: ").Append(CreateReverseRelations).Append("\n");
            sb.Append("  UseTfidf: ").Append(UseTfidf).Append("\n");
            sb.Append("  Delete: ").Append(Delete).Append("\n");
            sb.Append("  ItemId: ").Append(ItemId).Append("\n");
            sb.Append("  UnitType: ").Append(UnitType).Append("\n");
            sb.Append("  DocumentId: ").Append(DocumentId).Append("\n");
            sb.Append("  LocationStart: ").Append(LocationStart).Append("\n");
            sb.Append("  LocationEnd: ").Append(LocationEnd).Append("\n");
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
            return this.Equals(input as ProjectSearchSimilarTextUnitsRequest);
        }

        /// <summary>
        /// Returns true if ProjectSearchSimilarTextUnitsRequest instances are equal
        /// </summary>
        /// <param name="input">Instance of ProjectSearchSimilarTextUnitsRequest to be compared</param>
        /// <returns>Boolean</returns>
        public bool Equals(ProjectSearchSimilarTextUnitsRequest input)
        {
            if (input == null)
                return false;

            return 
                (
                    this.RunName == input.RunName ||
                    (this.RunName != null &&
                    this.RunName.Equals(input.RunName))
                ) && 
                (
                    this.DistanceType == input.DistanceType ||
                    (this.DistanceType != null &&
                    this.DistanceType.Equals(input.DistanceType))
                ) && 
                (
                    this.SimilarityThreshold == input.SimilarityThreshold ||
                    (this.SimilarityThreshold != null &&
                    this.SimilarityThreshold.Equals(input.SimilarityThreshold))
                ) && 
                (
                    this.CreateReverseRelations == input.CreateReverseRelations ||
                    (this.CreateReverseRelations != null &&
                    this.CreateReverseRelations.Equals(input.CreateReverseRelations))
                ) && 
                (
                    this.UseTfidf == input.UseTfidf ||
                    (this.UseTfidf != null &&
                    this.UseTfidf.Equals(input.UseTfidf))
                ) && 
                (
                    this.Delete == input.Delete ||
                    (this.Delete != null &&
                    this.Delete.Equals(input.Delete))
                ) && 
                (
                    this.ItemId == input.ItemId ||
                    (this.ItemId != null &&
                    this.ItemId.Equals(input.ItemId))
                ) && 
                (
                    this.UnitType == input.UnitType ||
                    (this.UnitType != null &&
                    this.UnitType.Equals(input.UnitType))
                ) && 
                (
                    this.DocumentId == input.DocumentId ||
                    (this.DocumentId != null &&
                    this.DocumentId.Equals(input.DocumentId))
                ) && 
                (
                    this.LocationStart == input.LocationStart ||
                    (this.LocationStart != null &&
                    this.LocationStart.Equals(input.LocationStart))
                ) && 
                (
                    this.LocationEnd == input.LocationEnd ||
                    (this.LocationEnd != null &&
                    this.LocationEnd.Equals(input.LocationEnd))
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
                if (this.RunName != null)
                    hashCode = hashCode * 59 + this.RunName.GetHashCode();
                if (this.DistanceType != null)
                    hashCode = hashCode * 59 + this.DistanceType.GetHashCode();
                if (this.SimilarityThreshold != null)
                    hashCode = hashCode * 59 + this.SimilarityThreshold.GetHashCode();
                if (this.CreateReverseRelations != null)
                    hashCode = hashCode * 59 + this.CreateReverseRelations.GetHashCode();
                if (this.UseTfidf != null)
                    hashCode = hashCode * 59 + this.UseTfidf.GetHashCode();
                if (this.Delete != null)
                    hashCode = hashCode * 59 + this.Delete.GetHashCode();
                if (this.ItemId != null)
                    hashCode = hashCode * 59 + this.ItemId.GetHashCode();
                if (this.UnitType != null)
                    hashCode = hashCode * 59 + this.UnitType.GetHashCode();
                if (this.DocumentId != null)
                    hashCode = hashCode * 59 + this.DocumentId.GetHashCode();
                if (this.LocationStart != null)
                    hashCode = hashCode * 59 + this.LocationStart.GetHashCode();
                if (this.LocationEnd != null)
                    hashCode = hashCode * 59 + this.LocationEnd.GetHashCode();
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
