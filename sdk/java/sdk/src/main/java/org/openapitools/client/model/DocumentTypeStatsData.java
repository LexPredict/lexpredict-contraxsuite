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
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * DocumentTypeStatsData
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-09-21T17:23:12.379447+03:00[Europe/Moscow]")
public class DocumentTypeStatsData {
  public static final String SERIALIZED_NAME_UID = "uid";
  @SerializedName(SERIALIZED_NAME_UID)
  private UUID uid;

  public static final String SERIALIZED_NAME_CODE = "code";
  @SerializedName(SERIALIZED_NAME_CODE)
  private String code;

  public static final String SERIALIZED_NAME_TITLE = "title";
  @SerializedName(SERIALIZED_NAME_TITLE)
  private String title;

  public static final String SERIALIZED_NAME_FIELDS_COUNT = "fields_count";
  @SerializedName(SERIALIZED_NAME_FIELDS_COUNT)
  private Integer fieldsCount;

  public static final String SERIALIZED_NAME_DETECTORS_COUNT = "detectors_count";
  @SerializedName(SERIALIZED_NAME_DETECTORS_COUNT)
  private Integer detectorsCount;

  public static final String SERIALIZED_NAME_HIDE_UNTIL_PYTHON_COUNT = "hide_until_python_count";
  @SerializedName(SERIALIZED_NAME_HIDE_UNTIL_PYTHON_COUNT)
  private Integer hideUntilPythonCount;

  public static final String SERIALIZED_NAME_HIDDEN_ALWAYS_COUNT = "hidden_always_count";
  @SerializedName(SERIALIZED_NAME_HIDDEN_ALWAYS_COUNT)
  private Integer hiddenAlwaysCount;

  public static final String SERIALIZED_NAME_HIDE_UNTIL_PYTHON_PCNT = "hide_until_python_pcnt";
  @SerializedName(SERIALIZED_NAME_HIDE_UNTIL_PYTHON_PCNT)
  private BigDecimal hideUntilPythonPcnt;

  public static final String SERIALIZED_NAME_HIDDEN_ALWAYS_PCNT = "hidden_always_pcnt";
  @SerializedName(SERIALIZED_NAME_HIDDEN_ALWAYS_PCNT)
  private BigDecimal hiddenAlwaysPcnt;

  public static final String SERIALIZED_NAME_FIELDS_DATA = "fields_data";
  @SerializedName(SERIALIZED_NAME_FIELDS_DATA)
  private List<Object> fieldsData = null;

  public static final String SERIALIZED_NAME_DETECTOR_DISABLED_COUNT = "detector_disabled_count";
  @SerializedName(SERIALIZED_NAME_DETECTOR_DISABLED_COUNT)
  private BigDecimal detectorDisabledCount;

  public static final String SERIALIZED_NAME_DETECTOR_DISABLED_PCNT = "detector_disabled_pcnt";
  @SerializedName(SERIALIZED_NAME_DETECTOR_DISABLED_PCNT)
  private BigDecimal detectorDisabledPcnt;

  public static final String SERIALIZED_NAME_DETECTOR_USE_REGEXPS_ONLY_COUNT = "detector_use_regexps_only_count";
  @SerializedName(SERIALIZED_NAME_DETECTOR_USE_REGEXPS_ONLY_COUNT)
  private BigDecimal detectorUseRegexpsOnlyCount;

  public static final String SERIALIZED_NAME_DETECTOR_USE_REGEXPS_ONLY_PCNT = "detector_use_regexps_only_pcnt";
  @SerializedName(SERIALIZED_NAME_DETECTOR_USE_REGEXPS_ONLY_PCNT)
  private BigDecimal detectorUseRegexpsOnlyPcnt;

  public static final String SERIALIZED_NAME_DETECTOR_USE_FORMULA_ONLY_COUNT = "detector_use_formula_only_count";
  @SerializedName(SERIALIZED_NAME_DETECTOR_USE_FORMULA_ONLY_COUNT)
  private BigDecimal detectorUseFormulaOnlyCount;

