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

/**
 * GeoAliasUsage
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2020-12-11T16:57:55.511+03:00[Europe/Moscow]")
public class GeoAliasUsage {
  public static final String SERIALIZED_NAME_ALIAS_ALIAS = "alias__alias";
  @SerializedName(SERIALIZED_NAME_ALIAS_ALIAS)
  private String aliasAlias;

  public static final String SERIALIZED_NAME_ALIAS_LOCALE = "alias__locale";
  @SerializedName(SERIALIZED_NAME_ALIAS_LOCALE)
  private String aliasLocale;

  public static final String SERIALIZED_NAME_ALIAS_TYPE = "alias__type";
  @SerializedName(SERIALIZED_NAME_ALIAS_TYPE)
  private String aliasType;

  public static final String SERIALIZED_NAME_COUNT = "count";
  @SerializedName(SERIALIZED_NAME_COUNT)
  private Integer count;

  public static final String SERIALIZED_NAME_ALIAS_ENTITY_NAME = "alias__entity__name";
  @SerializedName(SERIALIZED_NAME_ALIAS_ENTITY_NAME)
  private String aliasEntityName;

  public static final String SERIALIZED_NAME_ALIAS_ENTITY_CATEGORY = "alias__entity__category";
  @SerializedName(SERIALIZED_NAME_ALIAS_ENTITY_CATEGORY)
  private String aliasEntityCategory;

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


   /**
   * Get aliasAlias
   * @return aliasAlias
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getAliasAlias() {
    return aliasAlias;
  }




   /**
   * Get aliasLocale
   * @return aliasLocale
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getAliasLocale() {
    return aliasLocale;
  }




   /**
   * Get aliasType
   * @return aliasType
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getAliasType() {
    return aliasType;
  }




  public GeoAliasUsage count(Integer count) {
    
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
   * Get aliasEntityName
   * @return aliasEntityName
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getAliasEntityName() {
    return aliasEntityName;
  }




   /**
   * Get aliasEntityCategory
   * @return aliasEntityCategory
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getAliasEntityCategory() {
    return aliasEntityCategory;
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
    GeoAliasUsage geoAliasUsage = (GeoAliasUsage) o;
    return Objects.equals(this.aliasAlias, geoAliasUsage.aliasAlias) &&
        Objects.equals(this.aliasLocale, geoAliasUsage.aliasLocale) &&
        Objects.equals(this.aliasType, geoAliasUsage.aliasType) &&
        Objects.equals(this.count, geoAliasUsage.count) &&
        Objects.equals(this.aliasEntityName, geoAliasUsage.aliasEntityName) &&
        Objects.equals(this.aliasEntityCategory, geoAliasUsage.aliasEntityCategory) &&
        Objects.equals(this.pk, geoAliasUsage.pk) &&
        Objects.equals(this.textUnitPk, geoAliasUsage.textUnitPk) &&
        Objects.equals(this.textUnitUnitType, geoAliasUsage.textUnitUnitType) &&
        Objects.equals(this.textUnitLocationStart, geoAliasUsage.textUnitLocationStart) &&
        Objects.equals(this.textUnitLocationEnd, geoAliasUsage.textUnitLocationEnd) &&
        Objects.equals(this.textUnitDocumentPk, geoAliasUsage.textUnitDocumentPk) &&
        Objects.equals(this.textUnitDocumentName, geoAliasUsage.textUnitDocumentName) &&
        Objects.equals(this.textUnitDocumentDescription, geoAliasUsage.textUnitDocumentDescription) &&
        Objects.equals(this.textUnitDocumentDocumentType, geoAliasUsage.textUnitDocumentDocumentType);
  }

  @Override
  public int hashCode() {
    return Objects.hash(aliasAlias, aliasLocale, aliasType, count, aliasEntityName, aliasEntityCategory, pk, textUnitPk, textUnitUnitType, textUnitLocationStart, textUnitLocationEnd, textUnitDocumentPk, textUnitDocumentName, textUnitDocumentDescription, textUnitDocumentDocumentType);
  }


  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class GeoAliasUsage {\n");
    sb.append("    aliasAlias: ").append(toIndentedString(aliasAlias)).append("\n");
    sb.append("    aliasLocale: ").append(toIndentedString(aliasLocale)).append("\n");
    sb.append("    aliasType: ").append(toIndentedString(aliasType)).append("\n");
    sb.append("    count: ").append(toIndentedString(count)).append("\n");
    sb.append("    aliasEntityName: ").append(toIndentedString(aliasEntityName)).append("\n");
    sb.append("    aliasEntityCategory: ").append(toIndentedString(aliasEntityCategory)).append("\n");
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

