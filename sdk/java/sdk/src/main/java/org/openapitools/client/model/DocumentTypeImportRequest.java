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
import java.io.File;
import java.io.IOException;

/**
 * DocumentTypeImportRequest
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2022-01-19T15:46:46.101102+03:00[Europe/Moscow]")
public class DocumentTypeImportRequest {
  public static final String SERIALIZED_NAME_FILE = "file";
  @SerializedName(SERIALIZED_NAME_FILE)
  private File file;

  public static final String SERIALIZED_NAME_UPDATE_CACHE = "update_cache";
  @SerializedName(SERIALIZED_NAME_UPDATE_CACHE)
  private Boolean updateCache;

  /**
   * Gets or Sets action
   */
  @JsonAdapter(ActionEnum.Adapter.class)
  public enum ActionEnum {
    VALIDATE("validate"),
    
    VALIDATE_IMPORT("validate|import"),
    
    IMPORT_AUTO_FIX_RETAIN_MISSING_OBJECTS("import|auto_fix|retain_missing_objects"),
    
    IMPORT_AUTO_FIX_REMOVE_MISSING_OBJECTS("import|auto_fix|remove_missing_objects");

    private String value;

    ActionEnum(String value) {
      this.value = value;
    }

    public String getValue() {
      return value;
    }

    @Override
    public String toString() {
      return String.valueOf(value);
    }

    public static ActionEnum fromValue(String value) {
      for (ActionEnum b : ActionEnum.values()) {
        if (b.value.equals(value)) {
          return b;
        }
      }
      throw new IllegalArgumentException("Unexpected value '" + value + "'");
    }

    public static class Adapter extends TypeAdapter<ActionEnum> {
      @Override
      public void write(final JsonWriter jsonWriter, final ActionEnum enumeration) throws IOException {
        jsonWriter.value(enumeration.getValue());
      }

      @Override
      public ActionEnum read(final JsonReader jsonReader) throws IOException {
        String value =  jsonReader.nextString();
        return ActionEnum.fromValue(value);
      }
    }
  }

  public static final String SERIALIZED_NAME_ACTION = "action";
  @SerializedName(SERIALIZED_NAME_ACTION)
  private ActionEnum action;

  public static final String SERIALIZED_NAME_SOURCE_VERSION = "source_version";
  @SerializedName(SERIALIZED_NAME_SOURCE_VERSION)
  private String sourceVersion;

  public DocumentTypeImportRequest() { 
  }

  public DocumentTypeImportRequest file(File file) {
    
    this.file = file;
    return this;
  }

   /**
   * Get file
   * @return file
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public File getFile() {
    return file;
  }


  public void setFile(File file) {
    this.file = file;
  }


  public DocumentTypeImportRequest updateCache(Boolean updateCache) {
    
    this.updateCache = updateCache;
    return this;
  }

   /**
   * Get updateCache
   * @return updateCache
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Boolean getUpdateCache() {
    return updateCache;
  }


  public void setUpdateCache(Boolean updateCache) {
    this.updateCache = updateCache;
  }


  public DocumentTypeImportRequest action(ActionEnum action) {
    
    this.action = action;
    return this;
  }

   /**
   * Get action
   * @return action
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public ActionEnum getAction() {
    return action;
  }


  public void setAction(ActionEnum action) {
    this.action = action;
  }


  public DocumentTypeImportRequest sourceVersion(String sourceVersion) {
    
    this.sourceVersion = sourceVersion;
    return this;
  }

   /**
   * Get sourceVersion
   * @return sourceVersion
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getSourceVersion() {
    return sourceVersion;
  }


  public void setSourceVersion(String sourceVersion) {
    this.sourceVersion = sourceVersion;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    DocumentTypeImportRequest documentTypeImportRequest = (DocumentTypeImportRequest) o;
    return Objects.equals(this.file, documentTypeImportRequest.file) &&
        Objects.equals(this.updateCache, documentTypeImportRequest.updateCache) &&
        Objects.equals(this.action, documentTypeImportRequest.action) &&
        Objects.equals(this.sourceVersion, documentTypeImportRequest.sourceVersion);
  }

  @Override
  public int hashCode() {
    return Objects.hash(file, updateCache, action, sourceVersion);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class DocumentTypeImportRequest {\n");
    sb.append("    file: ").append(toIndentedString(file)).append("\n");
    sb.append("    updateCache: ").append(toIndentedString(updateCache)).append("\n");
    sb.append("    action: ").append(toIndentedString(action)).append("\n");
    sb.append("    sourceVersion: ").append(toIndentedString(sourceVersion)).append("\n");
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

