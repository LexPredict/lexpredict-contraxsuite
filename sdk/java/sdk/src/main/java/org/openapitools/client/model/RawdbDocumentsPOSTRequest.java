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
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * RawdbDocumentsPOSTRequest
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-09-21T17:23:12.379447+03:00[Europe/Moscow]")
public class RawdbDocumentsPOSTRequest {
  public static final String SERIALIZED_NAME_PROJECT_IDS = "project_ids";
  @SerializedName(SERIALIZED_NAME_PROJECT_IDS)
  private String projectIds;

  public static final String SERIALIZED_NAME_COLUMNS = "columns";
  @SerializedName(SERIALIZED_NAME_COLUMNS)
  private String columns;

  public static final String SERIALIZED_NAME_ASSOCIATED_TEXT = "associated_text";
  @SerializedName(SERIALIZED_NAME_ASSOCIATED_TEXT)
  private Boolean associatedText;

  public static final String SERIALIZED_NAME_AS_ZIP = "as_zip";
  @SerializedName(SERIALIZED_NAME_AS_ZIP)
  private Boolean asZip;

  public static final String SERIALIZED_NAME_FMT = "fmt";
  @SerializedName(SERIALIZED_NAME_FMT)
  private String fmt;

  public static final String SERIALIZED_NAME_LIMIT = "limit";
  @SerializedName(SERIALIZED_NAME_LIMIT)
  private Integer limit;

  public static final String SERIALIZED_NAME_ORDER_BY = "order_by";
  @SerializedName(SERIALIZED_NAME_ORDER_BY)
  private String orderBy;

  public static final String SERIALIZED_NAME_SAVED_FILTERS = "saved_filters";
  @SerializedName(SERIALIZED_NAME_SAVED_FILTERS)
  private String savedFilters;

  public static final String SERIALIZED_NAME_SAVE_FILTER = "save_filter";
  @SerializedName(SERIALIZED_NAME_SAVE_FILTER)
  private Boolean saveFilter;

  public static final String SERIALIZED_NAME_RETURN_REVIEWED = "return_reviewed";
  @SerializedName(SERIALIZED_NAME_RETURN_REVIEWED)
  private Boolean returnReviewed;

  public static final String SERIALIZED_NAME_RETURN_TOTAL = "return_total";
  @SerializedName(SERIALIZED_NAME_RETURN_TOTAL)
  private Boolean returnTotal;

  public static final String SERIALIZED_NAME_RETURN_DATA = "return_data";
  @SerializedName(SERIALIZED_NAME_RETURN_DATA)
  private Boolean returnData;

  public static final String SERIALIZED_NAME_IGNORE_ERRORS = "ignore_errors";
  @SerializedName(SERIALIZED_NAME_IGNORE_ERRORS)
  private Boolean ignoreErrors;

  public static final String SERIALIZED_NAME_FILTERS = "filters";
  @SerializedName(SERIALIZED_NAME_FILTERS)
  private Map<String, String> filters = null;


  public RawdbDocumentsPOSTRequest projectIds(String projectIds) {
    
    this.projectIds = projectIds;
    return this;
  }

