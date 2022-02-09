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
import java.io.IOException;
import org.openapitools.jackson.nullable.JsonNullable;
import org.threeten.bp.OffsetDateTime;

/**
 * Action
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2022-01-19T15:46:46.101102+03:00[Europe/Moscow]")
public class Action {
  public static final String SERIALIZED_NAME_ID = "id";
  @SerializedName(SERIALIZED_NAME_ID)
  private Integer id;

  public static final String SERIALIZED_NAME_NAME = "name";
  @SerializedName(SERIALIZED_NAME_NAME)
  private String name;

  public static final String SERIALIZED_NAME_MESSAGE = "message";
  @SerializedName(SERIALIZED_NAME_MESSAGE)
  private String message;

  public static final String SERIALIZED_NAME_VIEW_ACTION = "view_action";
  @SerializedName(SERIALIZED_NAME_VIEW_ACTION)
  private String viewAction;

  public static final String SERIALIZED_NAME_OBJECT_PK = "object_pk";
  @SerializedName(SERIALIZED_NAME_OBJECT_PK)
  private String objectPk;

  public static final String SERIALIZED_NAME_MODEL_NAME = "model_name";
  @SerializedName(SERIALIZED_NAME_MODEL_NAME)
  private String modelName;

  public static final String SERIALIZED_NAME_DATE = "date";
  @SerializedName(SERIALIZED_NAME_DATE)
  private OffsetDateTime date;

  public static final String SERIALIZED_NAME_USER_NAME = "user__name";
  @SerializedName(SERIALIZED_NAME_USER_NAME)
  private String userName;

  public static final String SERIALIZED_NAME_USER_INITIALS = "user__initials";
  @SerializedName(SERIALIZED_NAME_USER_INITIALS)
  private String userInitials;

  public static final String SERIALIZED_NAME_USER_PHOTO_URL = "user_photo_url";
  @SerializedName(SERIALIZED_NAME_USER_PHOTO_URL)
  private String userPhotoUrl;

  public static final String SERIALIZED_NAME_REQUEST_DATA = "request_data";
  @SerializedName(SERIALIZED_NAME_REQUEST_DATA)
  private Object requestData;

  public Action() { 
  }

  
  public Action(
     Integer id, 
     OffsetDateTime date, 
     String userName, 
     String userInitials, 
     String userPhotoUrl
  ) {
    this();
    this.id = id;
    this.date = date;
    this.userName = userName;
    this.userInitials = userInitials;
    this.userPhotoUrl = userPhotoUrl;
  }

   /**
   * Get id
   * @return id
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getId() {
    return id;
  }




  public Action name(String name) {
    
    this.name = name;
    return this;
  }

   /**
   * Get name
   * @return name
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getName() {
    return name;
  }


  public void setName(String name) {
    this.name = name;
  }


  public Action message(String message) {
    
    this.message = message;
    return this;
  }

   /**
   * Get message
   * @return message
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getMessage() {
    return message;
  }


  public void setMessage(String message) {
    this.message = message;
  }


  public Action viewAction(String viewAction) {
    
    this.viewAction = viewAction;
    return this;
  }

   /**
   * Get viewAction
   * @return viewAction
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getViewAction() {
    return viewAction;
  }


  public void setViewAction(String viewAction) {
    this.viewAction = viewAction;
  }


  public Action objectPk(String objectPk) {
    
    this.objectPk = objectPk;
    return this;
  }

   /**
   * Get objectPk
   * @return objectPk
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getObjectPk() {
    return objectPk;
  }


  public void setObjectPk(String objectPk) {
    this.objectPk = objectPk;
  }


  public Action modelName(String modelName) {
    
    this.modelName = modelName;
    return this;
  }

   /**
   * Get modelName
   * @return modelName
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getModelName() {
    return modelName;
  }


  public void setModelName(String modelName) {
    this.modelName = modelName;
  }


   /**
   * Get date
   * @return date
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public OffsetDateTime getDate() {
    return date;
  }




   /**
   * Get userName
   * @return userName
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getUserName() {
    return userName;
  }




   /**
   * Get userInitials
   * @return userInitials
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getUserInitials() {
    return userInitials;
  }




   /**
   * Get userPhotoUrl
   * @return userPhotoUrl
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getUserPhotoUrl() {
    return userPhotoUrl;
  }




  public Action requestData(Object requestData) {
    
    this.requestData = requestData;
    return this;
  }

   /**
   * Get requestData
   * @return requestData
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Object getRequestData() {
    return requestData;
  }


  public void setRequestData(Object requestData) {
    this.requestData = requestData;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    Action action = (Action) o;
    return Objects.equals(this.id, action.id) &&
        Objects.equals(this.name, action.name) &&
        Objects.equals(this.message, action.message) &&
        Objects.equals(this.viewAction, action.viewAction) &&
        Objects.equals(this.objectPk, action.objectPk) &&
        Objects.equals(this.modelName, action.modelName) &&
        Objects.equals(this.date, action.date) &&
        Objects.equals(this.userName, action.userName) &&
        Objects.equals(this.userInitials, action.userInitials) &&
        Objects.equals(this.userPhotoUrl, action.userPhotoUrl) &&
        Objects.equals(this.requestData, action.requestData);
  }

  private static <T> boolean equalsNullable(JsonNullable<T> a, JsonNullable<T> b) {
    return a == b || (a != null && b != null && a.isPresent() && b.isPresent() && Objects.deepEquals(a.get(), b.get()));
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, name, message, viewAction, objectPk, modelName, date, userName, userInitials, userPhotoUrl, requestData);
  }

  private static <T> int hashCodeNullable(JsonNullable<T> a) {
    if (a == null) {
      return 1;
    }
    return a.isPresent() ? Arrays.deepHashCode(new Object[]{a.get()}) : 31;
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class Action {\n");
    sb.append("    id: ").append(toIndentedString(id)).append("\n");
    sb.append("    name: ").append(toIndentedString(name)).append("\n");
    sb.append("    message: ").append(toIndentedString(message)).append("\n");
    sb.append("    viewAction: ").append(toIndentedString(viewAction)).append("\n");
    sb.append("    objectPk: ").append(toIndentedString(objectPk)).append("\n");
    sb.append("    modelName: ").append(toIndentedString(modelName)).append("\n");
    sb.append("    date: ").append(toIndentedString(date)).append("\n");
    sb.append("    userName: ").append(toIndentedString(userName)).append("\n");
    sb.append("    userInitials: ").append(toIndentedString(userInitials)).append("\n");
    sb.append("    userPhotoUrl: ").append(toIndentedString(userPhotoUrl)).append("\n");
    sb.append("    requestData: ").append(toIndentedString(requestData)).append("\n");
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

