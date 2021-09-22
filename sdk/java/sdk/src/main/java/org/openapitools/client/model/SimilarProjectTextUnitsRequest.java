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

/**
 * SimilarProjectTextUnitsRequest
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-09-21T17:23:12.379447+03:00[Europe/Moscow]")
public class SimilarProjectTextUnitsRequest {
  public static final String SERIALIZED_NAME_TEXT_MAX_LENGTH = "text_max_length";
  @SerializedName(SERIALIZED_NAME_TEXT_MAX_LENGTH)
  private Integer textMaxLength;

  public static final String SERIALIZED_NAME_RUN_ID = "run_id";
  @SerializedName(SERIALIZED_NAME_RUN_ID)
  private Integer runId;

  public static final String SERIALIZED_NAME_LAST_RUN = "last_run";
  @SerializedName(SERIALIZED_NAME_LAST_RUN)
  private Boolean lastRun;

  public static final String SERIALIZED_NAME_TEXT_UNIT_ID = "text_unit_id";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_ID)
  private Integer textUnitId;

  public static final String SERIALIZED_NAME_DOCUMENT_ID = "document_id";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_ID)
  private Integer documentId;

  public static final String SERIALIZED_NAME_LOCATION_START = "location_start";
  @SerializedName(SERIALIZED_NAME_LOCATION_START)
  private Integer locationStart;

  public static final String SERIALIZED_NAME_LOCATION_END = "location_end";
  @SerializedName(SERIALIZED_NAME_LOCATION_END)
  private Integer locationEnd;

  public static final String SERIALIZED_NAME_SELECTION = "selection";
  @SerializedName(SERIALIZED_NAME_SELECTION)
  private List<Object> selection = null;


  public SimilarProjectTextUnitsRequest textMaxLength(Integer textMaxLength) {
    
    this.textMaxLength = textMaxLength;
    return this;
  }

   /**
   * text unit b text max length, 0 to get all text
   * @return textMaxLength
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "text unit b text max length, 0 to get all text")

  public Integer getTextMaxLength() {
    return textMaxLength;
  }


  public void setTextMaxLength(Integer textMaxLength) {
    this.textMaxLength = textMaxLength;
  }


  public SimilarProjectTextUnitsRequest runId(Integer runId) {
    
    this.runId = runId;
    return this;
  }

   /**
   * run id or text unit id required
   * @return runId
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "run id or text unit id required")

  public Integer getRunId() {
    return runId;
  }


  public void setRunId(Integer runId) {
    this.runId = runId;
  }


  public SimilarProjectTextUnitsRequest lastRun(Boolean lastRun) {
    
    this.lastRun = lastRun;
    return this;
  }

   /**
   * run id or last_run or text unit id required
   * @return lastRun
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "run id or last_run or text unit id required")

  public Boolean getLastRun() {
    return lastRun;
  }


  public void setLastRun(Boolean lastRun) {
    this.lastRun = lastRun;
  }


  public SimilarProjectTextUnitsRequest textUnitId(Integer textUnitId) {
    
    this.textUnitId = textUnitId;
    return this;
  }

   /**
   * run id or text unit id required
   * @return textUnitId
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "run id or text unit id required")

  public Integer getTextUnitId() {
    return textUnitId;
  }


  public void setTextUnitId(Integer textUnitId) {
    this.textUnitId = textUnitId;
  }


  public SimilarProjectTextUnitsRequest documentId(Integer documentId) {
    
    this.documentId = documentId;
    return this;
  }

   /**
   * document ID
   * @return documentId
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "document ID")

  public Integer getDocumentId() {
    return documentId;
  }


  public void setDocumentId(Integer documentId) {
    this.documentId = documentId;
  }


  public SimilarProjectTextUnitsRequest locationStart(Integer locationStart) {
    
    this.locationStart = locationStart;
    return this;
  }

   /**
   * start of chosen text block in a Document
   * @return locationStart
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "start of chosen text block in a Document")

  public Integer getLocationStart() {
    return locationStart;
  }


  public void setLocationStart(Integer locationStart) {
    this.locationStart = locationStart;
  }


  public SimilarProjectTextUnitsRequest locationEnd(Integer locationEnd) {
    
    this.locationEnd = locationEnd;
    return this;
  }

   /**
   * end of chosen text block in a Document
   * @return locationEnd
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "end of chosen text block in a Document")

  public Integer getLocationEnd() {
    return locationEnd;
  }


  public void setLocationEnd(Integer locationEnd) {
    this.locationEnd = locationEnd;
  }


  public SimilarProjectTextUnitsRequest selection(List<Object> selection) {
    
    this.selection = selection;
    return this;
  }

  public SimilarProjectTextUnitsRequest addSelectionItem(Object selectionItem) {
    if (this.selection == null) {
      this.selection = new ArrayList<Object>();
    }
    this.selection.add(selectionItem);
    return this;
  }

   /**
   * selection coordinates
   * @return selection
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "selection coordinates")

  public List<Object> getSelection() {
    return selection;
  }


  public void setSelection(List<Object> selection) {
    this.selection = selection;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    SimilarProjectTextUnitsRequest similarProjectTextUnitsRequest = (SimilarProjectTextUnitsRequest) o;
    return Objects.equals(this.textMaxLength, similarProjectTextUnitsRequest.textMaxLength) &&
        Objects.equals(this.runId, similarProjectTextUnitsRequest.runId) &&
        Objects.equals(this.lastRun, similarProjectTextUnitsRequest.lastRun) &&
        Objects.equals(this.textUnitId, similarProjectTextUnitsRequest.textUnitId) &&
        Objects.equals(this.documentId, similarProjectTextUnitsRequest.documentId) &&
        Objects.equals(this.locationStart, similarProjectTextUnitsRequest.locationStart) &&
        Objects.equals(this.locationEnd, similarProjectTextUnitsRequest.locationEnd) &&
        Objects.equals(this.selection, similarProjectTextUnitsRequest.selection);
  }

  @Override
  public int hashCode() {
    return Objects.hash(textMaxLength, runId, lastRun, textUnitId, documentId, locationStart, locationEnd, selection);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class SimilarProjectTextUnitsRequest {\n");
    sb.append("    textMaxLength: ").append(toIndentedString(textMaxLength)).append("\n");
    sb.append("    runId: ").append(toIndentedString(runId)).append("\n");
    sb.append("    lastRun: ").append(toIndentedString(lastRun)).append("\n");
    sb.append("    textUnitId: ").append(toIndentedString(textUnitId)).append("\n");
    sb.append("    documentId: ").append(toIndentedString(documentId)).append("\n");
    sb.append("    locationStart: ").append(toIndentedString(locationStart)).append("\n");
    sb.append("    locationEnd: ").append(toIndentedString(locationEnd)).append("\n");
    sb.append("    selection: ").append(toIndentedString(selection)).append("\n");
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

