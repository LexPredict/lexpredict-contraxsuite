/*
 * Contraxsuite API
 * Contraxsuite API
 *
 * The version of the OpenAPI document: 2.1.188
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
import org.openapitools.client.model.ProjectDocumentSimilarityResponseData;
import org.openapitools.jackson.nullable.JsonNullable;

/**
 * ProjectDocumentSimilarityResponse
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2022-01-19T15:46:46.101102+03:00[Europe/Moscow]")
public class ProjectDocumentSimilarityResponse {
  public static final String SERIALIZED_NAME_DATA = "data";
  @SerializedName(SERIALIZED_NAME_DATA)
  private List<ProjectDocumentSimilarityResponseData> data = new ArrayList<ProjectDocumentSimilarityResponseData>();

  public static final String SERIALIZED_NAME_DOCUMENT_A_ID = "document_a_id";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_A_ID)
  private Integer documentAId;

  public static final String SERIALIZED_NAME_DOCUMENT_A_NAME = "document_a_name";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_A_NAME)
  private String documentAName;

  public static final String SERIALIZED_NAME_TOTAL_RECORDS = "total_records";
  @SerializedName(SERIALIZED_NAME_TOTAL_RECORDS)
  private Integer totalRecords;

  public ProjectDocumentSimilarityResponse() { 
  }

  public ProjectDocumentSimilarityResponse data(List<ProjectDocumentSimilarityResponseData> data) {
    
    this.data = data;
    return this;
  }

  public ProjectDocumentSimilarityResponse addDataItem(ProjectDocumentSimilarityResponseData dataItem) {
    this.data.add(dataItem);
    return this;
  }

   /**
   * Get data
   * @return data
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public List<ProjectDocumentSimilarityResponseData> getData() {
    return data;
  }


  public void setData(List<ProjectDocumentSimilarityResponseData> data) {
    this.data = data;
  }


  public ProjectDocumentSimilarityResponse documentAId(Integer documentAId) {
    
    this.documentAId = documentAId;
    return this;
  }

   /**
   * Get documentAId
   * @return documentAId
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getDocumentAId() {
    return documentAId;
  }


  public void setDocumentAId(Integer documentAId) {
    this.documentAId = documentAId;
  }


  public ProjectDocumentSimilarityResponse documentAName(String documentAName) {
    
    this.documentAName = documentAName;
    return this;
  }

   /**
   * Get documentAName
   * @return documentAName
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getDocumentAName() {
    return documentAName;
  }


  public void setDocumentAName(String documentAName) {
    this.documentAName = documentAName;
  }


  public ProjectDocumentSimilarityResponse totalRecords(Integer totalRecords) {
    
    this.totalRecords = totalRecords;
    return this;
  }

   /**
   * Get totalRecords
   * @return totalRecords
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getTotalRecords() {
    return totalRecords;
  }


  public void setTotalRecords(Integer totalRecords) {
    this.totalRecords = totalRecords;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    ProjectDocumentSimilarityResponse projectDocumentSimilarityResponse = (ProjectDocumentSimilarityResponse) o;
    return Objects.equals(this.data, projectDocumentSimilarityResponse.data) &&
        Objects.equals(this.documentAId, projectDocumentSimilarityResponse.documentAId) &&
        Objects.equals(this.documentAName, projectDocumentSimilarityResponse.documentAName) &&
        Objects.equals(this.totalRecords, projectDocumentSimilarityResponse.totalRecords);
  }

  private static <T> boolean equalsNullable(JsonNullable<T> a, JsonNullable<T> b) {
    return a == b || (a != null && b != null && a.isPresent() && b.isPresent() && Objects.deepEquals(a.get(), b.get()));
  }

  @Override
  public int hashCode() {
    return Objects.hash(data, documentAId, documentAName, totalRecords);
  }

  private static <T> int hashCodeNullable(JsonNullable<T> a) {
    if (a == null) {
      return 1;
    }
    return a.isPresent() ? Arrays.deepHashCode(new Object[]{a.get()}) : 31;
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class ProjectDocumentSimilarityResponse {\n");
    sb.append("    data: ").append(toIndentedString(data)).append("\n");
    sb.append("    documentAId: ").append(toIndentedString(documentAId)).append("\n");
    sb.append("    documentAName: ").append(toIndentedString(documentAName)).append("\n");
    sb.append("    totalRecords: ").append(toIndentedString(totalRecords)).append("\n");
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
