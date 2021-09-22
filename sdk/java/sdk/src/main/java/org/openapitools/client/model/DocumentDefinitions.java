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

/**
 * DocumentDefinitions
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-09-21T17:23:12.379447+03:00[Europe/Moscow]")
public class DocumentDefinitions {
  public static final String SERIALIZED_NAME_DEFINITION = "definition";
  @SerializedName(SERIALIZED_NAME_DEFINITION)
  private String definition;

  public static final String SERIALIZED_NAME_MATCHES = "matches";
  @SerializedName(SERIALIZED_NAME_MATCHES)
  private List<Object> matches = new ArrayList<Object>();

  public static final String SERIALIZED_NAME_DESCRIPTIONS = "descriptions";
  @SerializedName(SERIALIZED_NAME_DESCRIPTIONS)
  private List<Object> descriptions = new ArrayList<Object>();


  public DocumentDefinitions definition(String definition) {
    
    this.definition = definition;
    return this;
  }

   /**
   * Get definition
   * @return definition
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getDefinition() {
    return definition;
  }


  public void setDefinition(String definition) {
    this.definition = definition;
  }


  public DocumentDefinitions matches(List<Object> matches) {
    
    this.matches = matches;
    return this;
  }

  public DocumentDefinitions addMatchesItem(Object matchesItem) {
    this.matches.add(matchesItem);
    return this;
  }

   /**
   * Get matches
   * @return matches
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public List<Object> getMatches() {
    return matches;
  }


  public void setMatches(List<Object> matches) {
    this.matches = matches;
  }


  public DocumentDefinitions descriptions(List<Object> descriptions) {
    
    this.descriptions = descriptions;
    return this;
  }

  public DocumentDefinitions addDescriptionsItem(Object descriptionsItem) {
    this.descriptions.add(descriptionsItem);
    return this;
  }

   /**
   * Get descriptions
   * @return descriptions
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public List<Object> getDescriptions() {
    return descriptions;
  }


  public void setDescriptions(List<Object> descriptions) {
    this.descriptions = descriptions;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    DocumentDefinitions documentDefinitions = (DocumentDefinitions) o;
    return Objects.equals(this.definition, documentDefinitions.definition) &&
        Objects.equals(this.matches, documentDefinitions.matches) &&
        Objects.equals(this.descriptions, documentDefinitions.descriptions);
  }

  @Override
  public int hashCode() {
    return Objects.hash(definition, matches, descriptions);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class DocumentDefinitions {\n");
    sb.append("    definition: ").append(toIndentedString(definition)).append("\n");
    sb.append("    matches: ").append(toIndentedString(matches)).append("\n");
    sb.append("    descriptions: ").append(toIndentedString(descriptions)).append("\n");
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