   /**
   * Get projectIds
   * @return projectIds
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getProjectIds() {
    return projectIds;
  }


  public void setProjectIds(String projectIds) {
    this.projectIds = projectIds;
  }


  public RawdbDocumentsPOSTRequest columns(String columns) {
    
    this.columns = columns;
    return this;
  }

   /**
   * Get columns
   * @return columns
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getColumns() {
    return columns;
  }


  public void setColumns(String columns) {
    this.columns = columns;
  }


  public RawdbDocumentsPOSTRequest associatedText(Boolean associatedText) {
    
    this.associatedText = associatedText;
    return this;
  }

   /**
   * Get associatedText
   * @return associatedText
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Boolean getAssociatedText() {
    return associatedText;
  }


  public void setAssociatedText(Boolean associatedText) {
    this.associatedText = associatedText;
  }


  public RawdbDocumentsPOSTRequest asZip(Boolean asZip) {
    
    this.asZip = asZip;
    return this;
  }

   /**
   * Get asZip
   * @return asZip
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Boolean getAsZip() {
    return asZip;
  }


  public void setAsZip(Boolean asZip) {
    this.asZip = asZip;
  }


  public RawdbDocumentsPOSTRequest fmt(String fmt) {
    
    this.fmt = fmt;
    return this;
  }

   /**
   * Get fmt
   * @return fmt
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getFmt() {
    return fmt;
  }


  public void setFmt(String fmt) {
    this.fmt = fmt;
  }


  public RawdbDocumentsPOSTRequest limit(Integer limit) {
    
    this.limit = limit;
    return this;
  }

   /**
   * Get limit
   * @return limit
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getLimit() {
    return limit;
  }


  public void setLimit(Integer limit) {
    this.limit = limit;
  }


  public RawdbDocumentsPOSTRequest orderBy(String orderBy) {
    
    this.orderBy = orderBy;
    return this;
  }

   /**
   * Get orderBy
   * @return orderBy
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getOrderBy() {
    return orderBy;
  }


  public void setOrderBy(String orderBy) {
    this.orderBy = orderBy;
  }


  public RawdbDocumentsPOSTRequest savedFilters(String savedFilters) {
    
    this.savedFilters = savedFilters;
    return this;
  }

   /**
   * Get savedFilters
   * @return savedFilters
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getSavedFilters() {
    return savedFilters;
  }


  public void setSavedFilters(String savedFilters) {
    this.savedFilters = savedFilters;
  }


  public RawdbDocumentsPOSTRequest saveFilter(Boolean saveFilter) {
    
    this.saveFilter = saveFilter;
    return this;
  }

   /**
   * Get saveFilter
   * @return saveFilter
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Boolean getSaveFilter() {
    return saveFilter;
  }


  public void setSaveFilter(Boolean saveFilter) {
    this.saveFilter = saveFilter;
  }


  public RawdbDocumentsPOSTRequest returnReviewed(Boolean returnReviewed) {
    
    this.returnReviewed = returnReviewed;
    return this;
  }

   /**
   * Get returnReviewed
   * @return returnReviewed
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Boolean getReturnReviewed() {
    return returnReviewed;
  }


  public void setReturnReviewed(Boolean returnReviewed) {
    this.returnReviewed = returnReviewed;
  }


  public RawdbDocumentsPOSTRequest returnTotal(Boolean returnTotal) {
    
    this.returnTotal = returnTotal;
    return this;
  }

   /**
   * Get returnTotal
   * @return returnTotal
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Boolean getReturnTotal() {
    return returnTotal;
  }


  public void setReturnTotal(Boolean returnTotal) {
    this.returnTotal = returnTotal;
  }


  public RawdbDocumentsPOSTRequest returnData(Boolean returnData) {
    
    this.returnData = returnData;
    return this;
  }

   /**
   * Get returnData
   * @return returnData
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Boolean getReturnData() {
    return returnData;
  }


  public void setReturnData(Boolean returnData) {
    this.returnData = returnData;
  }


  public RawdbDocumentsPOSTRequest ignoreErrors(Boolean ignoreErrors) {
    
    this.ignoreErrors = ignoreErrors;
    return this;
  }

   /**
   * Get ignoreErrors
   * @return ignoreErrors
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Boolean getIgnoreErrors() {
    return ignoreErrors;
  }


  public void setIgnoreErrors(Boolean ignoreErrors) {
    this.ignoreErrors = ignoreErrors;
  }


  public RawdbDocumentsPOSTRequest filters(Map<String, String> filters) {
    
    this.filters = filters;
    return this;
  }

  public RawdbDocumentsPOSTRequest putFiltersItem(String key, String filtersItem) {
    if (this.filters == null) {
      this.filters = new HashMap<String, String>();
    }
    this.filters.put(key, filtersItem);
    return this;
  }

   /**
   * Get filters
   * @return filters
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Map<String, String> getFilters() {
    return filters;
  }


  public void setFilters(Map<String, String> filters) {
    this.filters = filters;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    RawdbDocumentsPOSTRequest rawdbDocumentsPOSTRequest = (RawdbDocumentsPOSTRequest) o;
    return Objects.equals(this.projectIds, rawdbDocumentsPOSTRequest.projectIds) &&
        Objects.equals(this.columns, rawdbDocumentsPOSTRequest.columns) &&
        Objects.equals(this.associatedText, rawdbDocumentsPOSTRequest.associatedText) &&
        Objects.equals(this.asZip, rawdbDocumentsPOSTRequest.asZip) &&
        Objects.equals(this.fmt, rawdbDocumentsPOSTRequest.fmt) &&
        Objects.equals(this.limit, rawdbDocumentsPOSTRequest.limit) &&
        Objects.equals(this.orderBy, rawdbDocumentsPOSTRequest.orderBy) &&
        Objects.equals(this.savedFilters, rawdbDocumentsPOSTRequest.savedFilters) &&
        Objects.equals(this.saveFilter, rawdbDocumentsPOSTRequest.saveFilter) &&
        Objects.equals(this.returnReviewed, rawdbDocumentsPOSTRequest.returnReviewed) &&
        Objects.equals(this.returnTotal, rawdbDocumentsPOSTRequest.returnTotal) &&
        Objects.equals(this.returnData, rawdbDocumentsPOSTRequest.returnData) &&
        Objects.equals(this.ignoreErrors, rawdbDocumentsPOSTRequest.ignoreErrors) &&
        Objects.equals(this.filters, rawdbDocumentsPOSTRequest.filters);
  }

  @Override
  public int hashCode() {
    return Objects.hash(projectIds, columns, associatedText, asZip, fmt, limit, orderBy, savedFilters, saveFilter, returnReviewed, returnTotal, returnData, ignoreErrors, filters);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class RawdbDocumentsPOSTRequest {\n");
    sb.append("    projectIds: ").append(toIndentedString(projectIds)).append("\n");
    sb.append("    columns: ").append(toIndentedString(columns)).append("\n");
    sb.append("    associatedText: ").append(toIndentedString(associatedText)).append("\n");
    sb.append("    asZip: ").append(toIndentedString(asZip)).append("\n");
    sb.append("    fmt: ").append(toIndentedString(fmt)).append("\n");
    sb.append("    limit: ").append(toIndentedString(limit)).append("\n");
    sb.append("    orderBy: ").append(toIndentedString(orderBy)).append("\n");
    sb.append("    savedFilters: ").append(toIndentedString(savedFilters)).append("\n");
    sb.append("    saveFilter: ").append(toIndentedString(saveFilter)).append("\n");
    sb.append("    returnReviewed: ").append(toIndentedString(returnReviewed)).append("\n");
    sb.append("    returnTotal: ").append(toIndentedString(returnTotal)).append("\n");
    sb.append("    returnData: ").append(toIndentedString(returnData)).append("\n");
    sb.append("    ignoreErrors: ").append(toIndentedString(ignoreErrors)).append("\n");
    sb.append("    filters: ").append(toIndentedString(filters)).append("\n");
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

