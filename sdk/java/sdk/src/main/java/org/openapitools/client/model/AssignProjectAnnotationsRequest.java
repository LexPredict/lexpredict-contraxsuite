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
import java.util.ArrayList;
import java.util.List;
import org.openapitools.jackson.nullable.JsonNullable;

/**
 * AssignProjectAnnotationsRequest
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-09-21T17:23:12.379447+03:00[Europe/Moscow]")
public class AssignProjectAnnotationsRequest {
  public static final String SERIALIZED_NAME_ASSIGNEE_ID = "assignee_id";
  @SerializedName(SERIALIZED_NAME_ASSIGNEE_ID)
  private Integer assigneeId;

  public static final String SERIALIZED_NAME_ALL = "all";
  @SerializedName(SERIALIZED_NAME_ALL)
  private Boolean all;

  public static final String SERIALIZED_NAME_ANNOTATION_IDS = "annotation_ids";
  @SerializedName(SERIALIZED_NAME_ANNOTATION_IDS)
  private List<Integer> annotationIds = null;

  public static final String SERIALIZED_NAME_NO_ANNOTATION_IDS = "no_annotation_ids";
  @SerializedName(SERIALIZED_NAME_NO_ANNOTATION_IDS)
  private List<Integer> noAnnotationIds = null;


  public AssignProjectAnnotationsRequest assigneeId(Integer assigneeId) {
    
    this.assigneeId = assigneeId;
    return this;
  }

   /**
   * Get assigneeId
   * @return assigneeId
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getAssigneeId() {
    return assigneeId;
  }


  public void setAssigneeId(Integer assigneeId) {
    this.assigneeId = assigneeId;
  }


  public AssignProjectAnnotationsRequest all(Boolean all) {
    
    this.all = all;
    return this;
  }

   /**
   * Get all
   * @return all
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Boolean getAll() {
    return all;
  }


  public void setAll(Boolean all) {
    this.all = all;
  }


  public AssignProjectAnnotationsRequest annotationIds(List<Integer> annotationIds) {
    
    this.annotationIds = annotationIds;
    return this;
  }

  public AssignProjectAnnotationsRequest addAnnotationIdsItem(Integer annotationIdsItem) {
    if (this.annotationIds == null) {
      this.annotationIds = new ArrayList<Integer>();
    }
    this.annotationIds.add(annotationIdsItem);
    return this;
  }

   /**
   * Get annotationIds
   * @return annotationIds
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public List<Integer> getAnnotationIds() {
    return annotationIds;
  }


  public void setAnnotationIds(List<Integer> annotationIds) {
    this.annotationIds = annotationIds;
  }


  public AssignProjectAnnotationsRequest noAnnotationIds(List<Integer> noAnnotationIds) {
    
    this.noAnnotationIds = noAnnotationIds;
    return this;
  }

  public AssignProjectAnnotationsRequest addNoAnnotationIdsItem(Integer noAnnotationIdsItem) {
    if (this.noAnnotationIds == null) {
      this.noAnnotationIds = new ArrayList<Integer>();
    }
    this.noAnnotationIds.add(noAnnotationIdsItem);
    return this;
  }

   /**
   * Get noAnnotationIds
   * @return noAnnotationIds
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public List<Integer> getNoAnnotationIds() {
    return noAnnotationIds;
  }


  public void setNoAnnotationIds(List<Integer> noAnnotationIds) {
    this.noAnnotationIds = noAnnotationIds;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    AssignProjectAnnotationsRequest assignProjectAnnotationsRequest = (AssignProjectAnnotationsRequest) o;
    return Objects.equals(this.assigneeId, assignProjectAnnotationsRequest.assigneeId) &&
        Objects.equals(this.all, assignProjectAnnotationsRequest.all) &&
        Objects.equals(this.annotationIds, assignProjectAnnotationsRequest.annotationIds) &&
        Objects.equals(this.noAnnotationIds, assignProjectAnnotationsRequest.noAnnotationIds);
  }

  private static <T> boolean equalsNullable(JsonNullable<T> a, JsonNullable<T> b) {
    return a == b || (a != null && b != null && a.isPresent() && b.isPresent() && a.get().getClass().isArray() ? Arrays.equals((T[])a.get(), (T[])b.get()) : Objects.equals(a.get(), b.get()));
  }

  @Override
  public int hashCode() {
    return Objects.hash(assigneeId, all, annotationIds, noAnnotationIds);
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
    sb.append("class AssignProjectAnnotationsRequest {\n");
    sb.append("    assigneeId: ").append(toIndentedString(assigneeId)).append("\n");
    sb.append("    all: ").append(toIndentedString(all)).append("\n");
    sb.append("    annotationIds: ").append(toIndentedString(annotationIds)).append("\n");
    sb.append("    noAnnotationIds: ").append(toIndentedString(noAnnotationIds)).append("\n");
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

