/*
 * 
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 1.0.0
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

/**
 * MarkUnmarkForDeleteDocumentsRequest
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2020-12-11T16:57:55.511+03:00[Europe/Moscow]")
public class MarkUnmarkForDeleteDocumentsRequest {
  public static final String SERIALIZED_NAME_ALL = "all";
  @SerializedName(SERIALIZED_NAME_ALL)
  private Boolean all;

  public static final String SERIALIZED_NAME_PROJECT_ID = "project_id";
  @SerializedName(SERIALIZED_NAME_PROJECT_ID)
  private Integer projectId;

  public static final String SERIALIZED_NAME_DOCUMENT_IDS = "document_ids";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_IDS)
  private List<Integer> documentIds = null;


  public MarkUnmarkForDeleteDocumentsRequest all(Boolean all) {
    
    this.all = all;
    return this;
  }

   /**
   * Get all
   * @return all
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Boolean getAll() {
    return all;
  }


  public void setAll(Boolean all) {
    this.all = all;
  }


  public MarkUnmarkForDeleteDocumentsRequest projectId(Integer projectId) {
    
    this.projectId = projectId;
    return this;
  }

   /**
   * Get projectId
   * @return projectId
  **/
  @ApiModelProperty(required = true, value = "")

  public Integer getProjectId() {
    return projectId;
  }


  public void setProjectId(Integer projectId) {
    this.projectId = projectId;
  }


  public MarkUnmarkForDeleteDocumentsRequest documentIds(List<Integer> documentIds) {
    
    this.documentIds = documentIds;
    return this;
  }

  public MarkUnmarkForDeleteDocumentsRequest addDocumentIdsItem(Integer documentIdsItem) {
    if (this.documentIds == null) {
      this.documentIds = new ArrayList<Integer>();
    }
    this.documentIds.add(documentIdsItem);
    return this;
  }

   /**
   * Get documentIds
   * @return documentIds
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public List<Integer> getDocumentIds() {
    return documentIds;
  }


  public void setDocumentIds(List<Integer> documentIds) {
    this.documentIds = documentIds;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    MarkUnmarkForDeleteDocumentsRequest markUnmarkForDeleteDocumentsRequest = (MarkUnmarkForDeleteDocumentsRequest) o;
    return Objects.equals(this.all, markUnmarkForDeleteDocumentsRequest.all) &&
        Objects.equals(this.projectId, markUnmarkForDeleteDocumentsRequest.projectId) &&
        Objects.equals(this.documentIds, markUnmarkForDeleteDocumentsRequest.documentIds);
  }

  @Override
  public int hashCode() {
    return Objects.hash(all, projectId, documentIds);
  }


  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class MarkUnmarkForDeleteDocumentsRequest {\n");
    sb.append("    all: ").append(toIndentedString(all)).append("\n");
    sb.append("    projectId: ").append(toIndentedString(projectId)).append("\n");
    sb.append("    documentIds: ").append(toIndentedString(documentIds)).append("\n");
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

