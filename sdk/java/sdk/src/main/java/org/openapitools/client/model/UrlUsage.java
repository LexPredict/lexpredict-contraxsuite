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
 * UrlUsage
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2022-01-19T15:46:46.101102+03:00[Europe/Moscow]")
public class UrlUsage {
  public static final String SERIALIZED_NAME_SOURCE_URL = "source_url";
  @SerializedName(SERIALIZED_NAME_SOURCE_URL)
  private String sourceUrl;

  public static final String SERIALIZED_NAME_COUNT = "count";
  @SerializedName(SERIALIZED_NAME_COUNT)
  private Integer count;

  public static final String SERIALIZED_NAME_PK = "pk";
  @SerializedName(SERIALIZED_NAME_PK)
  private Integer pk;

  public static final String SERIALIZED_NAME_TEXT_UNIT_PK = "text_unit__pk";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_PK)
  private String textUnitPk;

  public static final String SERIALIZED_NAME_TEXT_UNIT_UNIT_TYPE = "text_unit__unit_type";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_UNIT_TYPE)
  private String textUnitUnitType;

  public static final String SERIALIZED_NAME_TEXT_UNIT_LOCATION_START = "text_unit__location_start";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_LOCATION_START)
  private String textUnitLocationStart;

  public static final String SERIALIZED_NAME_TEXT_UNIT_LOCATION_END = "text_unit__location_end";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_LOCATION_END)
  private String textUnitLocationEnd;

  public static final String SERIALIZED_NAME_TEXT_UNIT_DOCUMENT_PK = "text_unit__document__pk";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_DOCUMENT_PK)
  private String textUnitDocumentPk;

  public static final String SERIALIZED_NAME_TEXT_UNIT_DOCUMENT_NAME = "text_unit__document__name";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_DOCUMENT_NAME)
  private String textUnitDocumentName;

  public static final String SERIALIZED_NAME_TEXT_UNIT_DOCUMENT_DESCRIPTION = "text_unit__document__description";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_DOCUMENT_DESCRIPTION)
  private String textUnitDocumentDescription;

  public static final String SERIALIZED_NAME_TEXT_UNIT_DOCUMENT_DOCUMENT_TYPE = "text_unit__document__document_type";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_DOCUMENT_DOCUMENT_TYPE)
  private String textUnitDocumentDocumentType;

  public UrlUsage() { 
  }

  
  public UrlUsage(
     Integer pk, 
     String textUnitPk, 
     String textUnitUnitType, 
     String textUnitLocationStart, 
     String textUnitLocationEnd, 
     String textUnitDocumentPk, 
     String textUnitDocumentName, 
     String textUnitDocumentDescription, 
     String textUnitDocumentDocumentType
  ) {
    this();
    this.pk = pk;
    this.textUnitPk = textUnitPk;
    this.textUnitUnitType = textUnitUnitType;
    this.textUnitLocationStart = textUnitLocationStart;
    this.textUnitLocationEnd = textUnitLocationEnd;
    this.textUnitDocumentPk = textUnitDocumentPk;
    this.textUnitDocumentName = textUnitDocumentName;
    this.textUnitDocumentDescription = textUnitDocumentDescription;
    this.textUnitDocumentDocumentType = textUnitDocumentDocumentType;
  }

  public UrlUsage sourceUrl(String sourceUrl) {
    
    this.sourceUrl = sourceUrl;
    return this;
  }

   /**
   * Get sourceUrl
   * @return sourceUrl
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getSourceUrl() {
    return sourceUrl;
  }


  public void setSourceUrl(String sourceUrl) {
    this.sourceUrl = sourceUrl;
  }


  public UrlUsage count(Integer count) {
    
    this.count = count;
    return this;
  }

   /**
   * Get count
   * minimum: -2147483648
   * maximum: 2147483647
   * @return count
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getCount() {
    return count;
  }


  public void setCount(Integer count) {
    this.count = count;
  }


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
   * Get textUnitLocationStart
   * @return textUnitLocationStart
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getTextUnitLocationStart() {
    return textUnitLocationStart;
  }




   /**
   * Get textUnitLocationEnd
   * @return textUnitLocationEnd
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getTextUnitLocationEnd() {
    return textUnitLocationEnd;
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
   * Get textUnitDocumentDescription
   * @return textUnitDocumentDescription
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getTextUnitDocumentDescription() {
    return textUnitDocumentDescription;
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




  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    UrlUsage urlUsage = (UrlUsage) o;
    return Objects.equals(this.sourceUrl, urlUsage.sourceUrl) &&
        Objects.equals(this.count, urlUsage.count) &&
        Objects.equals(this.pk, urlUsage.pk) &&
        Objects.equals(this.textUnitPk, urlUsage.textUnitPk) &&
        Objects.equals(this.textUnitUnitType, urlUsage.textUnitUnitType) &&
        Objects.equals(this.textUnitLocationStart, urlUsage.textUnitLocationStart) &&
        Objects.equals(this.textUnitLocationEnd, urlUsage.textUnitLocationEnd) &&
        Objects.equals(this.textUnitDocumentPk, urlUsage.textUnitDocumentPk) &&
        Objects.equals(this.textUnitDocumentName, urlUsage.textUnitDocumentName) &&
        Objects.equals(this.textUnitDocumentDescription, urlUsage.textUnitDocumentDescription) &&
        Objects.equals(this.textUnitDocumentDocumentType, urlUsage.textUnitDocumentDocumentType);
  }

  @Override
  public int hashCode() {
    return Objects.hash(sourceUrl, count, pk, textUnitPk, textUnitUnitType, textUnitLocationStart, textUnitLocationEnd, textUnitDocumentPk, textUnitDocumentName, textUnitDocumentDescription, textUnitDocumentDocumentType);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class UrlUsage {\n");
    sb.append("    sourceUrl: ").append(toIndentedString(sourceUrl)).append("\n");
    sb.append("    count: ").append(toIndentedString(count)).append("\n");
    sb.append("    pk: ").append(toIndentedString(pk)).append("\n");
    sb.append("    textUnitPk: ").append(toIndentedString(textUnitPk)).append("\n");
    sb.append("    textUnitUnitType: ").append(toIndentedString(textUnitUnitType)).append("\n");
    sb.append("    textUnitLocationStart: ").append(toIndentedString(textUnitLocationStart)).append("\n");
    sb.append("    textUnitLocationEnd: ").append(toIndentedString(textUnitLocationEnd)).append("\n");
    sb.append("    textUnitDocumentPk: ").append(toIndentedString(textUnitDocumentPk)).append("\n");
    sb.append("    textUnitDocumentName: ").append(toIndentedString(textUnitDocumentName)).append("\n");
    sb.append("    textUnitDocumentDescription: ").append(toIndentedString(textUnitDocumentDescription)).append("\n");
    sb.append("    textUnitDocumentDocumentType: ").append(toIndentedString(textUnitDocumentDocumentType)).append("\n");
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

