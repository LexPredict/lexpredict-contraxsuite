/*
 * Contraxsuite API
 * Contraxsuite API
 *
 * The version of the OpenAPI document: 2.0.0
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

/**
 * DocumentFieldCategoryListFields
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-05-07T11:20:07.445799+03:00[Europe/Moscow]")
public class DocumentFieldCategoryListFields {
  public static final String SERIALIZED_NAME_ID = "id";
  @SerializedName(SERIALIZED_NAME_ID)
  private String id;

  public static final String SERIALIZED_NAME_CATEGORY = "category";
  @SerializedName(SERIALIZED_NAME_CATEGORY)
  private Integer category;

  public static final String SERIALIZED_NAME_CODE = "code";
  @SerializedName(SERIALIZED_NAME_CODE)
  private String code;

  public static final String SERIALIZED_NAME_TITLE = "title";
  @SerializedName(SERIALIZED_NAME_TITLE)
  private String title;

  public static final String SERIALIZED_NAME_ORDER = "order";
  @SerializedName(SERIALIZED_NAME_ORDER)
  private Integer order;


  public DocumentFieldCategoryListFields id(String id) {
    
    this.id = id;
    return this;
  }

   /**
   * Get id
   * @return id
  **/
  @ApiModelProperty(required = true, value = "")

  public String getId() {
    return id;
  }


  public void setId(String id) {
    this.id = id;
  }


  public DocumentFieldCategoryListFields category(Integer category) {
    
    this.category = category;
    return this;
  }

   /**
   * Get category
   * @return category
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getCategory() {
    return category;
  }


  public void setCategory(Integer category) {
    this.category = category;
  }


  public DocumentFieldCategoryListFields code(String code) {
    
    this.code = code;
    return this;
  }

   /**
   * Field codes must be lowercase, should start with  a Latin letter, and contain only Latin letters, digits, underscores. Field codes must be unique to every Document Type.
   * @return code
  **/
  @ApiModelProperty(required = true, value = "Field codes must be lowercase, should start with  a Latin letter, and contain only Latin letters, digits, underscores. Field codes must be unique to every Document Type.")

  public String getCode() {
    return code;
  }


  public void setCode(String code) {
    this.code = code;
  }


  public DocumentFieldCategoryListFields title(String title) {
    
    this.title = title;
    return this;
  }

   /**
   * Get title
   * @return title
  **/
  @ApiModelProperty(required = true, value = "")

  public String getTitle() {
    return title;
  }


  public void setTitle(String title) {
    this.title = title;
  }


  public DocumentFieldCategoryListFields order(Integer order) {
    
    this.order = order;
    return this;
  }

   /**
   * Get order
   * minimum: 0
   * maximum: 32767
   * @return order
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getOrder() {
    return order;
  }


  public void setOrder(Integer order) {
    this.order = order;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    DocumentFieldCategoryListFields documentFieldCategoryListFields = (DocumentFieldCategoryListFields) o;
    return Objects.equals(this.id, documentFieldCategoryListFields.id) &&
        Objects.equals(this.category, documentFieldCategoryListFields.category) &&
        Objects.equals(this.code, documentFieldCategoryListFields.code) &&
        Objects.equals(this.title, documentFieldCategoryListFields.title) &&
        Objects.equals(this.order, documentFieldCategoryListFields.order);
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, category, code, title, order);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class DocumentFieldCategoryListFields {\n");
    sb.append("    id: ").append(toIndentedString(id)).append("\n");
    sb.append("    category: ").append(toIndentedString(category)).append("\n");
    sb.append("    code: ").append(toIndentedString(code)).append("\n");
    sb.append("    title: ").append(toIndentedString(title)).append("\n");
    sb.append("    order: ").append(toIndentedString(order)).append("\n");
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
