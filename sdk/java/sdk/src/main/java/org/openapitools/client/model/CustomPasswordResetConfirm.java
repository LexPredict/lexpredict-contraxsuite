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
 * CustomPasswordResetConfirm
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-05-07T11:20:07.445799+03:00[Europe/Moscow]")
public class CustomPasswordResetConfirm {
  public static final String SERIALIZED_NAME_NEW_PASSWORD1 = "new_password1";
  @SerializedName(SERIALIZED_NAME_NEW_PASSWORD1)
  private String newPassword1;

  public static final String SERIALIZED_NAME_NEW_PASSWORD2 = "new_password2";
  @SerializedName(SERIALIZED_NAME_NEW_PASSWORD2)
  private String newPassword2;

  public static final String SERIALIZED_NAME_UID = "uid";
  @SerializedName(SERIALIZED_NAME_UID)
  private String uid;

  public static final String SERIALIZED_NAME_TOKEN = "token";
  @SerializedName(SERIALIZED_NAME_TOKEN)
  private String token;


  public CustomPasswordResetConfirm newPassword1(String newPassword1) {
    
    this.newPassword1 = newPassword1;
    return this;
  }

   /**
   * Get newPassword1
   * @return newPassword1
  **/
  @ApiModelProperty(required = true, value = "")

  public String getNewPassword1() {
    return newPassword1;
  }


  public void setNewPassword1(String newPassword1) {
    this.newPassword1 = newPassword1;
  }


  public CustomPasswordResetConfirm newPassword2(String newPassword2) {
    
    this.newPassword2 = newPassword2;
    return this;
  }

   /**
   * Get newPassword2
   * @return newPassword2
  **/
  @ApiModelProperty(required = true, value = "")

  public String getNewPassword2() {
    return newPassword2;
  }


  public void setNewPassword2(String newPassword2) {
    this.newPassword2 = newPassword2;
  }


  public CustomPasswordResetConfirm uid(String uid) {
    
    this.uid = uid;
    return this;
  }

   /**
   * Get uid
   * @return uid
  **/
  @ApiModelProperty(required = true, value = "")

  public String getUid() {
    return uid;
  }


  public void setUid(String uid) {
    this.uid = uid;
  }


  public CustomPasswordResetConfirm token(String token) {
    
    this.token = token;
    return this;
  }

   /**
   * Get token
   * @return token
  **/
  @ApiModelProperty(required = true, value = "")

  public String getToken() {
    return token;
  }


  public void setToken(String token) {
    this.token = token;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    CustomPasswordResetConfirm customPasswordResetConfirm = (CustomPasswordResetConfirm) o;
    return Objects.equals(this.newPassword1, customPasswordResetConfirm.newPassword1) &&
        Objects.equals(this.newPassword2, customPasswordResetConfirm.newPassword2) &&
        Objects.equals(this.uid, customPasswordResetConfirm.uid) &&
        Objects.equals(this.token, customPasswordResetConfirm.token);
  }

  @Override
  public int hashCode() {
    return Objects.hash(newPassword1, newPassword2, uid, token);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class CustomPasswordResetConfirm {\n");
    sb.append("    newPassword1: ").append(toIndentedString(newPassword1)).append("\n");
    sb.append("    newPassword2: ").append(toIndentedString(newPassword2)).append("\n");
    sb.append("    uid: ").append(toIndentedString(uid)).append("\n");
    sb.append("    token: ").append(toIndentedString(token)).append("\n");
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
