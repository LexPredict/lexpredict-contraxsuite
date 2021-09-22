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
 * MLModel
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-09-21T17:23:12.379447+03:00[Europe/Moscow]")
public class MLModel {
  public static final String SERIALIZED_NAME_ID = "id";
  @SerializedName(SERIALIZED_NAME_ID)
  private Integer id;

  public static final String SERIALIZED_NAME_NAME = "name";
  @SerializedName(SERIALIZED_NAME_NAME)
  private String name;

  public static final String SERIALIZED_NAME_VERSION = "version";
  @SerializedName(SERIALIZED_NAME_VERSION)
  private String version;

  public static final String SERIALIZED_NAME_VECTOR_NAME = "vector_name";
  @SerializedName(SERIALIZED_NAME_VECTOR_NAME)
  private String vectorName;

  public static final String SERIALIZED_NAME_MODEL_PATH = "model_path";
  @SerializedName(SERIALIZED_NAME_MODEL_PATH)
  private String modelPath;

  public static final String SERIALIZED_NAME_IS_ACTIVE = "is_active";
  @SerializedName(SERIALIZED_NAME_IS_ACTIVE)
  private Boolean isActive;

  public static final String SERIALIZED_NAME_DEFAULT = "default";
  @SerializedName(SERIALIZED_NAME_DEFAULT)
  private Boolean _default;

  /**
   * Should the model be applied to documents or text units
   */
  @JsonAdapter(ApplyToEnum.Adapter.class)
  public enum ApplyToEnum {
    DOCUMENT("document"),
    
    TEXT_UNIT("text_unit");

    private String value;

    ApplyToEnum(String value) {
      this.value = value;
    }

    public String getValue() {
      return value;
    }

    @Override
    public String toString() {
      return String.valueOf(value);
    }

    public static ApplyToEnum fromValue(String value) {
      for (ApplyToEnum b : ApplyToEnum.values()) {
        if (b.value.equals(value)) {
          return b;
        }
      }
      return null;
    }

    public static class Adapter extends TypeAdapter<ApplyToEnum> {
      @Override
      public void write(final JsonWriter jsonWriter, final ApplyToEnum enumeration) throws IOException {
        jsonWriter.value(enumeration.getValue());
      }

      @Override
      public ApplyToEnum read(final JsonReader jsonReader) throws IOException {
        String value =  jsonReader.nextString();
        return ApplyToEnum.fromValue(value);
      }
    }
  }

  public static final String SERIALIZED_NAME_APPLY_TO = "apply_to";
  @SerializedName(SERIALIZED_NAME_APPLY_TO)
  private ApplyToEnum applyTo;

  /**
   * The model class
   */
  @JsonAdapter(TargetEntityEnum.Adapter.class)
  public enum TargetEntityEnum {
    TRANSFORMER("transformer"),
    
    CLASSIFIER("classifier"),
    
    CONTRACT_TYPE_CLASSIFIER("contract_type_classifier"),
    
    IS_CONTRACT("is_contract");

    private String value;

    TargetEntityEnum(String value) {
      this.value = value;
    }

    public String getValue() {
      return value;
    }

    @Override
    public String toString() {
      return String.valueOf(value);
    }

    public static TargetEntityEnum fromValue(String value) {
      for (TargetEntityEnum b : TargetEntityEnum.values()) {
        if (b.value.equals(value)) {
          return b;
        }
      }
      return null;
    }

    public static class Adapter extends TypeAdapter<TargetEntityEnum> {
      @Override
      public void write(final JsonWriter jsonWriter, final TargetEntityEnum enumeration) throws IOException {
        jsonWriter.value(enumeration.getValue());
      }

      @Override
      public TargetEntityEnum read(final JsonReader jsonReader) throws IOException {
        String value =  jsonReader.nextString();
        return TargetEntityEnum.fromValue(value);
      }
    }
  }

  public static final String SERIALIZED_NAME_TARGET_ENTITY = "target_entity";
  @SerializedName(SERIALIZED_NAME_TARGET_ENTITY)
  private TargetEntityEnum targetEntity;

  public static final String SERIALIZED_NAME_LANGUAGE = "language";
  @SerializedName(SERIALIZED_NAME_LANGUAGE)
  private String language;

  /**
   * Text unit type: sentence or paragraph
   */
  @JsonAdapter(TextUnitTypeEnum.Adapter.class)
  public enum TextUnitTypeEnum {
    SENTENCE("sentence"),
    
    PARAGRAPH("paragraph");

