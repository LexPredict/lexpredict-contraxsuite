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
 * WebNotificationDetailNotification
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2022-01-19T15:46:46.101102+03:00[Europe/Moscow]")
public class WebNotificationDetailNotification {
  public static final String SERIALIZED_NAME_ID = "id";
  @SerializedName(SERIALIZED_NAME_ID)
  private Integer id;

  public static final String SERIALIZED_NAME_MESSAGE_DATA = "message_data";
  @SerializedName(SERIALIZED_NAME_MESSAGE_DATA)
  private Object messageData;

  public static final String SERIALIZED_NAME_MESSAGE_TEMPLATE = "message_template";
  @SerializedName(SERIALIZED_NAME_MESSAGE_TEMPLATE)
  private String messageTemplate;

  public static final String SERIALIZED_NAME_CREATED_DATE = "created_date";
  @SerializedName(SERIALIZED_NAME_CREATED_DATE)
  private OffsetDateTime createdDate;

  /**
   * Notification type
   */
  @JsonAdapter(NotificationTypeEnum.Adapter.class)
  public enum NotificationTypeEnum {
    DOCUMENT_ASSIGNED("DOCUMENT_ASSIGNED"),
    
    DOCUMENT_UNASSIGNED("DOCUMENT_UNASSIGNED"),
    
    CLAUSES_ASSIGNED("CLAUSES_ASSIGNED"),
    
    CLAUSES_UNASSIGNED("CLAUSES_UNASSIGNED"),
    
    DOCUMENTS_UPLOADED("DOCUMENTS_UPLOADED"),
    
    DOCUMENT_DELETED("DOCUMENT_DELETED"),
    
    DOCUMENT_ADDED("DOCUMENT_ADDED"),
    
    DOCUMENT_STATUS_CHANGED("DOCUMENT_STATUS_CHANGED"),
    
    CLUSTER_IMPORTED("CLUSTER_IMPORTED"),
    
    FIELD_VALUE_DETECTION_COMPLETED("FIELD_VALUE_DETECTION_COMPLETED"),
    
    CUSTOM_TERM_SET_SEARCH_FINISHED("CUSTOM_TERM_SET_SEARCH_FINISHED"),
    
    CUSTOM_COMPANY_TYPE_SEARCH_FINISHED("CUSTOM_COMPANY_TYPE_SEARCH_FINISHED"),
    
    DOCUMENT_SIMILARITY_SEARCH_FINISHED("DOCUMENT_SIMILARITY_SEARCH_FINISHED"),
    
    TEXT_UNIT_SIMILARITY_SEARCH_FINISHED("TEXT_UNIT_SIMILARITY_SEARCH_FINISHED");

    private String value;

    NotificationTypeEnum(String value) {
      this.value = value;
    }

    public String getValue() {
      return value;
    }

    @Override
    public String toString() {
      return String.valueOf(value);
    }

    public static NotificationTypeEnum fromValue(String value) {
      for (NotificationTypeEnum b : NotificationTypeEnum.values()) {
        if (b.value.equals(value)) {
          return b;
        }
      }
      return null;
    }

    public static class Adapter extends TypeAdapter<NotificationTypeEnum> {
      @Override
      public void write(final JsonWriter jsonWriter, final NotificationTypeEnum enumeration) throws IOException {
        jsonWriter.value(enumeration.getValue());
      }

      @Override
      public NotificationTypeEnum read(final JsonReader jsonReader) throws IOException {
        String value =  jsonReader.nextString();
        return NotificationTypeEnum.fromValue(value);
      }
    }
  }

  public static final String SERIALIZED_NAME_NOTIFICATION_TYPE = "notification_type";
  @SerializedName(SERIALIZED_NAME_NOTIFICATION_TYPE)
  private NotificationTypeEnum notificationType;

  public static final String SERIALIZED_NAME_REDIRECT_LINK = "redirect_link";
  @SerializedName(SERIALIZED_NAME_REDIRECT_LINK)
  private Object redirectLink;

  public WebNotificationDetailNotification() { 
  }

  
  public WebNotificationDetailNotification(
     Integer id, 
     String messageTemplate, 
     OffsetDateTime createdDate
  ) {
    this();
    this.id = id;
    this.messageTemplate = messageTemplate;
    this.createdDate = createdDate;
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




  public WebNotificationDetailNotification messageData(Object messageData) {
    
    this.messageData = messageData;
    return this;
  }

   /**
   * Get messageData
   * @return messageData
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Object getMessageData() {
    return messageData;
  }


  public void setMessageData(Object messageData) {
    this.messageData = messageData;
  }


   /**
   * Get messageTemplate
   * @return messageTemplate
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getMessageTemplate() {
    return messageTemplate;
  }




   /**
   * Get createdDate
   * @return createdDate
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public OffsetDateTime getCreatedDate() {
    return createdDate;
  }




  public WebNotificationDetailNotification notificationType(NotificationTypeEnum notificationType) {
    
    this.notificationType = notificationType;
    return this;
  }

   /**
   * Notification type
   * @return notificationType
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "Notification type")

  public NotificationTypeEnum getNotificationType() {
    return notificationType;
  }


  public void setNotificationType(NotificationTypeEnum notificationType) {
    this.notificationType = notificationType;
  }


  public WebNotificationDetailNotification redirectLink(Object redirectLink) {
    
    this.redirectLink = redirectLink;
    return this;
  }

   /**
   * Get redirectLink
   * @return redirectLink
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Object getRedirectLink() {
    return redirectLink;
  }


  public void setRedirectLink(Object redirectLink) {
    this.redirectLink = redirectLink;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    WebNotificationDetailNotification webNotificationDetailNotification = (WebNotificationDetailNotification) o;
    return Objects.equals(this.id, webNotificationDetailNotification.id) &&
        Objects.equals(this.messageData, webNotificationDetailNotification.messageData) &&
        Objects.equals(this.messageTemplate, webNotificationDetailNotification.messageTemplate) &&
        Objects.equals(this.createdDate, webNotificationDetailNotification.createdDate) &&
        Objects.equals(this.notificationType, webNotificationDetailNotification.notificationType) &&
        Objects.equals(this.redirectLink, webNotificationDetailNotification.redirectLink);
  }

  private static <T> boolean equalsNullable(JsonNullable<T> a, JsonNullable<T> b) {
    return a == b || (a != null && b != null && a.isPresent() && b.isPresent() && Objects.deepEquals(a.get(), b.get()));
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, messageData, messageTemplate, createdDate, notificationType, redirectLink);
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
    sb.append("class WebNotificationDetailNotification {\n");
    sb.append("    id: ").append(toIndentedString(id)).append("\n");
    sb.append("    messageData: ").append(toIndentedString(messageData)).append("\n");
    sb.append("    messageTemplate: ").append(toIndentedString(messageTemplate)).append("\n");
    sb.append("    createdDate: ").append(toIndentedString(createdDate)).append("\n");
    sb.append("    notificationType: ").append(toIndentedString(notificationType)).append("\n");
    sb.append("    redirectLink: ").append(toIndentedString(redirectLink)).append("\n");
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
