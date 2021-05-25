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
import org.threeten.bp.OffsetDateTime;

/**
 * AnnotationUpdateResponse
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-05-07T11:20:07.445799+03:00[Europe/Moscow]")
public class AnnotationUpdateResponse {
  public static final String SERIALIZED_NAME_PK = "pk";
  @SerializedName(SERIALIZED_NAME_PK)
  private Integer pk;

  public static final String SERIALIZED_NAME_DOCUMENT = "document";
  @SerializedName(SERIALIZED_NAME_DOCUMENT)
  private Integer document;

  public static final String SERIALIZED_NAME_DOCUMENT_NAME = "document_name";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_NAME)
  private String documentName;

  public static final String SERIALIZED_NAME_FIELD = "field";
  @SerializedName(SERIALIZED_NAME_FIELD)
  private String field;

  public static final String SERIALIZED_NAME_FIELD_NAME = "field_name";
  @SerializedName(SERIALIZED_NAME_FIELD_NAME)
  private String fieldName;

  public static final String SERIALIZED_NAME_VALUE = "value";
  @SerializedName(SERIALIZED_NAME_VALUE)
  private Object value;

  public static final String SERIALIZED_NAME_PROJECT = "project";
  @SerializedName(SERIALIZED_NAME_PROJECT)
  private String project;

  public static final String SERIALIZED_NAME_LOCATION_START = "location_start";
  @SerializedName(SERIALIZED_NAME_LOCATION_START)
  private Integer locationStart;

  public static final String SERIALIZED_NAME_LOCATION_END = "location_end";
  @SerializedName(SERIALIZED_NAME_LOCATION_END)
  private Integer locationEnd;

  public static final String SERIALIZED_NAME_LOCATION_TEXT = "location_text";
  @SerializedName(SERIALIZED_NAME_LOCATION_TEXT)
  private String locationText;

  public static final String SERIALIZED_NAME_MODIFIED_BY = "modified_by";
  @SerializedName(SERIALIZED_NAME_MODIFIED_BY)
  private Integer modifiedBy;

  public static final String SERIALIZED_NAME_MODIFIED_DATE = "modified_date";
  @SerializedName(SERIALIZED_NAME_MODIFIED_DATE)
  private OffsetDateTime modifiedDate;


   /**
   * Get pk
   * @return pk
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getPk() {
    return pk;
  }




  public AnnotationUpdateResponse document(Integer document) {
    
    this.document = document;
    return this;
  }

   /**
   * Get document
   * @return document
  **/
  @ApiModelProperty(required = true, value = "")

  public Integer getDocument() {
    return document;
  }


  public void setDocument(Integer document) {
    this.document = document;
  }


  public AnnotationUpdateResponse documentName(String documentName) {
    
    this.documentName = documentName;
    return this;
  }

   /**
   * Get documentName
   * @return documentName
  **/
  @ApiModelProperty(required = true, value = "")

  public String getDocumentName() {
    return documentName;
  }


  public void setDocumentName(String documentName) {
    this.documentName = documentName;
  }


  public AnnotationUpdateResponse field(String field) {
    
    this.field = field;
    return this;
  }

   /**
   * Get field
   * @return field
  **/
  @ApiModelProperty(required = true, value = "")

  public String getField() {
    return field;
  }


  public void setField(String field) {
    this.field = field;
  }


  public AnnotationUpdateResponse fieldName(String fieldName) {
    
    this.fieldName = fieldName;
    return this;
  }

   /**
   * Get fieldName
   * @return fieldName
  **/
  @ApiModelProperty(required = true, value = "")

  public String getFieldName() {
    return fieldName;
  }


  public void setFieldName(String fieldName) {
    this.fieldName = fieldName;
  }


  public AnnotationUpdateResponse value(Object value) {
    
    this.value = value;
    return this;
  }

   /**
   * Get value
   * @return value
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(required = true, value = "")

  public Object getValue() {
    return value;
  }


  public void setValue(Object value) {
    this.value = value;
  }


  public AnnotationUpdateResponse project(String project) {
    
    this.project = project;
    return this;
  }

   /**
   * Get project
   * @return project
  **/
  @ApiModelProperty(required = true, value = "")

  public String getProject() {
    return project;
  }


  public void setProject(String project) {
    this.project = project;
  }


  public AnnotationUpdateResponse locationStart(Integer locationStart) {
    
    this.locationStart = locationStart;
    return this;
  }

   /**
   * Get locationStart
   * minimum: 0
   * maximum: 2147483647
   * @return locationStart
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(required = true, value = "")

  public Integer getLocationStart() {
    return locationStart;
  }


  public void setLocationStart(Integer locationStart) {
    this.locationStart = locationStart;
  }


  public AnnotationUpdateResponse locationEnd(Integer locationEnd) {
    
    this.locationEnd = locationEnd;
    return this;
  }

   /**
   * Get locationEnd
   * minimum: 0
   * maximum: 2147483647
   * @return locationEnd
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(required = true, value = "")

  public Integer getLocationEnd() {
    return locationEnd;
  }


  public void setLocationEnd(Integer locationEnd) {
    this.locationEnd = locationEnd;
  }


  public AnnotationUpdateResponse locationText(String locationText) {
    
    this.locationText = locationText;
    return this;
  }

   /**
   * Get locationText
   * @return locationText
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getLocationText() {
    return locationText;
  }


  public void setLocationText(String locationText) {
    this.locationText = locationText;
  }


  public AnnotationUpdateResponse modifiedBy(Integer modifiedBy) {
    
    this.modifiedBy = modifiedBy;
    return this;
  }

   /**
   * Get modifiedBy
   * @return modifiedBy
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getModifiedBy() {
    return modifiedBy;
  }


  public void setModifiedBy(Integer modifiedBy) {
    this.modifiedBy = modifiedBy;
  }


   /**
   * Get modifiedDate
   * @return modifiedDate
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public OffsetDateTime getModifiedDate() {
    return modifiedDate;
  }




  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    AnnotationUpdateResponse annotationUpdateResponse = (AnnotationUpdateResponse) o;
    return Objects.equals(this.pk, annotationUpdateResponse.pk) &&
        Objects.equals(this.document, annotationUpdateResponse.document) &&
        Objects.equals(this.documentName, annotationUpdateResponse.documentName) &&
        Objects.equals(this.field, annotationUpdateResponse.field) &&
        Objects.equals(this.fieldName, annotationUpdateResponse.fieldName) &&
        Objects.equals(this.value, annotationUpdateResponse.value) &&
        Objects.equals(this.project, annotationUpdateResponse.project) &&
        Objects.equals(this.locationStart, annotationUpdateResponse.locationStart) &&
        Objects.equals(this.locationEnd, annotationUpdateResponse.locationEnd) &&
        Objects.equals(this.locationText, annotationUpdateResponse.locationText) &&
        Objects.equals(this.modifiedBy, annotationUpdateResponse.modifiedBy) &&
        Objects.equals(this.modifiedDate, annotationUpdateResponse.modifiedDate);
  }

  @Override
  public int hashCode() {
    return Objects.hash(pk, document, documentName, field, fieldName, value, project, locationStart, locationEnd, locationText, modifiedBy, modifiedDate);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class AnnotationUpdateResponse {\n");
    sb.append("    pk: ").append(toIndentedString(pk)).append("\n");
    sb.append("    document: ").append(toIndentedString(document)).append("\n");
    sb.append("    documentName: ").append(toIndentedString(documentName)).append("\n");
    sb.append("    field: ").append(toIndentedString(field)).append("\n");
    sb.append("    fieldName: ").append(toIndentedString(fieldName)).append("\n");
    sb.append("    value: ").append(toIndentedString(value)).append("\n");
    sb.append("    project: ").append(toIndentedString(project)).append("\n");
    sb.append("    locationStart: ").append(toIndentedString(locationStart)).append("\n");
    sb.append("    locationEnd: ").append(toIndentedString(locationEnd)).append("\n");
    sb.append("    locationText: ").append(toIndentedString(locationText)).append("\n");
    sb.append("    modifiedBy: ").append(toIndentedString(modifiedBy)).append("\n");
    sb.append("    modifiedDate: ").append(toIndentedString(modifiedDate)).append("\n");
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