  public static final String SERIALIZED_NAME_DETECTOR_USE_FORMULA_ONLY_PCNT = "detector_use_formula_only_pcnt";
  @SerializedName(SERIALIZED_NAME_DETECTOR_USE_FORMULA_ONLY_PCNT)
  private BigDecimal detectorUseFormulaOnlyPcnt;

  public static final String SERIALIZED_NAME_DETECTOR_REGEXP_TABLE_COUNT = "detector_regexp_table_count";
  @SerializedName(SERIALIZED_NAME_DETECTOR_REGEXP_TABLE_COUNT)
  private BigDecimal detectorRegexpTableCount;

  public static final String SERIALIZED_NAME_DETECTOR_REGEXP_TABLE_PCNT = "detector_regexp_table_pcnt";
  @SerializedName(SERIALIZED_NAME_DETECTOR_REGEXP_TABLE_PCNT)
  private BigDecimal detectorRegexpTablePcnt;

  public static final String SERIALIZED_NAME_DETECTOR_TEXT_BASED_ML_ONLY_COUNT = "detector_text_based_ml_only_count";
  @SerializedName(SERIALIZED_NAME_DETECTOR_TEXT_BASED_ML_ONLY_COUNT)
  private BigDecimal detectorTextBasedMlOnlyCount;

  public static final String SERIALIZED_NAME_DETECTOR_TEXT_BASED_ML_ONLY_PCNT = "detector_text_based_ml_only_pcnt";
  @SerializedName(SERIALIZED_NAME_DETECTOR_TEXT_BASED_ML_ONLY_PCNT)
  private BigDecimal detectorTextBasedMlOnlyPcnt;

  public static final String SERIALIZED_NAME_DETECTOR_FIELDS_BASED_ML_ONLY_COUNT = "detector_fields_based_ml_only_count";
  @SerializedName(SERIALIZED_NAME_DETECTOR_FIELDS_BASED_ML_ONLY_COUNT)
  private BigDecimal detectorFieldsBasedMlOnlyCount;

  public static final String SERIALIZED_NAME_DETECTOR_FIELDS_BASED_ML_ONLY_PCNT = "detector_fields_based_ml_only_pcnt";
  @SerializedName(SERIALIZED_NAME_DETECTOR_FIELDS_BASED_ML_ONLY_PCNT)
  private BigDecimal detectorFieldsBasedMlOnlyPcnt;

  public static final String SERIALIZED_NAME_DETECTOR_FIELDS_BASED_PROB_ML_ONLY_COUNT = "detector_fields_based_prob_ml_only_count";
  @SerializedName(SERIALIZED_NAME_DETECTOR_FIELDS_BASED_PROB_ML_ONLY_COUNT)
  private BigDecimal detectorFieldsBasedProbMlOnlyCount;

  public static final String SERIALIZED_NAME_DETECTOR_FIELDS_BASED_PROB_ML_ONLY_PCNT = "detector_fields_based_prob_ml_only_pcnt";
  @SerializedName(SERIALIZED_NAME_DETECTOR_FIELDS_BASED_PROB_ML_ONLY_PCNT)
  private BigDecimal detectorFieldsBasedProbMlOnlyPcnt;

  public static final String SERIALIZED_NAME_DETECTOR_FIELD_BASED_REGEXPS_COUNT = "detector_field_based_regexps_count";
  @SerializedName(SERIALIZED_NAME_DETECTOR_FIELD_BASED_REGEXPS_COUNT)
  private BigDecimal detectorFieldBasedRegexpsCount;

  public static final String SERIALIZED_NAME_DETECTOR_FIELD_BASED_REGEXPS_PCNT = "detector_field_based_regexps_pcnt";
  @SerializedName(SERIALIZED_NAME_DETECTOR_FIELD_BASED_REGEXPS_PCNT)
  private BigDecimal detectorFieldBasedRegexpsPcnt;

  public static final String SERIALIZED_NAME_DETECTOR_MLFLOW_MODEL_COUNT = "detector_mlflow_model_count";
  @SerializedName(SERIALIZED_NAME_DETECTOR_MLFLOW_MODEL_COUNT)
  private BigDecimal detectorMlflowModelCount;

