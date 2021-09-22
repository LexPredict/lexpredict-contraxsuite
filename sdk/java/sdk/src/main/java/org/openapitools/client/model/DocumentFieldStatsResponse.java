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
 * DocumentFieldStatsResponse
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-09-21T17:23:12.379447+03:00[Europe/Moscow]")
public class DocumentFieldStatsResponse {
  public static final String SERIALIZED_NAME_CODE = "code";
  @SerializedName(SERIALIZED_NAME_CODE)
  private String code;

  public static final String SERIALIZED_NAME_TITLE = "title";
  @SerializedName(SERIALIZED_NAME_TITLE)
  private String title;

  public static final String SERIALIZED_NAME_TOTAL = "total";
  @SerializedName(SERIALIZED_NAME_TOTAL)
  private Integer total;

  public static final String SERIALIZED_NAME_TODO = "todo";
  @SerializedName(SERIALIZED_NAME_TODO)
  private Integer todo;

  public static final String SERIALIZED_NAME_SYS_GENERATED_CONFIRM_CORRECT = "sys_generated_confirm_correct";
  @SerializedName(SERIALIZED_NAME_SYS_GENERATED_CONFIRM_CORRECT)
  private Integer sysGeneratedConfirmCorrect;

  public static final String SERIALIZED_NAME_REJECTED = "rejected";
  @SerializedName(SERIALIZED_NAME_REJECTED)
  private Integer rejected;

  public static final String SERIALIZED_NAME_USER_GENERATED = "user_generated";
  @SerializedName(SERIALIZED_NAME_USER_GENERATED)
  private Integer userGenerated;

  public static final String SERIALIZED_NAME_DEPS_ON_FIELDS = "deps_on_fields";
  @SerializedName(SERIALIZED_NAME_DEPS_ON_FIELDS)
  private List<String> depsOnFields = new ArrayList<String>();


  public DocumentFieldStatsResponse code(String code) {
    
    this.code = code;
    return this;
  }

   /**
   * Get code
   * @return code
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getCode() {
    return code;
  }


  public void setCode(String code) {
    this.code = code;
  }


  public DocumentFieldStatsResponse title(String title) {
    
    this.title = title;
    return this;
  }

   /**
   * Get title
   * @return title
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getTitle() {
    return title;
  }


  public void setTitle(String title) {
    this.title = title;
  }


  public DocumentFieldStatsResponse total(Integer total) {
    
    this.total = total;
    return this;
  }

   /**
   * Get total
   * @return total
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getTotal() {
    return total;
  }


  public void setTotal(Integer total) {
    this.total = total;
  }


  public DocumentFieldStatsResponse todo(Integer todo) {
    
    this.todo = todo;
    return this;
  }

   /**
   * Get todo
   * @return todo
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getTodo() {
    return todo;
  }


  public void setTodo(Integer todo) {
    this.todo = todo;
  }


  public DocumentFieldStatsResponse sysGeneratedConfirmCorrect(Integer sysGeneratedConfirmCorrect) {
    
    this.sysGeneratedConfirmCorrect = sysGeneratedConfirmCorrect;
    return this;
  }

   /**
   * Get sysGeneratedConfirmCorrect
   * @return sysGeneratedConfirmCorrect
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getSysGeneratedConfirmCorrect() {
    return sysGeneratedConfirmCorrect;
  }


  public void setSysGeneratedConfirmCorrect(Integer sysGeneratedConfirmCorrect) {
    this.sysGeneratedConfirmCorrect = sysGeneratedConfirmCorrect;
  }


  public DocumentFieldStatsResponse rejected(Integer rejected) {
    
    this.rejected = rejected;
    return this;
  }

   /**
   * Get rejected
   * @return rejected
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getRejected() {
    return rejected;
  }


  public void setRejected(Integer rejected) {
    this.rejected = rejected;
  }


  public DocumentFieldStatsResponse userGenerated(Integer userGenerated) {
    
    this.userGenerated = userGenerated;
    return this;
  }

   /**
   * Get userGenerated
   * @return userGenerated
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getUserGenerated() {
    return userGenerated;
  }


  public void setUserGenerated(Integer userGenerated) {
    this.userGenerated = userGenerated;
  }


  public DocumentFieldStatsResponse depsOnFields(List<String> depsOnFields) {
    
    this.depsOnFields = depsOnFields;
    return this;
  }

  public DocumentFieldStatsResponse addDepsOnFieldsItem(String depsOnFieldsItem) {
    this.depsOnFields.add(depsOnFieldsItem);
    return this;
  }

   /**
   * Get depsOnFields
   * @return depsOnFields
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public List<String> getDepsOnFields() {
    return depsOnFields;
  }


  public void setDepsOnFields(List<String> depsOnFields) {
    this.depsOnFields = depsOnFields;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    DocumentFieldStatsResponse documentFieldStatsResponse = (DocumentFieldStatsResponse) o;
    return Objects.equals(this.code, documentFieldStatsResponse.code) &&
        Objects.equals(this.title, documentFieldStatsResponse.title) &&
        Objects.equals(this.total, documentFieldStatsResponse.total) &&
        Objects.equals(this.todo, documentFieldStatsResponse.todo) &&
        Objects.equals(this.sysGeneratedConfirmCorrect, documentFieldStatsResponse.sysGeneratedConfirmCorrect) &&
        Objects.equals(this.rejected, documentFieldStatsResponse.rejected) &&
        Objects.equals(this.userGenerated, documentFieldStatsResponse.userGenerated) &&
        Objects.equals(this.depsOnFields, documentFieldStatsResponse.depsOnFields);
  }

  @Override
  public int hashCode() {
    return Objects.hash(code, title, total, todo, sysGeneratedConfirmCorrect, rejected, userGenerated, depsOnFields);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class DocumentFieldStatsResponse {\n");
    sb.append("    code: ").append(toIndentedString(code)).append("\n");
    sb.append("    title: ").append(toIndentedString(title)).append("\n");
    sb.append("    total: ").append(toIndentedString(total)).append("\n");
    sb.append("    todo: ").append(toIndentedString(todo)).append("\n");
    sb.append("    sysGeneratedConfirmCorrect: ").append(toIndentedString(sysGeneratedConfirmCorrect)).append("\n");
    sb.append("    rejected: ").append(toIndentedString(rejected)).append("\n");
    sb.append("    userGenerated: ").append(toIndentedString(userGenerated)).append("\n");
    sb.append("    depsOnFields: ").append(toIndentedString(depsOnFields)).append("\n");
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

