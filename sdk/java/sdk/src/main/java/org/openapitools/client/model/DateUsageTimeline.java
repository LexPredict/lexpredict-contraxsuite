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

/**
 * DateUsageTimeline
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2022-01-19T15:46:46.101102+03:00[Europe/Moscow]")
public class DateUsageTimeline {
  public static final String SERIALIZED_NAME_DOCUMENT_ID = "document_id";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_ID)
  private Integer documentId;

  public static final String SERIALIZED_NAME_PER_MONTH = "per_month";
  @SerializedName(SERIALIZED_NAME_PER_MONTH)
  private Boolean perMonth = false;

  public DateUsageTimeline() { 
  }

  public DateUsageTimeline documentId(Integer documentId) {
    
    this.documentId = documentId;
    return this;
  }

   /**
   * Get documentId
   * @return documentId
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getDocumentId() {
    return documentId;
  }


  public void setDocumentId(Integer documentId) {
    this.documentId = documentId;
  }


  public DateUsageTimeline perMonth(Boolean perMonth) {
    
    this.perMonth = perMonth;
    return this;
  }

   /**
   * Get perMonth
   * @return perMonth
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Boolean getPerMonth() {
    return perMonth;
  }


  public void setPerMonth(Boolean perMonth) {
    this.perMonth = perMonth;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    DateUsageTimeline dateUsageTimeline = (DateUsageTimeline) o;
    return Objects.equals(this.documentId, dateUsageTimeline.documentId) &&
        Objects.equals(this.perMonth, dateUsageTimeline.perMonth);
  }

  @Override
  public int hashCode() {
    return Objects.hash(documentId, perMonth);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class DateUsageTimeline {\n");
    sb.append("    documentId: ").append(toIndentedString(documentId)).append("\n");
    sb.append("    perMonth: ").append(toIndentedString(perMonth)).append("\n");
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

