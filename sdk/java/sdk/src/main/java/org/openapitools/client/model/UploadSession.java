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
import java.util.UUID;

/**
 * UploadSession
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2020-12-11T16:57:55.511+03:00[Europe/Moscow]")
public class UploadSession {
  public static final String SERIALIZED_NAME_UID = "uid";
  @SerializedName(SERIALIZED_NAME_UID)
  private UUID uid;

  public static final String SERIALIZED_NAME_PROJECT = "project";
  @SerializedName(SERIALIZED_NAME_PROJECT)
  private Integer project;

  public static final String SERIALIZED_NAME_CREATED_BY = "created_by";
  @SerializedName(SERIALIZED_NAME_CREATED_BY)
  private Integer createdBy;

  public static final String SERIALIZED_NAME_UPLOAD_FILES = "upload_files";
  @SerializedName(SERIALIZED_NAME_UPLOAD_FILES)
  private Object uploadFiles;

  public static final String SERIALIZED_NAME_REVIEW_FILES = "review_files";
  @SerializedName(SERIALIZED_NAME_REVIEW_FILES)
  private Boolean reviewFiles;

  public static final String SERIALIZED_NAME_FORCE = "force";
  @SerializedName(SERIALIZED_NAME_FORCE)
  private Boolean force;


   /**
   * Get uid
   * @return uid
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public UUID getUid() {
    return uid;
  }




  public UploadSession project(Integer project) {
    
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


  public UploadSession createdBy(Integer createdBy) {
    
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
   * Get uploadFiles
   * @return uploadFiles
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Object getUploadFiles() {
    return uploadFiles;
  }




   /**
   * Get reviewFiles
   * @return reviewFiles
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Boolean getReviewFiles() {
    return reviewFiles;
  }




   /**
   * Get force
   * @return force
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Boolean getForce() {
    return force;
  }




  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    UploadSession uploadSession = (UploadSession) o;
    return Objects.equals(this.uid, uploadSession.uid) &&
        Objects.equals(this.project, uploadSession.project) &&
        Objects.equals(this.createdBy, uploadSession.createdBy) &&
        Objects.equals(this.uploadFiles, uploadSession.uploadFiles) &&
        Objects.equals(this.reviewFiles, uploadSession.reviewFiles) &&
        Objects.equals(this.force, uploadSession.force);
  }

  @Override
  public int hashCode() {
    return Objects.hash(uid, project, createdBy, uploadFiles, reviewFiles, force);
  }


  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class UploadSession {\n");
    sb.append("    uid: ").append(toIndentedString(uid)).append("\n");
    sb.append("    project: ").append(toIndentedString(project)).append("\n");
    sb.append("    createdBy: ").append(toIndentedString(createdBy)).append("\n");
    sb.append("    uploadFiles: ").append(toIndentedString(uploadFiles)).append("\n");
    sb.append("    reviewFiles: ").append(toIndentedString(reviewFiles)).append("\n");
    sb.append("    force: ").append(toIndentedString(force)).append("\n");
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

