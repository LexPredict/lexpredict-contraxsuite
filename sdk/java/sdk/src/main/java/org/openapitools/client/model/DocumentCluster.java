/*
 * Contraxsuite API
 * Contraxsuite API
 *
 * The version of the OpenAPI document: 2.0.0
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
import org.openapitools.client.model.DocumentClusterDocumentData;
import org.threeten.bp.OffsetDateTime;

/**
 * DocumentCluster
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-05-07T11:20:07.445799+03:00[Europe/Moscow]")
public class DocumentCluster {
  public static final String SERIALIZED_NAME_PK = "pk";
  @SerializedName(SERIALIZED_NAME_PK)
  private Integer pk;

  public static final String SERIALIZED_NAME_CLUSTER_ID = "cluster_id";
  @SerializedName(SERIALIZED_NAME_CLUSTER_ID)
  private Integer clusterId;

  public static final String SERIALIZED_NAME_NAME = "name";
  @SerializedName(SERIALIZED_NAME_NAME)
  private String name;

  public static final String SERIALIZED_NAME_SELF_NAME = "self_name";
  @SerializedName(SERIALIZED_NAME_SELF_NAME)
  private String selfName;

  public static final String SERIALIZED_NAME_DESCRIPTION = "description";
  @SerializedName(SERIALIZED_NAME_DESCRIPTION)
  private String description;

  public static final String SERIALIZED_NAME_CLUSTER_BY = "cluster_by";
  @SerializedName(SERIALIZED_NAME_CLUSTER_BY)
  private String clusterBy;

  public static final String SERIALIZED_NAME_USING = "using";
  @SerializedName(SERIALIZED_NAME_USING)
  private String using;

  public static final String SERIALIZED_NAME_CREATED_DATE = "created_date";
  @SerializedName(SERIALIZED_NAME_CREATED_DATE)
  private OffsetDateTime createdDate;

  public static final String SERIALIZED_NAME_DOCUMENTS_COUNT = "documents_count";
  @SerializedName(SERIALIZED_NAME_DOCUMENTS_COUNT)
  private Integer documentsCount;

  public static final String SERIALIZED_NAME_DOCUMENT_DATA = "document_data";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_DATA)
  private List<DocumentClusterDocumentData> documentData = null;


   /**
   * Get pk
   * @return pk
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getPk() {
    return pk;
  }




  public DocumentCluster clusterId(Integer clusterId) {
    
    this.clusterId = clusterId;
    return this;
  }

   /**
   * Get clusterId
   * minimum: -2147483648
   * maximum: 2147483647
   * @return clusterId
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getClusterId() {
    return clusterId;
  }


  public void setClusterId(Integer clusterId) {
    this.clusterId = clusterId;
  }


  public DocumentCluster name(String name) {
    
    this.name = name;
    return this;
  }

   /**
   * Get name
   * @return name
  **/
  @ApiModelProperty(required = true, value = "")

  public String getName() {
    return name;
  }


  public void setName(String name) {
    this.name = name;
  }


  public DocumentCluster selfName(String selfName) {
    
    this.selfName = selfName;
    return this;
  }

   /**
   * Get selfName
   * @return selfName
  **/
  @ApiModelProperty(required = true, value = "")

  public String getSelfName() {
    return selfName;
  }


  public void setSelfName(String selfName) {
    this.selfName = selfName;
  }


  public DocumentCluster description(String description) {
    
    this.description = description;
    return this;
  }

   /**
   * Get description
   * @return description
  **/
  @ApiModelProperty(required = true, value = "")

  public String getDescription() {
    return description;
  }


  public void setDescription(String description) {
    this.description = description;
  }


  public DocumentCluster clusterBy(String clusterBy) {
    
    this.clusterBy = clusterBy;
    return this;
  }

   /**
   * Get clusterBy
   * @return clusterBy
  **/
  @ApiModelProperty(required = true, value = "")

  public String getClusterBy() {
    return clusterBy;
  }


  public void setClusterBy(String clusterBy) {
    this.clusterBy = clusterBy;
  }


  public DocumentCluster using(String using) {
    
    this.using = using;
    return this;
  }

   /**
   * Get using
   * @return using
  **/
  @ApiModelProperty(required = true, value = "")

  public String getUsing() {
    return using;
  }


  public void setUsing(String using) {
    this.using = using;
  }


  public DocumentCluster createdDate(OffsetDateTime createdDate) {
    
    this.createdDate = createdDate;
    return this;
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


  public void setCreatedDate(OffsetDateTime createdDate) {
    this.createdDate = createdDate;
  }


   /**
   * Get documentsCount
   * @return documentsCount
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getDocumentsCount() {
    return documentsCount;
  }




   /**
   * Get documentData
   * @return documentData
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public List<DocumentClusterDocumentData> getDocumentData() {
    return documentData;
  }




  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    DocumentCluster documentCluster = (DocumentCluster) o;
    return Objects.equals(this.pk, documentCluster.pk) &&
        Objects.equals(this.clusterId, documentCluster.clusterId) &&
        Objects.equals(this.name, documentCluster.name) &&
        Objects.equals(this.selfName, documentCluster.selfName) &&
        Objects.equals(this.description, documentCluster.description) &&
        Objects.equals(this.clusterBy, documentCluster.clusterBy) &&
        Objects.equals(this.using, documentCluster.using) &&
        Objects.equals(this.createdDate, documentCluster.createdDate) &&
        Objects.equals(this.documentsCount, documentCluster.documentsCount) &&
        Objects.equals(this.documentData, documentCluster.documentData);
  }

  @Override
  public int hashCode() {
    return Objects.hash(pk, clusterId, name, selfName, description, clusterBy, using, createdDate, documentsCount, documentData);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class DocumentCluster {\n");
    sb.append("    pk: ").append(toIndentedString(pk)).append("\n");
    sb.append("    clusterId: ").append(toIndentedString(clusterId)).append("\n");
    sb.append("    name: ").append(toIndentedString(name)).append("\n");
    sb.append("    selfName: ").append(toIndentedString(selfName)).append("\n");
    sb.append("    description: ").append(toIndentedString(description)).append("\n");
    sb.append("    clusterBy: ").append(toIndentedString(clusterBy)).append("\n");
    sb.append("    using: ").append(toIndentedString(using)).append("\n");
    sb.append("    createdDate: ").append(toIndentedString(createdDate)).append("\n");
    sb.append("    documentsCount: ").append(toIndentedString(documentsCount)).append("\n");
    sb.append("    documentData: ").append(toIndentedString(documentData)).append("\n");
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
