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
import org.openapitools.client.model.SocialAccountsResponseSocialAccounts;

/**
 * SocialAccountsResponse
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-09-21T17:23:12.379447+03:00[Europe/Moscow]")
public class SocialAccountsResponse {
  public static final String SERIALIZED_NAME_SOCIAL_ACCOUNTS = "social_accounts";
  @SerializedName(SERIALIZED_NAME_SOCIAL_ACCOUNTS)
  private SocialAccountsResponseSocialAccounts socialAccounts;


  public SocialAccountsResponse socialAccounts(SocialAccountsResponseSocialAccounts socialAccounts) {
    
    this.socialAccounts = socialAccounts;
    return this;
  }

   /**
   * Get socialAccounts
   * @return socialAccounts
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public SocialAccountsResponseSocialAccounts getSocialAccounts() {
    return socialAccounts;
  }


  public void setSocialAccounts(SocialAccountsResponseSocialAccounts socialAccounts) {
    this.socialAccounts = socialAccounts;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    SocialAccountsResponse socialAccountsResponse = (SocialAccountsResponse) o;
    return Objects.equals(this.socialAccounts, socialAccountsResponse.socialAccounts);
  }

  @Override
  public int hashCode() {
    return Objects.hash(socialAccounts);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class SocialAccountsResponse {\n");
    sb.append("    socialAccounts: ").append(toIndentedString(socialAccounts)).append("\n");
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

