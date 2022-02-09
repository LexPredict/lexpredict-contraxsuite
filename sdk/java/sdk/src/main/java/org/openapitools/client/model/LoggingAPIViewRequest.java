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

/**
 * LoggingAPIViewRequest
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2022-01-19T15:46:46.101102+03:00[Europe/Moscow]")
public class LoggingAPIViewRequest {
  public static final String SERIALIZED_NAME_QUERY_INFO = "queryInfo";
  @SerializedName(SERIALIZED_NAME_QUERY_INFO)
  private Object queryInfo;

  public static final String SERIALIZED_NAME_RECORDS = "records";
  @SerializedName(SERIALIZED_NAME_RECORDS)
  private List<Object> records = new ArrayList<Object>();

  public LoggingAPIViewRequest() { 
  }

  public LoggingAPIViewRequest queryInfo(Object queryInfo) {
    
    this.queryInfo = queryInfo;
    return this;
  }

   /**
   * Get queryInfo
   * @return queryInfo
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Object getQueryInfo() {
    return queryInfo;
  }


  public void setQueryInfo(Object queryInfo) {
    this.queryInfo = queryInfo;
  }


  public LoggingAPIViewRequest records(List<Object> records) {
    
    this.records = records;
    return this;
  }

  public LoggingAPIViewRequest addRecordsItem(Object recordsItem) {
    this.records.add(recordsItem);
    return this;
  }

   /**
   * Get records
   * @return records
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public List<Object> getRecords() {
    return records;
  }


  public void setRecords(List<Object> records) {
    this.records = records;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    LoggingAPIViewRequest loggingAPIViewRequest = (LoggingAPIViewRequest) o;
    return Objects.equals(this.queryInfo, loggingAPIViewRequest.queryInfo) &&
        Objects.equals(this.records, loggingAPIViewRequest.records);
  }

  @Override
  public int hashCode() {
    return Objects.hash(queryInfo, records);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class LoggingAPIViewRequest {\n");
    sb.append("    queryInfo: ").append(toIndentedString(queryInfo)).append("\n");
    sb.append("    records: ").append(toIndentedString(records)).append("\n");
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

