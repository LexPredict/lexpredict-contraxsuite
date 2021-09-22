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
import java.math.BigDecimal;
import org.openapitools.jackson.nullable.JsonNullable;

/**
 * PercentUsage
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-09-21T17:23:12.379447+03:00[Europe/Moscow]")
public class PercentUsage {
  public static final String SERIALIZED_NAME_AMOUNT = "amount";
  @SerializedName(SERIALIZED_NAME_AMOUNT)
  private BigDecimal amount;

  public static final String SERIALIZED_NAME_UNIT_TYPE = "unit_type";
  @SerializedName(SERIALIZED_NAME_UNIT_TYPE)
  private String unitType;

  public static final String SERIALIZED_NAME_TOTAL = "total";
  @SerializedName(SERIALIZED_NAME_TOTAL)
  private BigDecimal total;

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


  public PercentUsage amount(BigDecimal amount) {
    
    this.amount = amount;
    return this;
  }

   /**
   * Get amount
   * @return amount
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public BigDecimal getAmount() {
    return amount;
  }


  public void setAmount(BigDecimal amount) {
    this.amount = amount;
  }


  public PercentUsage unitType(String unitType) {
    
    this.unitType = unitType;
    return this;
  }

   /**
   * Get unitType
   * @return unitType
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getUnitType() {
    return unitType;
  }


  public void setUnitType(String unitType) {
    this.unitType = unitType;
  }


  public PercentUsage total(BigDecimal total) {
    
    this.total = total;
    return this;
  }

   /**
   * Get total
   * @return total
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public BigDecimal getTotal() {
    return total;
  }


  public void setTotal(BigDecimal total) {
    this.total = total;
  }


  public PercentUsage count(Integer count) {
    
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
    PercentUsage percentUsage = (PercentUsage) o;
    return Objects.equals(this.amount, percentUsage.amount) &&
        Objects.equals(this.unitType, percentUsage.unitType) &&
        Objects.equals(this.total, percentUsage.total) &&
        Objects.equals(this.count, percentUsage.count) &&
        Objects.equals(this.pk, percentUsage.pk) &&
        Objects.equals(this.textUnitPk, percentUsage.textUnitPk) &&
        Objects.equals(this.textUnitUnitType, percentUsage.textUnitUnitType) &&
        Objects.equals(this.textUnitLocationStart, percentUsage.textUnitLocationStart) &&
        Objects.equals(this.textUnitLocationEnd, percentUsage.textUnitLocationEnd) &&
        Objects.equals(this.textUnitDocumentPk, percentUsage.textUnitDocumentPk) &&
        Objects.equals(this.textUnitDocumentName, percentUsage.textUnitDocumentName) &&
        Objects.equals(this.textUnitDocumentDescription, percentUsage.textUnitDocumentDescription) &&
        Objects.equals(this.textUnitDocumentDocumentType, percentUsage.textUnitDocumentDocumentType);
  }

  private static <T> boolean equalsNullable(JsonNullable<T> a, JsonNullable<T> b) {
    return a == b || (a != null && b != null && a.isPresent() && b.isPresent() && a.get().getClass().isArray() ? Arrays.equals((T[])a.get(), (T[])b.get()) : Objects.equals(a.get(), b.get()));
  }

  @Override
  public int hashCode() {
    return Objects.hash(amount, unitType, total, count, pk, textUnitPk, textUnitUnitType, textUnitLocationStart, textUnitLocationEnd, textUnitDocumentPk, textUnitDocumentName, textUnitDocumentDescription, textUnitDocumentDocumentType);
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
    sb.append("class PercentUsage {\n");
    sb.append("    amount: ").append(toIndentedString(amount)).append("\n");
    sb.append("    unitType: ").append(toIndentedString(unitType)).append("\n");
    sb.append("    total: ").append(toIndentedString(total)).append("\n");
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

