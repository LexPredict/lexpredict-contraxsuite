/*
 * Contraxsuite API
 * Contraxsuite API
 *
 * The version of the OpenAPI document: 2.1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


package org.openapitools.client.model;

import java.util.Objects;
import java.util.Arrays;
import com.google.gson.TypeAdapter;
import com.google.gson.annotations.JsonAdapter;
import com.google.gson.annotations.SerializedName;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonWriter;
import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.openapitools.client.model.ProjectClusteringDocumentClusters;
import org.openapitools.jackson.nullable.JsonNullable;
import org.threeten.bp.OffsetDateTime;

/**
 * ProjectClustering
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-09-21T17:23:12.379447+03:00[Europe/Moscow]")
public class ProjectClustering {
  public static final String SERIALIZED_NAME_PK = "pk";
  @SerializedName(SERIALIZED_NAME_PK)
  private Integer pk;

  public static final String SERIALIZED_NAME_DOCUMENT_CLUSTERS = "document_clusters";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_CLUSTERS)
  private List<ProjectClusteringDocumentClusters> documentClusters = null;

  public static final String SERIALIZED_NAME_METADATA = "metadata";
  @SerializedName(SERIALIZED_NAME_METADATA)
  private Object metadata;

  public static final String SERIALIZED_NAME_CREATED_DATE = "created_date";
  @SerializedName(SERIALIZED_NAME_CREATED_DATE)
  private OffsetDateTime createdDate;

  public static final String SERIALIZED_NAME_STATUS = "status";
  @SerializedName(SERIALIZED_NAME_STATUS)
  private String status;

  public static final String SERIALIZED_NAME_REASON = "reason";
  @SerializedName(SERIALIZED_NAME_REASON)
  private String reason;

  public static final String SERIALIZED_NAME_PROJECT_CLUSTERS_DOCUMENTS_COUNT = "project_clusters_documents_count";
  @SerializedName(SERIALIZED_NAME_PROJECT_CLUSTERS_DOCUMENTS_COUNT)
  private Integer projectClustersDocumentsCount;

  public static final String SERIALIZED_NAME_PROJECT_CLUSTERS_ACTIONS_COUNT = "project_clusters_actions_count";
  @SerializedName(SERIALIZED_NAME_PROJECT_CLUSTERS_ACTIONS_COUNT)
  private Integer projectClustersActionsCount;


   /**
   * Get pk
   * @return pk
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getPk() {
    return pk;
  }




   /**
   * Get documentClusters
   * @return documentClusters
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public List<ProjectClusteringDocumentClusters> getDocumentClusters() {
    return documentClusters;
  }




  public ProjectClustering metadata(Object metadata) {
    
    this.metadata = metadata;
    return this;
  }

   /**
   * Get metadata
   * @return metadata
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Object getMetadata() {
    return metadata;
  }


  public void setMetadata(Object metadata) {
    this.metadata = metadata;
  }


   /**
   * Get createdDate
   * @return createdDate
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public OffsetDateTime getCreatedDate() {
    return createdDate;
  }




   /**
   * Get status
   * @return status
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getStatus() {
    return status;
  }




  public ProjectClustering reason(String reason) {
    
    this.reason = reason;
    return this;
  }

   /**
   * Get reason
   * @return reason
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getReason() {
    return reason;
  }


  public void setReason(String reason) {
    this.reason = reason;
  }


  public ProjectClustering projectClustersDocumentsCount(Integer projectClustersDocumentsCount) {
    
    this.projectClustersDocumentsCount = projectClustersDocumentsCount;
    return this;
  }

   /**
   * Get projectClustersDocumentsCount
   * @return projectClustersDocumentsCount
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getProjectClustersDocumentsCount() {
    return projectClustersDocumentsCount;
  }


  public void setProjectClustersDocumentsCount(Integer projectClustersDocumentsCount) {
    this.projectClustersDocumentsCount = projectClustersDocumentsCount;
  }


   /**
   * Get projectClustersActionsCount
   * @return projectClustersActionsCount
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getProjectClustersActionsCount() {
    return projectClustersActionsCount;
  }




  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    ProjectClustering projectClustering = (ProjectClustering) o;
    return Objects.equals(this.pk, projectClustering.pk) &&
        Objects.equals(this.documentClusters, projectClustering.documentClusters) &&
        Objects.equals(this.metadata, projectClustering.metadata) &&
        Objects.equals(this.createdDate, projectClustering.createdDate) &&
        Objects.equals(this.status, projectClustering.status) &&
        Objects.equals(this.reason, projectClustering.reason) &&
        Objects.equals(this.projectClustersDocumentsCount, projectClustering.projectClustersDocumentsCount) &&
        Objects.equals(this.projectClustersActionsCount, projectClustering.projectClustersActionsCount);
  }

  private static <T> boolean equalsNullable(JsonNullable<T> a, JsonNullable<T> b) {
    return a == b || (a != null && b != null && a.isPresent() && b.isPresent() && a.get().getClass().isArray() ? Arrays.equals((T[])a.get(), (T[])b.get()) : Objects.equals(a.get(), b.get()));
  }

  @Override
  public int hashCode() {
    return Objects.hash(pk, documentClusters, metadata, createdDate, status, reason, projectClustersDocumentsCount, projectClustersActionsCount);
  }

  private static <T> int hashCodeNullable(JsonNullable<T> a) {
    if (a == null) {
      return 1;
    }
    return a.isPresent()
      ? (a.get().getClass().isArray() ? Arrays.hashCode((T[])a.get()) : Objects.hashCode(a.get()))
      : 31;
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class ProjectClustering {\n");
    sb.append("    pk: ").append(toIndentedString(pk)).append("\n");
    sb.append("    documentClusters: ").append(toIndentedString(documentClusters)).append("\n");
    sb.append("    metadata: ").append(toIndentedString(metadata)).append("\n");
    sb.append("    createdDate: ").append(toIndentedString(createdDate)).append("\n");
    sb.append("    status: ").append(toIndentedString(status)).append("\n");
    sb.append("    reason: ").append(toIndentedString(reason)).append("\n");
    sb.append("    projectClustersDocumentsCount: ").append(toIndentedString(projectClustersDocumentsCount)).append("\n");
    sb.append("    projectClustersActionsCount: ").append(toIndentedString(projectClustersActionsCount)).append("\n");
    sb.append("}");
    return sb.toString();
  }

  /**
   * Convert the given object to string with each line indented by 4 spaces
   * (except the first line).
   */
  private String toIndentedString(Object o) {
    if (o == null) {
      return "null";
    }
    return o.toString().replace("\n", "\n    ");
  }

}

