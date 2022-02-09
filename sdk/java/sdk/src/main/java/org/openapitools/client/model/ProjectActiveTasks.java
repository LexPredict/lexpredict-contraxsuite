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
import org.openapitools.client.model.ProjectActiveTasksTasks;

/**
 * ProjectActiveTasks
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2022-01-19T15:46:46.101102+03:00[Europe/Moscow]")
public class ProjectActiveTasks {
  public static final String SERIALIZED_NAME_TASKS = "tasks";
  @SerializedName(SERIALIZED_NAME_TASKS)
  private ProjectActiveTasksTasks tasks;

  public static final String SERIALIZED_NAME_DOCUMENT_TRANSFORMER_CHANGE_IN_PROGRESS = "document_transformer_change_in_progress";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_TRANSFORMER_CHANGE_IN_PROGRESS)
  private Boolean documentTransformerChangeInProgress;

  public static final String SERIALIZED_NAME_TEXT_UNIT_TRANSFORMER_CHANGE_IN_PROGRESS = "text_unit_transformer_change_in_progress";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_TRANSFORMER_CHANGE_IN_PROGRESS)
  private Boolean textUnitTransformerChangeInProgress;

  public static final String SERIALIZED_NAME_LOCATE_TERMS_IN_PROGRESS = "locate_terms_in_progress";
  @SerializedName(SERIALIZED_NAME_LOCATE_TERMS_IN_PROGRESS)
  private Boolean locateTermsInProgress;

  public static final String SERIALIZED_NAME_LOCATE_COMPANIES_IN_PROGRESS = "locate_companies_in_progress";
  @SerializedName(SERIALIZED_NAME_LOCATE_COMPANIES_IN_PROGRESS)
  private Boolean locateCompaniesInProgress;

  public ProjectActiveTasks() { 
  }

  public ProjectActiveTasks tasks(ProjectActiveTasksTasks tasks) {
    
    this.tasks = tasks;
    return this;
  }

   /**
   * Get tasks
   * @return tasks
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public ProjectActiveTasksTasks getTasks() {
    return tasks;
  }


  public void setTasks(ProjectActiveTasksTasks tasks) {
    this.tasks = tasks;
  }


  public ProjectActiveTasks documentTransformerChangeInProgress(Boolean documentTransformerChangeInProgress) {
    
    this.documentTransformerChangeInProgress = documentTransformerChangeInProgress;
    return this;
  }

   /**
   * Get documentTransformerChangeInProgress
   * @return documentTransformerChangeInProgress
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Boolean getDocumentTransformerChangeInProgress() {
    return documentTransformerChangeInProgress;
  }


  public void setDocumentTransformerChangeInProgress(Boolean documentTransformerChangeInProgress) {
    this.documentTransformerChangeInProgress = documentTransformerChangeInProgress;
  }


  public ProjectActiveTasks textUnitTransformerChangeInProgress(Boolean textUnitTransformerChangeInProgress) {
    
    this.textUnitTransformerChangeInProgress = textUnitTransformerChangeInProgress;
    return this;
  }

   /**
   * Get textUnitTransformerChangeInProgress
   * @return textUnitTransformerChangeInProgress
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Boolean getTextUnitTransformerChangeInProgress() {
    return textUnitTransformerChangeInProgress;
  }


  public void setTextUnitTransformerChangeInProgress(Boolean textUnitTransformerChangeInProgress) {
    this.textUnitTransformerChangeInProgress = textUnitTransformerChangeInProgress;
  }


  public ProjectActiveTasks locateTermsInProgress(Boolean locateTermsInProgress) {
    
    this.locateTermsInProgress = locateTermsInProgress;
    return this;
  }

   /**
   * Get locateTermsInProgress
   * @return locateTermsInProgress
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Boolean getLocateTermsInProgress() {
    return locateTermsInProgress;
  }


  public void setLocateTermsInProgress(Boolean locateTermsInProgress) {
    this.locateTermsInProgress = locateTermsInProgress;
  }


  public ProjectActiveTasks locateCompaniesInProgress(Boolean locateCompaniesInProgress) {
    
    this.locateCompaniesInProgress = locateCompaniesInProgress;
    return this;
  }

   /**
   * Get locateCompaniesInProgress
   * @return locateCompaniesInProgress
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Boolean getLocateCompaniesInProgress() {
    return locateCompaniesInProgress;
  }


  public void setLocateCompaniesInProgress(Boolean locateCompaniesInProgress) {
    this.locateCompaniesInProgress = locateCompaniesInProgress;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    ProjectActiveTasks projectActiveTasks = (ProjectActiveTasks) o;
    return Objects.equals(this.tasks, projectActiveTasks.tasks) &&
        Objects.equals(this.documentTransformerChangeInProgress, projectActiveTasks.documentTransformerChangeInProgress) &&
        Objects.equals(this.textUnitTransformerChangeInProgress, projectActiveTasks.textUnitTransformerChangeInProgress) &&
        Objects.equals(this.locateTermsInProgress, projectActiveTasks.locateTermsInProgress) &&
        Objects.equals(this.locateCompaniesInProgress, projectActiveTasks.locateCompaniesInProgress);
  }

  @Override
  public int hashCode() {
    return Objects.hash(tasks, documentTransformerChangeInProgress, textUnitTransformerChangeInProgress, locateTermsInProgress, locateCompaniesInProgress);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class ProjectActiveTasks {\n");
    sb.append("    tasks: ").append(toIndentedString(tasks)).append("\n");
    sb.append("    documentTransformerChangeInProgress: ").append(toIndentedString(documentTransformerChangeInProgress)).append("\n");
    sb.append("    textUnitTransformerChangeInProgress: ").append(toIndentedString(textUnitTransformerChangeInProgress)).append("\n");
    sb.append("    locateTermsInProgress: ").append(toIndentedString(locateTermsInProgress)).append("\n");
    sb.append("    locateCompaniesInProgress: ").append(toIndentedString(locateCompaniesInProgress)).append("\n");
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

