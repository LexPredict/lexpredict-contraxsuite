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
import java.util.UUID;
import org.openapitools.jackson.nullable.JsonNullable;
import org.threeten.bp.OffsetDateTime;

/**
 * AnnotationInDocument
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-09-21T17:23:12.379447+03:00[Europe/Moscow]")
public class AnnotationInDocument {
  public static final String SERIALIZED_NAME_PK = "pk";
  @SerializedName(SERIALIZED_NAME_PK)
  private Integer pk;

  public static final String SERIALIZED_NAME_DOCUMENT = "document";
  @SerializedName(SERIALIZED_NAME_DOCUMENT)
  private Integer document;

  public static final String SERIALIZED_NAME_VALUE = "value";
  @SerializedName(SERIALIZED_NAME_VALUE)
  private Object value;

  public static final String SERIALIZED_NAME_FIELD = "field";
  @SerializedName(SERIALIZED_NAME_FIELD)
  private String field;

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

  public static final String SERIALIZED_NAME_UID = "uid";
  @SerializedName(SERIALIZED_NAME_UID)
  private UUID uid;


   /**
   * Get pk
   * @return pk
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getPk() {
    return pk;
  }




  public AnnotationInDocument document(Integer document) {
    
    this.document = document;
    return this;
  }

   /**
   * Get document
   * @return document
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getDocument() {
    return document;
  }


  public void setDocument(Integer document) {
    this.document = document;
  }


  public AnnotationInDocument value(Object value) {
    
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


  public AnnotationInDocument field(String field) {
    
    this.field = field;
    return this;
  }

   /**
   * Get field
   * @return field
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getField() {
    return field;
  }


  public void setField(String field) {
    this.field = field;
  }


  public AnnotationInDocument locationStart(Integer locationStart) {
    
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


  public AnnotationInDocument locationEnd(Integer locationEnd) {
    
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


  public AnnotationInDocument locationText(String locationText) {
    
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


  public AnnotationInDocument modifiedBy(Integer modifiedBy) {
    
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




   /**
   * Get uid
   * @return uid
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public UUID getUid() {
    return uid;
  }




  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    AnnotationInDocument annotationInDocument = (AnnotationInDocument) o;
    return Objects.equals(this.pk, annotationInDocument.pk) &&
        Objects.equals(this.document, annotationInDocument.document) &&
        Objects.equals(this.value, annotationInDocument.value) &&
        Objects.equals(this.field, annotationInDocument.field) &&
        Objects.equals(this.locationStart, annotationInDocument.locationStart) &&
        Objects.equals(this.locationEnd, annotationInDocument.locationEnd) &&
        Objects.equals(this.locationText, annotationInDocument.locationText) &&
        Objects.equals(this.modifiedBy, annotationInDocument.modifiedBy) &&
        Objects.equals(this.modifiedDate, annotationInDocument.modifiedDate) &&
        Objects.equals(this.uid, annotationInDocument.uid);
  }

  private static <T> boolean equalsNullable(JsonNullable<T> a, JsonNullable<T> b) {
    return a == b || (a != null && b != null && a.isPresent() && b.isPresent() && a.get().getClass().isArray() ? Arrays.equals((T[])a.get(), (T[])b.get()) : Objects.equals(a.get(), b.get()));
  }

  @Override
  public int hashCode() {
    return Objects.hash(pk, document, value, field, locationStart, locationEnd, locationText, modifiedBy, modifiedDate, uid);
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
    sb.append("class AnnotationInDocument {\n");
    sb.append("    pk: ").append(toIndentedString(pk)).append("\n");
    sb.append("    document: ").append(toIndentedString(document)).append("\n");
    sb.append("    value: ").append(toIndentedString(value)).append("\n");
    sb.append("    field: ").append(toIndentedString(field)).append("\n");
    sb.append("    locationStart: ").append(toIndentedString(locationStart)).append("\n");
    sb.append("    locationEnd: ").append(toIndentedString(locationEnd)).append("\n");
    sb.append("    locationText: ").append(toIndentedString(locationText)).append("\n");
    sb.append("    modifiedBy: ").append(toIndentedString(modifiedBy)).append("\n");
    sb.append("    modifiedDate: ").append(toIndentedString(modifiedDate)).append("\n");
    sb.append("    uid: ").append(toIndentedString(uid)).append("\n");
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