  public static final String SERIALIZED_NAME_DETECTOR_MLFLOW_MODEL_PCNT = "detector_mlflow_model_pcnt";
  @SerializedName(SERIALIZED_NAME_DETECTOR_MLFLOW_MODEL_PCNT)
  private BigDecimal detectorMlflowModelPcnt;


  public DocumentTypeStatsData uid(UUID uid) {
    
    this.uid = uid;
    return this;
  }

   /**
   * Get uid
   * @return uid
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public UUID getUid() {
    return uid;
  }


  public void setUid(UUID uid) {
    this.uid = uid;
  }


  public DocumentTypeStatsData code(String code) {
    
    this.code = code;
    return this;
  }

   /**
   * Get code
   * @return code
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getCode() {
    return code;
  }


  public void setCode(String code) {
    this.code = code;
  }


  public DocumentTypeStatsData title(String title) {
    
    this.title = title;
    return this;
  }

   /**
   * Get title
   * @return title
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getTitle() {
    return title;
  }


  public void setTitle(String title) {
    this.title = title;
  }


  public DocumentTypeStatsData fieldsCount(Integer fieldsCount) {
    
    this.fieldsCount = fieldsCount;
    return this;
  }

   /**
   * Get fieldsCount
   * @return fieldsCount
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getFieldsCount() {
    return fieldsCount;
  }


  public void setFieldsCount(Integer fieldsCount) {
    this.fieldsCount = fieldsCount;
  }


  public DocumentTypeStatsData detectorsCount(Integer detectorsCount) {
    
    this.detectorsCount = detectorsCount;
    return this;
  }

   /**
   * Get detectorsCount
   * @return detectorsCount
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getDetectorsCount() {
    return detectorsCount;
  }


  public void setDetectorsCount(Integer detectorsCount) {
    this.detectorsCount = detectorsCount;
  }


  public DocumentTypeStatsData hideUntilPythonCount(Integer hideUntilPythonCount) {
    
    this.hideUntilPythonCount = hideUntilPythonCount;
    return this;
  }

   /**
   * Get hideUntilPythonCount
   * @return hideUntilPythonCount
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getHideUntilPythonCount() {
    return hideUntilPythonCount;
  }


  public void setHideUntilPythonCount(Integer hideUntilPythonCount) {
    this.hideUntilPythonCount = hideUntilPythonCount;
  }


  public DocumentTypeStatsData hiddenAlwaysCount(Integer hiddenAlwaysCount) {
    
    this.hiddenAlwaysCount = hiddenAlwaysCount;
    return this;
  }

   /**
   * Get hiddenAlwaysCount
   * @return hiddenAlwaysCount
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getHiddenAlwaysCount() {
    return hiddenAlwaysCount;
  }


  public void setHiddenAlwaysCount(Integer hiddenAlwaysCount) {
    this.hiddenAlwaysCount = hiddenAlwaysCount;
  }


  public DocumentTypeStatsData hideUntilPythonPcnt(BigDecimal hideUntilPythonPcnt) {
    
    this.hideUntilPythonPcnt = hideUntilPythonPcnt;
    return this;
  }

   /**
   * Get hideUntilPythonPcnt
   * @return hideUntilPythonPcnt
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getHideUntilPythonPcnt() {
    return hideUntilPythonPcnt;
  }


  public void setHideUntilPythonPcnt(BigDecimal hideUntilPythonPcnt) {
    this.hideUntilPythonPcnt = hideUntilPythonPcnt;
  }


  public DocumentTypeStatsData hiddenAlwaysPcnt(BigDecimal hiddenAlwaysPcnt) {
    
    this.hiddenAlwaysPcnt = hiddenAlwaysPcnt;
    return this;
  }

   /**
   * Get hiddenAlwaysPcnt
   * @return hiddenAlwaysPcnt
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getHiddenAlwaysPcnt() {
    return hiddenAlwaysPcnt;
  }


  public void setHiddenAlwaysPcnt(BigDecimal hiddenAlwaysPcnt) {
    this.hiddenAlwaysPcnt = hiddenAlwaysPcnt;
  }


   /**
   * Get fieldsData
   * @return fieldsData
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public List<Object> getFieldsData() {
    return fieldsData;
  }




  public DocumentTypeStatsData detectorDisabledCount(BigDecimal detectorDisabledCount) {
    
    this.detectorDisabledCount = detectorDisabledCount;
    return this;
  }

   /**
   * Get detectorDisabledCount
   * @return detectorDisabledCount
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDetectorDisabledCount() {
    return detectorDisabledCount;
  }


  public void setDetectorDisabledCount(BigDecimal detectorDisabledCount) {
    this.detectorDisabledCount = detectorDisabledCount;
  }


  public DocumentTypeStatsData detectorDisabledPcnt(BigDecimal detectorDisabledPcnt) {
    
    this.detectorDisabledPcnt = detectorDisabledPcnt;
    return this;
  }

   /**
   * Get detectorDisabledPcnt
   * @return detectorDisabledPcnt
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDetectorDisabledPcnt() {
    return detectorDisabledPcnt;
  }


  public void setDetectorDisabledPcnt(BigDecimal detectorDisabledPcnt) {
    this.detectorDisabledPcnt = detectorDisabledPcnt;
  }


  public DocumentTypeStatsData detectorUseRegexpsOnlyCount(BigDecimal detectorUseRegexpsOnlyCount) {
    
    this.detectorUseRegexpsOnlyCount = detectorUseRegexpsOnlyCount;
    return this;
  }

   /**
   * Get detectorUseRegexpsOnlyCount
   * @return detectorUseRegexpsOnlyCount
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDetectorUseRegexpsOnlyCount() {
    return detectorUseRegexpsOnlyCount;
  }


  public void setDetectorUseRegexpsOnlyCount(BigDecimal detectorUseRegexpsOnlyCount) {
    this.detectorUseRegexpsOnlyCount = detectorUseRegexpsOnlyCount;
  }


  public DocumentTypeStatsData detectorUseRegexpsOnlyPcnt(BigDecimal detectorUseRegexpsOnlyPcnt) {
    
    this.detectorUseRegexpsOnlyPcnt = detectorUseRegexpsOnlyPcnt;
    return this;
  }

   /**
   * Get detectorUseRegexpsOnlyPcnt
   * @return detectorUseRegexpsOnlyPcnt
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDetectorUseRegexpsOnlyPcnt() {
    return detectorUseRegexpsOnlyPcnt;
  }


  public void setDetectorUseRegexpsOnlyPcnt(BigDecimal detectorUseRegexpsOnlyPcnt) {
    this.detectorUseRegexpsOnlyPcnt = detectorUseRegexpsOnlyPcnt;
  }


  public DocumentTypeStatsData detectorUseFormulaOnlyCount(BigDecimal detectorUseFormulaOnlyCount) {
    
    this.detectorUseFormulaOnlyCount = detectorUseFormulaOnlyCount;
    return this;
  }

   /**
   * Get detectorUseFormulaOnlyCount
   * @return detectorUseFormulaOnlyCount
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDetectorUseFormulaOnlyCount() {
    return detectorUseFormulaOnlyCount;
  }


  public void setDetectorUseFormulaOnlyCount(BigDecimal detectorUseFormulaOnlyCount) {
    this.detectorUseFormulaOnlyCount = detectorUseFormulaOnlyCount;
  }


  public DocumentTypeStatsData detectorUseFormulaOnlyPcnt(BigDecimal detectorUseFormulaOnlyPcnt) {
    
    this.detectorUseFormulaOnlyPcnt = detectorUseFormulaOnlyPcnt;
    return this;
  }

   /**
   * Get detectorUseFormulaOnlyPcnt
   * @return detectorUseFormulaOnlyPcnt
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDetectorUseFormulaOnlyPcnt() {
    return detectorUseFormulaOnlyPcnt;
  }


  public void setDetectorUseFormulaOnlyPcnt(BigDecimal detectorUseFormulaOnlyPcnt) {
    this.detectorUseFormulaOnlyPcnt = detectorUseFormulaOnlyPcnt;
  }


  public DocumentTypeStatsData detectorRegexpTableCount(BigDecimal detectorRegexpTableCount) {
    
    this.detectorRegexpTableCount = detectorRegexpTableCount;
    return this;
  }

   /**
   * Get detectorRegexpTableCount
   * @return detectorRegexpTableCount
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDetectorRegexpTableCount() {
    return detectorRegexpTableCount;
  }


  public void setDetectorRegexpTableCount(BigDecimal detectorRegexpTableCount) {
    this.detectorRegexpTableCount = detectorRegexpTableCount;
  }


  public DocumentTypeStatsData detectorRegexpTablePcnt(BigDecimal detectorRegexpTablePcnt) {
    
    this.detectorRegexpTablePcnt = detectorRegexpTablePcnt;
    return this;
  }

   /**
   * Get detectorRegexpTablePcnt
   * @return detectorRegexpTablePcnt
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDetectorRegexpTablePcnt() {
    return detectorRegexpTablePcnt;
  }


  public void setDetectorRegexpTablePcnt(BigDecimal detectorRegexpTablePcnt) {
    this.detectorRegexpTablePcnt = detectorRegexpTablePcnt;
  }


  public DocumentTypeStatsData detectorTextBasedMlOnlyCount(BigDecimal detectorTextBasedMlOnlyCount) {
    
    this.detectorTextBasedMlOnlyCount = detectorTextBasedMlOnlyCount;
    return this;
  }

   /**
   * Get detectorTextBasedMlOnlyCount
   * @return detectorTextBasedMlOnlyCount
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDetectorTextBasedMlOnlyCount() {
    return detectorTextBasedMlOnlyCount;
  }


  public void setDetectorTextBasedMlOnlyCount(BigDecimal detectorTextBasedMlOnlyCount) {
    this.detectorTextBasedMlOnlyCount = detectorTextBasedMlOnlyCount;
  }


  public DocumentTypeStatsData detectorTextBasedMlOnlyPcnt(BigDecimal detectorTextBasedMlOnlyPcnt) {
    
    this.detectorTextBasedMlOnlyPcnt = detectorTextBasedMlOnlyPcnt;
    return this;
  }

   /**
   * Get detectorTextBasedMlOnlyPcnt
   * @return detectorTextBasedMlOnlyPcnt
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDetectorTextBasedMlOnlyPcnt() {
    return detectorTextBasedMlOnlyPcnt;
  }


  public void setDetectorTextBasedMlOnlyPcnt(BigDecimal detectorTextBasedMlOnlyPcnt) {
    this.detectorTextBasedMlOnlyPcnt = detectorTextBasedMlOnlyPcnt;
  }


  public DocumentTypeStatsData detectorFieldsBasedMlOnlyCount(BigDecimal detectorFieldsBasedMlOnlyCount) {
    
    this.detectorFieldsBasedMlOnlyCount = detectorFieldsBasedMlOnlyCount;
    return this;
  }

   /**
   * Get detectorFieldsBasedMlOnlyCount
   * @return detectorFieldsBasedMlOnlyCount
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDetectorFieldsBasedMlOnlyCount() {
    return detectorFieldsBasedMlOnlyCount;
  }


  public void setDetectorFieldsBasedMlOnlyCount(BigDecimal detectorFieldsBasedMlOnlyCount) {
    this.detectorFieldsBasedMlOnlyCount = detectorFieldsBasedMlOnlyCount;
  }


  public DocumentTypeStatsData detectorFieldsBasedMlOnlyPcnt(BigDecimal detectorFieldsBasedMlOnlyPcnt) {
    
    this.detectorFieldsBasedMlOnlyPcnt = detectorFieldsBasedMlOnlyPcnt;
    return this;
  }

   /**
   * Get detectorFieldsBasedMlOnlyPcnt
   * @return detectorFieldsBasedMlOnlyPcnt
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDetectorFieldsBasedMlOnlyPcnt() {
    return detectorFieldsBasedMlOnlyPcnt;
  }


  public void setDetectorFieldsBasedMlOnlyPcnt(BigDecimal detectorFieldsBasedMlOnlyPcnt) {
    this.detectorFieldsBasedMlOnlyPcnt = detectorFieldsBasedMlOnlyPcnt;
  }


  public DocumentTypeStatsData detectorFieldsBasedProbMlOnlyCount(BigDecimal detectorFieldsBasedProbMlOnlyCount) {
    
    this.detectorFieldsBasedProbMlOnlyCount = detectorFieldsBasedProbMlOnlyCount;
    return this;
  }

   /**
   * Get detectorFieldsBasedProbMlOnlyCount
   * @return detectorFieldsBasedProbMlOnlyCount
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDetectorFieldsBasedProbMlOnlyCount() {
    return detectorFieldsBasedProbMlOnlyCount;
  }


  public void setDetectorFieldsBasedProbMlOnlyCount(BigDecimal detectorFieldsBasedProbMlOnlyCount) {
    this.detectorFieldsBasedProbMlOnlyCount = detectorFieldsBasedProbMlOnlyCount;
  }


  public DocumentTypeStatsData detectorFieldsBasedProbMlOnlyPcnt(BigDecimal detectorFieldsBasedProbMlOnlyPcnt) {
    
    this.detectorFieldsBasedProbMlOnlyPcnt = detectorFieldsBasedProbMlOnlyPcnt;
    return this;
  }

   /**
   * Get detectorFieldsBasedProbMlOnlyPcnt
   * @return detectorFieldsBasedProbMlOnlyPcnt
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDetectorFieldsBasedProbMlOnlyPcnt() {
    return detectorFieldsBasedProbMlOnlyPcnt;
  }


  public void setDetectorFieldsBasedProbMlOnlyPcnt(BigDecimal detectorFieldsBasedProbMlOnlyPcnt) {
    this.detectorFieldsBasedProbMlOnlyPcnt = detectorFieldsBasedProbMlOnlyPcnt;
  }


  public DocumentTypeStatsData detectorFieldBasedRegexpsCount(BigDecimal detectorFieldBasedRegexpsCount) {
    
    this.detectorFieldBasedRegexpsCount = detectorFieldBasedRegexpsCount;
    return this;
  }

   /**
   * Get detectorFieldBasedRegexpsCount
   * @return detectorFieldBasedRegexpsCount
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDetectorFieldBasedRegexpsCount() {
    return detectorFieldBasedRegexpsCount;
  }


  public void setDetectorFieldBasedRegexpsCount(BigDecimal detectorFieldBasedRegexpsCount) {
    this.detectorFieldBasedRegexpsCount = detectorFieldBasedRegexpsCount;
  }


  public DocumentTypeStatsData detectorFieldBasedRegexpsPcnt(BigDecimal detectorFieldBasedRegexpsPcnt) {
    
    this.detectorFieldBasedRegexpsPcnt = detectorFieldBasedRegexpsPcnt;
    return this;
  }

   /**
   * Get detectorFieldBasedRegexpsPcnt
   * @return detectorFieldBasedRegexpsPcnt
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDetectorFieldBasedRegexpsPcnt() {
    return detectorFieldBasedRegexpsPcnt;
  }


  public void setDetectorFieldBasedRegexpsPcnt(BigDecimal detectorFieldBasedRegexpsPcnt) {
    this.detectorFieldBasedRegexpsPcnt = detectorFieldBasedRegexpsPcnt;
  }


  public DocumentTypeStatsData detectorMlflowModelCount(BigDecimal detectorMlflowModelCount) {
    
    this.detectorMlflowModelCount = detectorMlflowModelCount;
    return this;
  }

   /**
   * Get detectorMlflowModelCount
   * @return detectorMlflowModelCount
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDetectorMlflowModelCount() {
    return detectorMlflowModelCount;
  }


  public void setDetectorMlflowModelCount(BigDecimal detectorMlflowModelCount) {
    this.detectorMlflowModelCount = detectorMlflowModelCount;
  }


  public DocumentTypeStatsData detectorMlflowModelPcnt(BigDecimal detectorMlflowModelPcnt) {
    
    this.detectorMlflowModelPcnt = detectorMlflowModelPcnt;
    return this;
  }

   /**
   * Get detectorMlflowModelPcnt
   * @return detectorMlflowModelPcnt
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDetectorMlflowModelPcnt() {
    return detectorMlflowModelPcnt;
  }


  public void setDetectorMlflowModelPcnt(BigDecimal detectorMlflowModelPcnt) {
    this.detectorMlflowModelPcnt = detectorMlflowModelPcnt;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    DocumentTypeStatsData documentTypeStatsData = (DocumentTypeStatsData) o;
    return Objects.equals(this.uid, documentTypeStatsData.uid) &&
        Objects.equals(this.code, documentTypeStatsData.code) &&
        Objects.equals(this.title, documentTypeStatsData.title) &&
        Objects.equals(this.fieldsCount, documentTypeStatsData.fieldsCount) &&
        Objects.equals(this.detectorsCount, documentTypeStatsData.detectorsCount) &&
        Objects.equals(this.hideUntilPythonCount, documentTypeStatsData.hideUntilPythonCount) &&
        Objects.equals(this.hiddenAlwaysCount, documentTypeStatsData.hiddenAlwaysCount) &&
        Objects.equals(this.hideUntilPythonPcnt, documentTypeStatsData.hideUntilPythonPcnt) &&
        Objects.equals(this.hiddenAlwaysPcnt, documentTypeStatsData.hiddenAlwaysPcnt) &&
        Objects.equals(this.fieldsData, documentTypeStatsData.fieldsData) &&
        Objects.equals(this.detectorDisabledCount, documentTypeStatsData.detectorDisabledCount) &&
        Objects.equals(this.detectorDisabledPcnt, documentTypeStatsData.detectorDisabledPcnt) &&
        Objects.equals(this.detectorUseRegexpsOnlyCount, documentTypeStatsData.detectorUseRegexpsOnlyCount) &&
        Objects.equals(this.detectorUseRegexpsOnlyPcnt, documentTypeStatsData.detectorUseRegexpsOnlyPcnt) &&
        Objects.equals(this.detectorUseFormulaOnlyCount, documentTypeStatsData.detectorUseFormulaOnlyCount) &&
        Objects.equals(this.detectorUseFormulaOnlyPcnt, documentTypeStatsData.detectorUseFormulaOnlyPcnt) &&
        Objects.equals(this.detectorRegexpTableCount, documentTypeStatsData.detectorRegexpTableCount) &&
        Objects.equals(this.detectorRegexpTablePcnt, documentTypeStatsData.detectorRegexpTablePcnt) &&
        Objects.equals(this.detectorTextBasedMlOnlyCount, documentTypeStatsData.detectorTextBasedMlOnlyCount) &&
        Objects.equals(this.detectorTextBasedMlOnlyPcnt, documentTypeStatsData.detectorTextBasedMlOnlyPcnt) &&
        Objects.equals(this.detectorFieldsBasedMlOnlyCount, documentTypeStatsData.detectorFieldsBasedMlOnlyCount) &&
        Objects.equals(this.detectorFieldsBasedMlOnlyPcnt, documentTypeStatsData.detectorFieldsBasedMlOnlyPcnt) &&
        Objects.equals(this.detectorFieldsBasedProbMlOnlyCount, documentTypeStatsData.detectorFieldsBasedProbMlOnlyCount) &&
        Objects.equals(this.detectorFieldsBasedProbMlOnlyPcnt, documentTypeStatsData.detectorFieldsBasedProbMlOnlyPcnt) &&
        Objects.equals(this.detectorFieldBasedRegexpsCount, documentTypeStatsData.detectorFieldBasedRegexpsCount) &&
        Objects.equals(this.detectorFieldBasedRegexpsPcnt, documentTypeStatsData.detectorFieldBasedRegexpsPcnt) &&
        Objects.equals(this.detectorMlflowModelCount, documentTypeStatsData.detectorMlflowModelCount) &&
        Objects.equals(this.detectorMlflowModelPcnt, documentTypeStatsData.detectorMlflowModelPcnt);
  }

  @Override
  public int hashCode() {
    return Objects.hash(uid, code, title, fieldsCount, detectorsCount, hideUntilPythonCount, hiddenAlwaysCount, hideUntilPythonPcnt, hiddenAlwaysPcnt, fieldsData, detectorDisabledCount, detectorDisabledPcnt, detectorUseRegexpsOnlyCount, detectorUseRegexpsOnlyPcnt, detectorUseFormulaOnlyCount, detectorUseFormulaOnlyPcnt, detectorRegexpTableCount, detectorRegexpTablePcnt, detectorTextBasedMlOnlyCount, detectorTextBasedMlOnlyPcnt, detectorFieldsBasedMlOnlyCount, detectorFieldsBasedMlOnlyPcnt, detectorFieldsBasedProbMlOnlyCount, detectorFieldsBasedProbMlOnlyPcnt, detectorFieldBasedRegexpsCount, detectorFieldBasedRegexpsPcnt, detectorMlflowModelCount, detectorMlflowModelPcnt);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class DocumentTypeStatsData {\n");
    sb.append("    uid: ").append(toIndentedString(uid)).append("\n");
    sb.append("    code: ").append(toIndentedString(code)).append("\n");
    sb.append("    title: ").append(toIndentedString(title)).append("\n");
    sb.append("    fieldsCount: ").append(toIndentedString(fieldsCount)).append("\n");
    sb.append("    detectorsCount: ").append(toIndentedString(detectorsCount)).append("\n");
    sb.append("    hideUntilPythonCount: ").append(toIndentedString(hideUntilPythonCount)).append("\n");
    sb.append("    hiddenAlwaysCount: ").append(toIndentedString(hiddenAlwaysCount)).append("\n");
    sb.append("    hideUntilPythonPcnt: ").append(toIndentedString(hideUntilPythonPcnt)).append("\n");
    sb.append("    hiddenAlwaysPcnt: ").append(toIndentedString(hiddenAlwaysPcnt)).append("\n");
    sb.append("    fieldsData: ").append(toIndentedString(fieldsData)).append("\n");
    sb.append("    detectorDisabledCount: ").append(toIndentedString(detectorDisabledCount)).append("\n");
    sb.append("    detectorDisabledPcnt: ").append(toIndentedString(detectorDisabledPcnt)).append("\n");
    sb.append("    detectorUseRegexpsOnlyCount: ").append(toIndentedString(detectorUseRegexpsOnlyCount)).append("\n");
    sb.append("    detectorUseRegexpsOnlyPcnt: ").append(toIndentedString(detectorUseRegexpsOnlyPcnt)).append("\n");
    sb.append("    detectorUseFormulaOnlyCount: ").append(toIndentedString(detectorUseFormulaOnlyCount)).append("\n");
    sb.append("    detectorUseFormulaOnlyPcnt: ").append(toIndentedString(detectorUseFormulaOnlyPcnt)).append("\n");
    sb.append("    detectorRegexpTableCount: ").append(toIndentedString(detectorRegexpTableCount)).append("\n");
    sb.append("    detectorRegexpTablePcnt: ").append(toIndentedString(detectorRegexpTablePcnt)).append("\n");
    sb.append("    detectorTextBasedMlOnlyCount: ").append(toIndentedString(detectorTextBasedMlOnlyCount)).append("\n");
    sb.append("    detectorTextBasedMlOnlyPcnt: ").append(toIndentedString(detectorTextBasedMlOnlyPcnt)).append("\n");
    sb.append("    detectorFieldsBasedMlOnlyCount: ").append(toIndentedString(detectorFieldsBasedMlOnlyCount)).append("\n");
    sb.append("    detectorFieldsBasedMlOnlyPcnt: ").append(toIndentedString(detectorFieldsBasedMlOnlyPcnt)).append("\n");
    sb.append("    detectorFieldsBasedProbMlOnlyCount: ").append(toIndentedString(detectorFieldsBasedProbMlOnlyCount)).append("\n");
    sb.append("    detectorFieldsBasedProbMlOnlyPcnt: ").append(toIndentedString(detectorFieldsBasedProbMlOnlyPcnt)).append("\n");
    sb.append("    detectorFieldBasedRegexpsCount: ").append(toIndentedString(detectorFieldBasedRegexpsCount)).append("\n");
    sb.append("    detectorFieldBasedRegexpsPcnt: ").append(toIndentedString(detectorFieldBasedRegexpsPcnt)).append("\n");
    sb.append("    detectorMlflowModelCount: ").append(toIndentedString(detectorMlflowModelCount)).append("\n");
    sb.append("    detectorMlflowModelPcnt: ").append(toIndentedString(detectorMlflowModelPcnt)).append("\n");
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

