/*
 * Contraxsuite API
 * Contraxsuite API
 *
 * The version of the OpenAPI document: 2.3.0
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

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonDeserializer;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import com.google.gson.TypeAdapterFactory;
import com.google.gson.reflect.TypeToken;

import java.lang.reflect.Type;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

import org.openapitools.client.JSON;

/**
 * ProjectDocumentSimilarityResponseDataInner
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2022-06-16T11:43:26.677726+03:00[Europe/Moscow]")
public class ProjectDocumentSimilarityResponseDataInner {
  public static final String SERIALIZED_NAME_DOCUMENT_A_NAME = "document_a_name";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_A_NAME)
  private String documentAName;

  public static final String SERIALIZED_NAME_DOCUMENT_A_ID = "document_a_id";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_A_ID)
  private String documentAId;

  public static final String SERIALIZED_NAME_DOCUMENT_B_NAME = "document_b_name";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_B_NAME)
  private String documentBName;

  public static final String SERIALIZED_NAME_DOCUMENT_B_ID = "document_b_id";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_B_ID)
  private String documentBId;

  public static final String SERIALIZED_NAME_DOCUMENT_B_TEXT = "document_b_text";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_B_TEXT)
  private String documentBText;

  public static final String SERIALIZED_NAME_SIMILARITY = "similarity";
  @SerializedName(SERIALIZED_NAME_SIMILARITY)
  private BigDecimal similarity;

  public static final String SERIALIZED_NAME_RUN_ID = "run_id";
  @SerializedName(SERIALIZED_NAME_RUN_ID)
  private String runId;

  public ProjectDocumentSimilarityResponseDataInner() { 
  }

  
  public ProjectDocumentSimilarityResponseDataInner(
     String documentAId, 
     String documentBId, 
     String runId
  ) {
    this();
    this.documentAId = documentAId;
    this.documentBId = documentBId;
    this.runId = runId;
  }

  public ProjectDocumentSimilarityResponseDataInner documentAName(String documentAName) {
    
    this.documentAName = documentAName;
    return this;
  }

   /**
   * Get documentAName
   * @return documentAName
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getDocumentAName() {
    return documentAName;
  }


  public void setDocumentAName(String documentAName) {
    this.documentAName = documentAName;
  }


   /**
   * Get documentAId
   * @return documentAId
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getDocumentAId() {
    return documentAId;
  }




  public ProjectDocumentSimilarityResponseDataInner documentBName(String documentBName) {
    
    this.documentBName = documentBName;
    return this;
  }

   /**
   * Get documentBName
   * @return documentBName
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getDocumentBName() {
    return documentBName;
  }


  public void setDocumentBName(String documentBName) {
    this.documentBName = documentBName;
  }


   /**
   * Get documentBId
   * @return documentBId
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getDocumentBId() {
    return documentBId;
  }




  public ProjectDocumentSimilarityResponseDataInner documentBText(String documentBText) {
    
    this.documentBText = documentBText;
    return this;
  }

   /**
   * Get documentBText
   * @return documentBText
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getDocumentBText() {
    return documentBText;
  }


  public void setDocumentBText(String documentBText) {
    this.documentBText = documentBText;
  }


  public ProjectDocumentSimilarityResponseDataInner similarity(BigDecimal similarity) {
    
    this.similarity = similarity;
    return this;
  }

   /**
   * Get similarity
   * @return similarity
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getSimilarity() {
    return similarity;
  }


  public void setSimilarity(BigDecimal similarity) {
    this.similarity = similarity;
  }


   /**
   * Get runId
   * @return runId
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getRunId() {
    return runId;
  }





  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    ProjectDocumentSimilarityResponseDataInner projectDocumentSimilarityResponseDataInner = (ProjectDocumentSimilarityResponseDataInner) o;
    return Objects.equals(this.documentAName, projectDocumentSimilarityResponseDataInner.documentAName) &&
        Objects.equals(this.documentAId, projectDocumentSimilarityResponseDataInner.documentAId) &&
        Objects.equals(this.documentBName, projectDocumentSimilarityResponseDataInner.documentBName) &&
        Objects.equals(this.documentBId, projectDocumentSimilarityResponseDataInner.documentBId) &&
        Objects.equals(this.documentBText, projectDocumentSimilarityResponseDataInner.documentBText) &&
        Objects.equals(this.similarity, projectDocumentSimilarityResponseDataInner.similarity) &&
        Objects.equals(this.runId, projectDocumentSimilarityResponseDataInner.runId);
  }

  @Override
  public int hashCode() {
    return Objects.hash(documentAName, documentAId, documentBName, documentBId, documentBText, similarity, runId);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class ProjectDocumentSimilarityResponseDataInner {\n");
    sb.append("    documentAName: ").append(toIndentedString(documentAName)).append("\n");
    sb.append("    documentAId: ").append(toIndentedString(documentAId)).append("\n");
    sb.append("    documentBName: ").append(toIndentedString(documentBName)).append("\n");
    sb.append("    documentBId: ").append(toIndentedString(documentBId)).append("\n");
    sb.append("    documentBText: ").append(toIndentedString(documentBText)).append("\n");
    sb.append("    similarity: ").append(toIndentedString(similarity)).append("\n");
    sb.append("    runId: ").append(toIndentedString(runId)).append("\n");
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


  public static HashSet<String> openapiFields;
  public static HashSet<String> openapiRequiredFields;

  static {
    // a set of all properties/fields (JSON key names)
    openapiFields = new HashSet<String>();
    openapiFields.add("document_a_name");
    openapiFields.add("document_a_id");
    openapiFields.add("document_b_name");
    openapiFields.add("document_b_id");
    openapiFields.add("document_b_text");
    openapiFields.add("similarity");
    openapiFields.add("run_id");

    // a set of required properties/fields (JSON key names)
    openapiRequiredFields = new HashSet<String>();
    openapiRequiredFields.add("document_a_name");
    openapiRequiredFields.add("document_b_name");
    openapiRequiredFields.add("document_b_text");
    openapiRequiredFields.add("similarity");
  }

 /**
  * Validates the JSON Object and throws an exception if issues found
  *
  * @param jsonObj JSON Object
  * @throws IOException if the JSON Object is invalid with respect to ProjectDocumentSimilarityResponseDataInner
  */
  public static void validateJsonObject(JsonObject jsonObj) throws IOException {
      if (jsonObj == null) {
        if (ProjectDocumentSimilarityResponseDataInner.openapiRequiredFields.isEmpty()) {
          return;
        } else { // has required fields
          throw new IllegalArgumentException(String.format("The required field(s) %s in ProjectDocumentSimilarityResponseDataInner is not found in the empty JSON string", ProjectDocumentSimilarityResponseDataInner.openapiRequiredFields.toString()));
        }
      }

      Set<Entry<String, JsonElement>> entries = jsonObj.entrySet();
      // check to see if the JSON string contains additional fields
      for (Entry<String, JsonElement> entry : entries) {
        if (!ProjectDocumentSimilarityResponseDataInner.openapiFields.contains(entry.getKey())) {
          throw new IllegalArgumentException(String.format("The field `%s` in the JSON string is not defined in the `ProjectDocumentSimilarityResponseDataInner` properties. JSON: %s", entry.getKey(), jsonObj.toString()));
        }
      }

      // check to make sure all required properties/fields are present in the JSON string
      for (String requiredField : ProjectDocumentSimilarityResponseDataInner.openapiRequiredFields) {
        if (jsonObj.get(requiredField) == null) {
          throw new IllegalArgumentException(String.format("The required field `%s` is not found in the JSON string: %s", requiredField, jsonObj.toString()));
        }
      }
      if (jsonObj.get("document_a_name") != null && !jsonObj.get("document_a_name").isJsonPrimitive()) {
        throw new IllegalArgumentException(String.format("Expected the field `document_a_name` to be a primitive type in the JSON string but got `%s`", jsonObj.get("document_a_name").toString()));
      }
      if (jsonObj.get("document_a_id") != null && !jsonObj.get("document_a_id").isJsonPrimitive()) {
        throw new IllegalArgumentException(String.format("Expected the field `document_a_id` to be a primitive type in the JSON string but got `%s`", jsonObj.get("document_a_id").toString()));
      }
      if (jsonObj.get("document_b_name") != null && !jsonObj.get("document_b_name").isJsonPrimitive()) {
        throw new IllegalArgumentException(String.format("Expected the field `document_b_name` to be a primitive type in the JSON string but got `%s`", jsonObj.get("document_b_name").toString()));
      }
      if (jsonObj.get("document_b_id") != null && !jsonObj.get("document_b_id").isJsonPrimitive()) {
        throw new IllegalArgumentException(String.format("Expected the field `document_b_id` to be a primitive type in the JSON string but got `%s`", jsonObj.get("document_b_id").toString()));
      }
      if (jsonObj.get("document_b_text") != null && !jsonObj.get("document_b_text").isJsonPrimitive()) {
        throw new IllegalArgumentException(String.format("Expected the field `document_b_text` to be a primitive type in the JSON string but got `%s`", jsonObj.get("document_b_text").toString()));
      }
      if (jsonObj.get("similarity") != null && !jsonObj.get("similarity").isJsonPrimitive()) {
        throw new IllegalArgumentException(String.format("Expected the field `similarity` to be a primitive type in the JSON string but got `%s`", jsonObj.get("similarity").toString()));
      }
      if (jsonObj.get("run_id") != null && !jsonObj.get("run_id").isJsonPrimitive()) {
        throw new IllegalArgumentException(String.format("Expected the field `run_id` to be a primitive type in the JSON string but got `%s`", jsonObj.get("run_id").toString()));
      }
  }

  public static class CustomTypeAdapterFactory implements TypeAdapterFactory {
    @SuppressWarnings("unchecked")
    @Override
    public <T> TypeAdapter<T> create(Gson gson, TypeToken<T> type) {
       if (!ProjectDocumentSimilarityResponseDataInner.class.isAssignableFrom(type.getRawType())) {
         return null; // this class only serializes 'ProjectDocumentSimilarityResponseDataInner' and its subtypes
       }
       final TypeAdapter<JsonElement> elementAdapter = gson.getAdapter(JsonElement.class);
       final TypeAdapter<ProjectDocumentSimilarityResponseDataInner> thisAdapter
                        = gson.getDelegateAdapter(this, TypeToken.get(ProjectDocumentSimilarityResponseDataInner.class));

       return (TypeAdapter<T>) new TypeAdapter<ProjectDocumentSimilarityResponseDataInner>() {
           @Override
           public void write(JsonWriter out, ProjectDocumentSimilarityResponseDataInner value) throws IOException {
             JsonObject obj = thisAdapter.toJsonTree(value).getAsJsonObject();
             elementAdapter.write(out, obj);
           }

           @Override
           public ProjectDocumentSimilarityResponseDataInner read(JsonReader in) throws IOException {
             JsonObject jsonObj = elementAdapter.read(in).getAsJsonObject();
             validateJsonObject(jsonObj);
             return thisAdapter.fromJsonTree(jsonObj);
           }

       }.nullSafe();
    }
  }

 /**
  * Create an instance of ProjectDocumentSimilarityResponseDataInner given an JSON string
  *
  * @param jsonString JSON string
  * @return An instance of ProjectDocumentSimilarityResponseDataInner
  * @throws IOException if the JSON string is invalid with respect to ProjectDocumentSimilarityResponseDataInner
  */
  public static ProjectDocumentSimilarityResponseDataInner fromJson(String jsonString) throws IOException {
    return JSON.getGson().fromJson(jsonString, ProjectDocumentSimilarityResponseDataInner.class);
  }

 /**
  * Convert an instance of ProjectDocumentSimilarityResponseDataInner to an JSON string
  *
  * @return JSON string
  */
  public String toJson() {
    return JSON.getGson().toJson(this);
  }
}
