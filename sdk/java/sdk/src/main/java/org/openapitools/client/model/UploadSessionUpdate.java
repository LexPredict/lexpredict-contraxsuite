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
 * UploadSessionUpdate
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-09-21T17:23:12.379447+03:00[Europe/Moscow]")
public class UploadSessionUpdate {
  public static final String SERIALIZED_NAME_PK = "pk";
  @SerializedName(SERIALIZED_NAME_PK)
  private UUID pk;

  public static final String SERIALIZED_NAME_PROJECT = "project";
  @SerializedName(SERIALIZED_NAME_PROJECT)
  private Integer project;

  public static final String SERIALIZED_NAME_CREATED_BY = "created_by";
  @SerializedName(SERIALIZED_NAME_CREATED_BY)
  private Integer createdBy;

  public static final String SERIALIZED_NAME_CREATED_DATE = "created_date";
  @SerializedName(SERIALIZED_NAME_CREATED_DATE)
  private OffsetDateTime createdDate;

  public static final String SERIALIZED_NAME_COMPLETED = "completed";
  @SerializedName(SERIALIZED_NAME_COMPLETED)
  private Boolean completed;


   /**
   * Get pk
   * @return pk
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public UUID getPk() {
    return pk;
  }




  public UploadSessionUpdate project(Integer project) {
    
    this.project = project;
    return this;
  }

   /**
   * Get project
   * @return project
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getProject() {
    return project;
  }


  public void setProject(Integer project) {
    this.project = project;
  }


  public UploadSessionUpdate createdBy(Integer createdBy) {
    
    this.createdBy = createdBy;
    return this;
  }

   /**
   * Get createdBy
   * @return createdBy
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getCreatedBy() {
    return createdBy;
  }


  public void setCreatedBy(Integer createdBy) {
    this.createdBy = createdBy;
  }


   /**
   * Get createdDate
   * @return createdDate
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public OffsetDateTime getCreatedDate() {
    return createdDate;
  }




  public UploadSessionUpdate completed(Boolean completed) {
    
    this.completed = completed;
    return this;
  }

   /**
   * Get completed
   * @return completed
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Boolean getCompleted() {
    return completed;
  }


  public void setCompleted(Boolean completed) {
    this.completed = completed;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    UploadSessionUpdate uploadSessionUpdate = (UploadSessionUpdate) o;
    return Objects.equals(this.pk, uploadSessionUpdate.pk) &&
        Objects.equals(this.project, uploadSessionUpdate.project) &&
        Objects.equals(this.createdBy, uploadSessionUpdate.createdBy) &&
        Objects.equals(this.createdDate, uploadSessionUpdate.createdDate) &&
        Objects.equals(this.completed, uploadSessionUpdate.completed);
  }

  private static <T> boolean equalsNullable(JsonNullable<T> a, JsonNullable<T> b) {
    return a == b || (a != null && b != null && a.isPresent() && b.isPresent() && a.get().getClass().isArray() ? Arrays.equals((T[])a.get(), (T[])b.get()) : Objects.equals(a.get(), b.get()));
  }

  @Override
  public int hashCode() {
    return Objects.hash(pk, project, createdBy, createdDate, completed);
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
    sb.append("class UploadSessionUpdate {\n");
    sb.append("    pk: ").append(toIndentedString(pk)).append("\n");
    sb.append("    project: ").append(toIndentedString(project)).append("\n");
    sb.append("    createdBy: ").append(toIndentedString(createdBy)).append("\n");
    sb.append("    createdDate: ").append(toIndentedString(createdDate)).append("\n");
    sb.append("    completed: ").append(toIndentedString(completed)).append("\n");
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

