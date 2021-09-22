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
import org.threeten.bp.OffsetDateTime;

/**
 * TextUnitClassification
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-09-21T17:23:12.379447+03:00[Europe/Moscow]")
public class TextUnitClassification {
  public static final String SERIALIZED_NAME_PK = "pk";
  @SerializedName(SERIALIZED_NAME_PK)
  private Integer pk;

  public static final String SERIALIZED_NAME_TEXT_UNIT_DOCUMENT_PK = "text_unit__document__pk";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_DOCUMENT_PK)
  private String textUnitDocumentPk;

  public static final String SERIALIZED_NAME_TEXT_UNIT_DOCUMENT_NAME = "text_unit__document__name";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_DOCUMENT_NAME)
  private String textUnitDocumentName;

  public static final String SERIALIZED_NAME_TEXT_UNIT_DOCUMENT_DOCUMENT_TYPE = "text_unit__document__document_type";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_DOCUMENT_DOCUMENT_TYPE)
  private String textUnitDocumentDocumentType;

  public static final String SERIALIZED_NAME_TEXT_UNIT_DOCUMENT_DESCRIPTION = "text_unit__document__description";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_DOCUMENT_DESCRIPTION)
  private String textUnitDocumentDescription;

  public static final String SERIALIZED_NAME_TEXT_UNIT_PK = "text_unit__pk";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_PK)
  private String textUnitPk;

  public static final String SERIALIZED_NAME_TEXT_UNIT_UNIT_TYPE = "text_unit__unit_type";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_UNIT_TYPE)
  private String textUnitUnitType;

  public static final String SERIALIZED_NAME_TEXT_UNIT_LANGUAGE = "text_unit__language";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_LANGUAGE)
  private String textUnitLanguage;

  public static final String SERIALIZED_NAME_CLASS_NAME = "class_name";
  @SerializedName(SERIALIZED_NAME_CLASS_NAME)
  private String className;

  public static final String SERIALIZED_NAME_CLASS_VALUE = "class_value";
  @SerializedName(SERIALIZED_NAME_CLASS_VALUE)
  private String classValue;

  public static final String SERIALIZED_NAME_USER_USERNAME = "user__username";
  @SerializedName(SERIALIZED_NAME_USER_USERNAME)
  private String userUsername;

  public static final String SERIALIZED_NAME_TIMESTAMP = "timestamp";
  @SerializedName(SERIALIZED_NAME_TIMESTAMP)
  private OffsetDateTime timestamp;


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
   * Get textUnitDocumentPk
   * @return textUnitDocumentPk
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getTextUnitDocumentPk() {
    return textUnitDocumentPk;
  }




   /**
   * Get textUnitDocumentName
   * @return textUnitDocumentName
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getTextUnitDocumentName() {
    return textUnitDocumentName;
  }




   /**
   * Get textUnitDocumentDocumentType
   * @return textUnitDocumentDocumentType
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getTextUnitDocumentDocumentType() {
    return textUnitDocumentDocumentType;
  }




   /**
   * Get textUnitDocumentDescription
   * @return textUnitDocumentDescription
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getTextUnitDocumentDescription() {
    return textUnitDocumentDescription;
  }




   /**
   * Get textUnitPk
   * @return textUnitPk
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getTextUnitPk() {
    return textUnitPk;
  }




   /**
   * Get textUnitUnitType
   * @return textUnitUnitType
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getTextUnitUnitType() {
    return textUnitUnitType;
  }




   /**
   * Get textUnitLanguage
   * @return textUnitLanguage
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getTextUnitLanguage() {
    return textUnitLanguage;
  }




  public TextUnitClassification className(String className) {
    
    this.className = className;
    return this;
  }

   /**
   * Get className
   * @return className
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getClassName() {
    return className;
  }


  public void setClassName(String className) {
    this.className = className;
  }


  public TextUnitClassification classValue(String classValue) {
    
    this.classValue = classValue;
    return this;
  }

   /**
   * Get classValue
   * @return classValue
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getClassValue() {
    return classValue;
  }


  public void setClassValue(String classValue) {
    this.classValue = classValue;
  }


   /**
   * Get userUsername
   * @return userUsername
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getUserUsername() {
    return userUsername;
  }




  public TextUnitClassification timestamp(OffsetDateTime timestamp) {
    
    this.timestamp = timestamp;
    return this;
  }

   /**
   * Get timestamp
   * @return timestamp
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public OffsetDateTime getTimestamp() {
    return timestamp;
  }


  public void setTimestamp(OffsetDateTime timestamp) {
    this.timestamp = timestamp;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    TextUnitClassification textUnitClassification = (TextUnitClassification) o;
    return Objects.equals(this.pk, textUnitClassification.pk) &&
        Objects.equals(this.textUnitDocumentPk, textUnitClassification.textUnitDocumentPk) &&
        Objects.equals(this.textUnitDocumentName, textUnitClassification.textUnitDocumentName) &&
        Objects.equals(this.textUnitDocumentDocumentType, textUnitClassification.textUnitDocumentDocumentType) &&
        Objects.equals(this.textUnitDocumentDescription, textUnitClassification.textUnitDocumentDescription) &&
        Objects.equals(this.textUnitPk, textUnitClassification.textUnitPk) &&
        Objects.equals(this.textUnitUnitType, textUnitClassification.textUnitUnitType) &&
        Objects.equals(this.textUnitLanguage, textUnitClassification.textUnitLanguage) &&
        Objects.equals(this.className, textUnitClassification.className) &&
        Objects.equals(this.classValue, textUnitClassification.classValue) &&
        Objects.equals(this.userUsername, textUnitClassification.userUsername) &&
        Objects.equals(this.timestamp, textUnitClassification.timestamp);
  }

  @Override
  public int hashCode() {
    return Objects.hash(pk, textUnitDocumentPk, textUnitDocumentName, textUnitDocumentDocumentType, textUnitDocumentDescription, textUnitPk, textUnitUnitType, textUnitLanguage, className, classValue, userUsername, timestamp);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class TextUnitClassification {\n");
    sb.append("    pk: ").append(toIndentedString(pk)).append("\n");
    sb.append("    textUnitDocumentPk: ").append(toIndentedString(textUnitDocumentPk)).append("\n");
    sb.append("    textUnitDocumentName: ").append(toIndentedString(textUnitDocumentName)).append("\n");
    sb.append("    textUnitDocumentDocumentType: ").append(toIndentedString(textUnitDocumentDocumentType)).append("\n");
    sb.append("    textUnitDocumentDescription: ").append(toIndentedString(textUnitDocumentDescription)).append("\n");
    sb.append("    textUnitPk: ").append(toIndentedString(textUnitPk)).append("\n");
    sb.append("    textUnitUnitType: ").append(toIndentedString(textUnitUnitType)).append("\n");
    sb.append("    textUnitLanguage: ").append(toIndentedString(textUnitLanguage)).append("\n");
    sb.append("    className: ").append(toIndentedString(className)).append("\n");
    sb.append("    classValue: ").append(toIndentedString(classValue)).append("\n");
    sb.append("    userUsername: ").append(toIndentedString(userUsername)).append("\n");
    sb.append("    timestamp: ").append(toIndentedString(timestamp)).append("\n");
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