    private String value;

    TextUnitTypeEnum(String value) {
      this.value = value;
    }

    public String getValue() {
      return value;
    }

    @Override
    public String toString() {
      return String.valueOf(value);
    }

    public static TextUnitTypeEnum fromValue(String value) {
      for (TextUnitTypeEnum b : TextUnitTypeEnum.values()) {
        if (b.value.equals(value)) {
          return b;
        }
      }
      return null;
    }

    public static class Adapter extends TypeAdapter<TextUnitTypeEnum> {
      @Override
      public void write(final JsonWriter jsonWriter, final TextUnitTypeEnum enumeration) throws IOException {
        jsonWriter.value(enumeration.getValue());
      }

      @Override
      public TextUnitTypeEnum read(final JsonReader jsonReader) throws IOException {
        String value =  jsonReader.nextString();
        return TextUnitTypeEnum.fromValue(value);
      }
    }
  }

  public static final String SERIALIZED_NAME_TEXT_UNIT_TYPE = "text_unit_type";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_TYPE)
  private TextUnitTypeEnum textUnitType;

  public static final String SERIALIZED_NAME_CODEBASE_VERSION = "codebase_version";
  @SerializedName(SERIALIZED_NAME_CODEBASE_VERSION)
  private String codebaseVersion;

  public static final String SERIALIZED_NAME_USER_MODIFIED = "user_modified";
  @SerializedName(SERIALIZED_NAME_USER_MODIFIED)
  private Boolean userModified;

  public static final String SERIALIZED_NAME_PROJECT = "project";
  @SerializedName(SERIALIZED_NAME_PROJECT)
  private Integer project;


   /**
   * Get id
   * @return id
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getId() {
    return id;
  }




  public MLModel name(String name) {
    
    this.name = name;
    return this;
  }

   /**
   * Model name, may include module parameters
   * @return name
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "Model name, may include module parameters")

  public String getName() {
    return name;
  }


  public void setName(String name) {
    this.name = name;
  }


  public MLModel version(String version) {
    
    this.version = version;
    return this;
  }

   /**
   * Model version
   * @return version
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "Model version")

  public String getVersion() {
    return version;
  }


  public void setVersion(String version) {
    this.version = version;
  }


  public MLModel vectorName(String vectorName) {
    
    this.vectorName = vectorName;
    return this;
  }

   /**
   * Get vectorName
   * @return vectorName
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getVectorName() {
    return vectorName;
  }


  public void setVectorName(String vectorName) {
    this.vectorName = vectorName;
  }


  public MLModel modelPath(String modelPath) {
    
    this.modelPath = modelPath;
    return this;
  }

   /**
   * Model path, relative to WebDAV root folder
   * @return modelPath
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "Model path, relative to WebDAV root folder")

  public String getModelPath() {
    return modelPath;
  }


  public void setModelPath(String modelPath) {
    this.modelPath = modelPath;
  }


  public MLModel isActive(Boolean isActive) {
    
    this.isActive = isActive;
    return this;
  }

   /**
   * Inactive models are ignored
   * @return isActive
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "Inactive models are ignored")

  public Boolean getIsActive() {
    return isActive;
  }


  public void setIsActive(Boolean isActive) {
    this.isActive = isActive;
  }


  public MLModel _default(Boolean _default) {
    
    this._default = _default;
    return this;
  }

   /**
   * The default model is used unless another model is deliberately selected
   * @return _default
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "The default model is used unless another model is deliberately selected")

  public Boolean getDefault() {
    return _default;
  }


  public void setDefault(Boolean _default) {
    this._default = _default;
  }


  public MLModel applyTo(ApplyToEnum applyTo) {
    
    this.applyTo = applyTo;
    return this;
  }

   /**
   * Should the model be applied to documents or text units
   * @return applyTo
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(required = true, value = "Should the model be applied to documents or text units")

  public ApplyToEnum getApplyTo() {
    return applyTo;
  }


  public void setApplyTo(ApplyToEnum applyTo) {
    this.applyTo = applyTo;
  }


  public MLModel targetEntity(TargetEntityEnum targetEntity) {
    
    this.targetEntity = targetEntity;
    return this;
  }

   /**
   * The model class
   * @return targetEntity
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(required = true, value = "The model class")

  public TargetEntityEnum getTargetEntity() {
    return targetEntity;
  }


  public void setTargetEntity(TargetEntityEnum targetEntity) {
    this.targetEntity = targetEntity;
  }


  public MLModel language(String language) {
    
    this.language = language;
    return this;
  }

   /**
   * Language (ISO 693-1) code, may be omitted
   * @return language
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(required = true, value = "Language (ISO 693-1) code, may be omitted")

  public String getLanguage() {
    return language;
  }


  public void setLanguage(String language) {
    this.language = language;
  }


  public MLModel textUnitType(TextUnitTypeEnum textUnitType) {
    
    this.textUnitType = textUnitType;
    return this;
  }

   /**
   * Text unit type: sentence or paragraph
   * @return textUnitType
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "Text unit type: sentence or paragraph")

  public TextUnitTypeEnum getTextUnitType() {
    return textUnitType;
  }


  public void setTextUnitType(TextUnitTypeEnum textUnitType) {
    this.textUnitType = textUnitType;
  }


  public MLModel codebaseVersion(String codebaseVersion) {
    
    this.codebaseVersion = codebaseVersion;
    return this;
  }

   /**
   * ContraxSuite version in which the model was created
   * @return codebaseVersion
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "ContraxSuite version in which the model was created")

  public String getCodebaseVersion() {
    return codebaseVersion;
  }


  public void setCodebaseVersion(String codebaseVersion) {
    this.codebaseVersion = codebaseVersion;
  }


  public MLModel userModified(Boolean userModified) {
    
    this.userModified = userModified;
    return this;
  }

   /**
   * User modified models are not automatically updated
   * @return userModified
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "User modified models are not automatically updated")

  public Boolean getUserModified() {
    return userModified;
  }


  public void setUserModified(Boolean userModified) {
    this.userModified = userModified;
  }


  public MLModel project(Integer project) {
    
    this.project = project;
    return this;
  }

   /**
   * Optional project reference
   * @return project
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "Optional project reference")

  public Integer getProject() {
    return project;
  }


  public void setProject(Integer project) {
    this.project = project;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    MLModel mlModel = (MLModel) o;
    return Objects.equals(this.id, mlModel.id) &&
        Objects.equals(this.name, mlModel.name) &&
        Objects.equals(this.version, mlModel.version) &&
        Objects.equals(this.vectorName, mlModel.vectorName) &&
        Objects.equals(this.modelPath, mlModel.modelPath) &&
        Objects.equals(this.isActive, mlModel.isActive) &&
        Objects.equals(this._default, mlModel._default) &&
        Objects.equals(this.applyTo, mlModel.applyTo) &&
        Objects.equals(this.targetEntity, mlModel.targetEntity) &&
        Objects.equals(this.language, mlModel.language) &&
        Objects.equals(this.textUnitType, mlModel.textUnitType) &&
        Objects.equals(this.codebaseVersion, mlModel.codebaseVersion) &&
        Objects.equals(this.userModified, mlModel.userModified) &&
        Objects.equals(this.project, mlModel.project);
  }

  private static <T> boolean equalsNullable(JsonNullable<T> a, JsonNullable<T> b) {
    return a == b || (a != null && b != null && a.isPresent() && b.isPresent() && a.get().getClass().isArray() ? Arrays.equals((T[])a.get(), (T[])b.get()) : Objects.equals(a.get(), b.get()));
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, name, version, vectorName, modelPath, isActive, _default, applyTo, targetEntity, language, textUnitType, codebaseVersion, userModified, project);
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
    sb.append("class MLModel {\n");
    sb.append("    id: ").append(toIndentedString(id)).append("\n");
    sb.append("    name: ").append(toIndentedString(name)).append("\n");
    sb.append("    version: ").append(toIndentedString(version)).append("\n");
    sb.append("    vectorName: ").append(toIndentedString(vectorName)).append("\n");
    sb.append("    modelPath: ").append(toIndentedString(modelPath)).append("\n");
    sb.append("    isActive: ").append(toIndentedString(isActive)).append("\n");
    sb.append("    _default: ").append(toIndentedString(_default)).append("\n");
    sb.append("    applyTo: ").append(toIndentedString(applyTo)).append("\n");
    sb.append("    targetEntity: ").append(toIndentedString(targetEntity)).append("\n");
    sb.append("    language: ").append(toIndentedString(language)).append("\n");
    sb.append("    textUnitType: ").append(toIndentedString(textUnitType)).append("\n");
    sb.append("    codebaseVersion: ").append(toIndentedString(codebaseVersion)).append("\n");
    sb.append("    userModified: ").append(toIndentedString(userModified)).append("\n");
    sb.append("    project: ").append(toIndentedString(project)).append("\n");
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

