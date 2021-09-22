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
import org.openapitools.jackson.nullable.JsonNullable;

/**
 * CitationUsage
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-09-21T17:23:12.379447+03:00[Europe/Moscow]")
public class CitationUsage {
  public static final String SERIALIZED_NAME_VOLUME = "volume";
  @SerializedName(SERIALIZED_NAME_VOLUME)
  private Integer volume;

  public static final String SERIALIZED_NAME_REPORTER = "reporter";
  @SerializedName(SERIALIZED_NAME_REPORTER)
  private String reporter;

  public static final String SERIALIZED_NAME_REPORTER_FULL_NAME = "reporter_full_name";
  @SerializedName(SERIALIZED_NAME_REPORTER_FULL_NAME)
  private String reporterFullName;

  public static final String SERIALIZED_NAME_PAGE = "page";
  @SerializedName(SERIALIZED_NAME_PAGE)
  private Integer page;

  public static final String SERIALIZED_NAME_PAGE2 = "page2";
  @SerializedName(SERIALIZED_NAME_PAGE2)
  private String page2;

  public static final String SERIALIZED_NAME_COURT = "court";
  @SerializedName(SERIALIZED_NAME_COURT)
  private String court;

  public static final String SERIALIZED_NAME_YEAR = "year";
  @SerializedName(SERIALIZED_NAME_YEAR)
  private Integer year;

  public static final String SERIALIZED_NAME_CITATION_STR = "citation_str";
  @SerializedName(SERIALIZED_NAME_CITATION_STR)
  private String citationStr;

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


  public CitationUsage volume(Integer volume) {
    
    this.volume = volume;
    return this;
  }

   /**
   * Get volume
   * minimum: 0
   * maximum: 2147483647
   * @return volume
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getVolume() {
    return volume;
  }


  public void setVolume(Integer volume) {
    this.volume = volume;
  }


  public CitationUsage reporter(String reporter) {
    
    this.reporter = reporter;
    return this;
  }

   /**
   * Get reporter
   * @return reporter
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getReporter() {
    return reporter;
  }


  public void setReporter(String reporter) {
    this.reporter = reporter;
  }


  public CitationUsage reporterFullName(String reporterFullName) {
    
    this.reporterFullName = reporterFullName;
    return this;
  }

   /**
   * Get reporterFullName
   * @return reporterFullName
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getReporterFullName() {
    return reporterFullName;
  }


  public void setReporterFullName(String reporterFullName) {
    this.reporterFullName = reporterFullName;
  }


  public CitationUsage page(Integer page) {
    
    this.page = page;
    return this;
  }

   /**
   * Get page
   * minimum: 0
   * maximum: 2147483647
   * @return page
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getPage() {
    return page;
  }


  public void setPage(Integer page) {
    this.page = page;
  }


  public CitationUsage page2(String page2) {
    
    this.page2 = page2;
    return this;
  }

   /**
   * Get page2
   * @return page2
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getPage2() {
    return page2;
  }


  public void setPage2(String page2) {
    this.page2 = page2;
  }


  public CitationUsage court(String court) {
    
    this.court = court;
    return this;
  }

   /**
   * Get court
   * @return court
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getCourt() {
    return court;
  }


  public void setCourt(String court) {
    this.court = court;
  }


  public CitationUsage year(Integer year) {
    
    this.year = year;
    return this;
  }

   /**
   * Get year
   * minimum: 0
   * maximum: 32767
   * @return year
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getYear() {
    return year;
  }


  public void setYear(Integer year) {
    this.year = year;
  }


  public CitationUsage citationStr(String citationStr) {
    
    this.citationStr = citationStr;
    return this;
  }

   /**
   * Get citationStr
   * @return citationStr
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getCitationStr() {
    return citationStr;
  }


  public void setCitationStr(String citationStr) {
    this.citationStr = citationStr;
  }


  public CitationUsage count(Integer count) {
    
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
    CitationUsage citationUsage = (CitationUsage) o;
    return Objects.equals(this.volume, citationUsage.volume) &&
        Objects.equals(this.reporter, citationUsage.reporter) &&
        Objects.equals(this.reporterFullName, citationUsage.reporterFullName) &&
        Objects.equals(this.page, citationUsage.page) &&
        Objects.equals(this.page2, citationUsage.page2) &&
        Objects.equals(this.court, citationUsage.court) &&
        Objects.equals(this.year, citationUsage.year) &&
        Objects.equals(this.citationStr, citationUsage.citationStr) &&
        Objects.equals(this.count, citationUsage.count) &&
        Objects.equals(this.pk, citationUsage.pk) &&
        Objects.equals(this.textUnitPk, citationUsage.textUnitPk) &&
        Objects.equals(this.textUnitUnitType, citationUsage.textUnitUnitType) &&
        Objects.equals(this.textUnitLocationStart, citationUsage.textUnitLocationStart) &&
        Objects.equals(this.textUnitLocationEnd, citationUsage.textUnitLocationEnd) &&
        Objects.equals(this.textUnitDocumentPk, citationUsage.textUnitDocumentPk) &&
        Objects.equals(this.textUnitDocumentName, citationUsage.textUnitDocumentName) &&
        Objects.equals(this.textUnitDocumentDescription, citationUsage.textUnitDocumentDescription) &&
        Objects.equals(this.textUnitDocumentDocumentType, citationUsage.textUnitDocumentDocumentType);
  }

  private static <T> boolean equalsNullable(JsonNullable<T> a, JsonNullable<T> b) {
    return a == b || (a != null && b != null && a.isPresent() && b.isPresent() && a.get().getClass().isArray() ? Arrays.equals((T[])a.get(), (T[])b.get()) : Objects.equals(a.get(), b.get()));
  }

  @Override
  public int hashCode() {
    return Objects.hash(volume, reporter, reporterFullName, page, page2, court, year, citationStr, count, pk, textUnitPk, textUnitUnitType, textUnitLocationStart, textUnitLocationEnd, textUnitDocumentPk, textUnitDocumentName, textUnitDocumentDescription, textUnitDocumentDocumentType);
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
    sb.append("class CitationUsage {\n");
    sb.append("    volume: ").append(toIndentedString(volume)).append("\n");
    sb.append("    reporter: ").append(toIndentedString(reporter)).append("\n");
    sb.append("    reporterFullName: ").append(toIndentedString(reporterFullName)).append("\n");
    sb.append("    page: ").append(toIndentedString(page)).append("\n");
    sb.append("    page2: ").append(toIndentedString(page2)).append("\n");
    sb.append("    court: ").append(toIndentedString(court)).append("\n");
    sb.append("    year: ").append(toIndentedString(year)).append("\n");
    sb.append("    citationStr: ").append(toIndentedString(citationStr)).append("\n");
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

