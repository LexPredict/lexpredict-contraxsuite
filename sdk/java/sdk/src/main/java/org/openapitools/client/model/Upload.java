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
import java.io.File;
import java.io.IOException;
import java.util.UUID;
import org.threeten.bp.OffsetDateTime;

/**
 * Upload
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2020-12-11T16:57:55.511+03:00[Europe/Moscow]")
public class Upload {
  public static final String SERIALIZED_NAME_ID = "id";
  @SerializedName(SERIALIZED_NAME_ID)
  private Integer id;

  public static final String SERIALIZED_NAME_GUID = "guid";
  @SerializedName(SERIALIZED_NAME_GUID)
  private UUID guid;

  public static final String SERIALIZED_NAME_STATE = "state";
  @SerializedName(SERIALIZED_NAME_STATE)
  private String state;

  public static final String SERIALIZED_NAME_UPLOAD_OFFSET = "upload_offset";
  @SerializedName(SERIALIZED_NAME_UPLOAD_OFFSET)
  private Long uploadOffset;

  public static final String SERIALIZED_NAME_UPLOAD_LENGTH = "upload_length";
  @SerializedName(SERIALIZED_NAME_UPLOAD_LENGTH)
  private Long uploadLength;

  public static final String SERIALIZED_NAME_UPLOAD_METADATA = "upload_metadata";
  @SerializedName(SERIALIZED_NAME_UPLOAD_METADATA)
  private String uploadMetadata;

  public static final String SERIALIZED_NAME_FILENAME = "filename";
  @SerializedName(SERIALIZED_NAME_FILENAME)
  private String filename;

  public static final String SERIALIZED_NAME_TEMPORARY_FILE_PATH = "temporary_file_path";
  @SerializedName(SERIALIZED_NAME_TEMPORARY_FILE_PATH)
  private String temporaryFilePath;

  public static final String SERIALIZED_NAME_EXPIRES = "expires";
  @SerializedName(SERIALIZED_NAME_EXPIRES)
  private OffsetDateTime expires;

  public static final String SERIALIZED_NAME_UPLOADED_FILE = "uploaded_file";
  @SerializedName(SERIALIZED_NAME_UPLOADED_FILE)
  private File uploadedFile;


   /**
   * Get id
   * @return id
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getId() {
    return id;
  }




  public Upload guid(UUID guid) {
    
    this.guid = guid;
    return this;
  }

   /**
   * Get guid
   * @return guid
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public UUID getGuid() {
    return guid;
  }


  public void setGuid(UUID guid) {
    this.guid = guid;
  }


  public Upload state(String state) {
    
    this.state = state;
    return this;
  }

   /**
   * Get state
   * @return state
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getState() {
    return state;
  }


  public void setState(String state) {
    this.state = state;
  }


  public Upload uploadOffset(Long uploadOffset) {
    
    this.uploadOffset = uploadOffset;
    return this;
  }

   /**
   * Get uploadOffset
   * minimum: -9223372036854775808
   * maximum: 9223372036854775807
   * @return uploadOffset
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Long getUploadOffset() {
    return uploadOffset;
  }


  public void setUploadOffset(Long uploadOffset) {
    this.uploadOffset = uploadOffset;
  }


  public Upload uploadLength(Long uploadLength) {
    
    this.uploadLength = uploadLength;
    return this;
  }

   /**
   * Get uploadLength
   * minimum: -9223372036854775808
   * maximum: 9223372036854775807
   * @return uploadLength
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Long getUploadLength() {
    return uploadLength;
  }


  public void setUploadLength(Long uploadLength) {
    this.uploadLength = uploadLength;
  }


  public Upload uploadMetadata(String uploadMetadata) {
    
    this.uploadMetadata = uploadMetadata;
    return this;
  }

   /**
   * Get uploadMetadata
   * @return uploadMetadata
  **/
  @ApiModelProperty(required = true, value = "")

  public String getUploadMetadata() {
    return uploadMetadata;
  }


  public void setUploadMetadata(String uploadMetadata) {
    this.uploadMetadata = uploadMetadata;
  }


  public Upload filename(String filename) {
    
    this.filename = filename;
    return this;
  }

   /**
   * Get filename
   * @return filename
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getFilename() {
    return filename;
  }


  public void setFilename(String filename) {
    this.filename = filename;
  }


  public Upload temporaryFilePath(String temporaryFilePath) {
    
    this.temporaryFilePath = temporaryFilePath;
    return this;
  }

   /**
   * Get temporaryFilePath
   * @return temporaryFilePath
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getTemporaryFilePath() {
    return temporaryFilePath;
  }


  public void setTemporaryFilePath(String temporaryFilePath) {
    this.temporaryFilePath = temporaryFilePath;
  }


  public Upload expires(OffsetDateTime expires) {
    
    this.expires = expires;
    return this;
  }

   /**
   * Get expires
   * @return expires
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public OffsetDateTime getExpires() {
    return expires;
  }


  public void setExpires(OffsetDateTime expires) {
    this.expires = expires;
  }


  public Upload uploadedFile(File uploadedFile) {
    
    this.uploadedFile = uploadedFile;
    return this;
  }

   /**
   * Get uploadedFile
   * @return uploadedFile
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public File getUploadedFile() {
    return uploadedFile;
  }


  public void setUploadedFile(File uploadedFile) {
    this.uploadedFile = uploadedFile;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    Upload upload = (Upload) o;
    return Objects.equals(this.id, upload.id) &&
        Objects.equals(this.guid, upload.guid) &&
        Objects.equals(this.state, upload.state) &&
        Objects.equals(this.uploadOffset, upload.uploadOffset) &&
        Objects.equals(this.uploadLength, upload.uploadLength) &&
        Objects.equals(this.uploadMetadata, upload.uploadMetadata) &&
        Objects.equals(this.filename, upload.filename) &&
        Objects.equals(this.temporaryFilePath, upload.temporaryFilePath) &&
        Objects.equals(this.expires, upload.expires) &&
        Objects.equals(this.uploadedFile, upload.uploadedFile);
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, guid, state, uploadOffset, uploadLength, uploadMetadata, filename, temporaryFilePath, expires, uploadedFile);
  }


  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class Upload {\n");
    sb.append("    id: ").append(toIndentedString(id)).append("\n");
    sb.append("    guid: ").append(toIndentedString(guid)).append("\n");
    sb.append("    state: ").append(toIndentedString(state)).append("\n");
    sb.append("    uploadOffset: ").append(toIndentedString(uploadOffset)).append("\n");
    sb.append("    uploadLength: ").append(toIndentedString(uploadLength)).append("\n");
    sb.append("    uploadMetadata: ").append(toIndentedString(uploadMetadata)).append("\n");
    sb.append("    filename: ").append(toIndentedString(filename)).append("\n");
    sb.append("    temporaryFilePath: ").append(toIndentedString(temporaryFilePath)).append("\n");
    sb.append("    expires: ").append(toIndentedString(expires)).append("\n");
    sb.append("    uploadedFile: ").append(toIndentedString(uploadedFile)).append("\n");
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

