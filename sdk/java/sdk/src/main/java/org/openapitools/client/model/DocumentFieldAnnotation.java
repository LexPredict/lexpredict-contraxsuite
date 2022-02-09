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
import java.util.UUID;
import org.openapitools.jackson.nullable.JsonNullable;
import org.threeten.bp.OffsetDateTime;

/**
 * DocumentFieldAnnotation
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2022-01-19T15:46:46.101102+03:00[Europe/Moscow]")
public class DocumentFieldAnnotation {
  public static final String SERIALIZED_NAME_PK = "pk";
  @SerializedName(SERIALIZED_NAME_PK)
  private Integer pk;

  public static final String SERIALIZED_NAME_UID = "uid";
  @SerializedName(SERIALIZED_NAME_UID)
  private UUID uid;

  public static final String SERIALIZED_NAME_PROJECT_ID = "project_id";
  @SerializedName(SERIALIZED_NAME_PROJECT_ID)
  private Integer projectId;

  public static final String SERIALIZED_NAME_PROJECT_NAME = "project_name";
  @SerializedName(SERIALIZED_NAME_PROJECT_NAME)
  private String projectName;

  public static final String SERIALIZED_NAME_DOCUMENT_ID = "document_id";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_ID)
  private String documentId;

  public static final String SERIALIZED_NAME_DOCUMENT_NAME = "document_name";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_NAME)
  private String documentName;

  public static final String SERIALIZED_NAME_DOCUMENT_TYPE = "document_type";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_TYPE)
  private String documentType;

  public static final String SERIALIZED_NAME_DOCUMENT_STATUS = "document_status";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_STATUS)
  private String documentStatus;

  public static final String SERIALIZED_NAME_FIELD_ID = "field_id";
  @SerializedName(SERIALIZED_NAME_FIELD_ID)
  private String fieldId;

  public static final String SERIALIZED_NAME_FIELD_NAME = "field_name";
  @SerializedName(SERIALIZED_NAME_FIELD_NAME)
  private String fieldName;

  public static final String SERIALIZED_NAME_VALUE = "value";
  @SerializedName(SERIALIZED_NAME_VALUE)
  private Object value;

  public static final String SERIALIZED_NAME_LOCATION_START = "location_start";
  @SerializedName(SERIALIZED_NAME_LOCATION_START)
  private Integer locationStart;

  public static final String SERIALIZED_NAME_LOCATION_END = "location_end";
  @SerializedName(SERIALIZED_NAME_LOCATION_END)
  private Integer locationEnd;

  public static final String SERIALIZED_NAME_LOCATION_TEXT = "location_text";
  @SerializedName(SERIALIZED_NAME_LOCATION_TEXT)
  private String locationText;

  public static final String SERIALIZED_NAME_ASSIGNEE_ID = "assignee_id";
  @SerializedName(SERIALIZED_NAME_ASSIGNEE_ID)
  private Integer assigneeId;

  public static final String SERIALIZED_NAME_ASSIGN_DATE = "assign_date";
  @SerializedName(SERIALIZED_NAME_ASSIGN_DATE)
  private OffsetDateTime assignDate;

  public static final String SERIALIZED_NAME_STATUS_ID = "status_id";
  @SerializedName(SERIALIZED_NAME_STATUS_ID)
  private Integer statusId;

  public static final String SERIALIZED_NAME_STATUS_NAME = "status_name";
  @SerializedName(SERIALIZED_NAME_STATUS_NAME)
  private String statusName;

  public static final String SERIALIZED_NAME_ASSIGNEE_NAME = "assignee_name";
  @SerializedName(SERIALIZED_NAME_ASSIGNEE_NAME)
  private String assigneeName;

  public static final String SERIALIZED_NAME_MODIFIED_BY_ID = "modified_by_id";
  @SerializedName(SERIALIZED_NAME_MODIFIED_BY_ID)
  private String modifiedById;

  public static final String SERIALIZED_NAME_MODIFIED_DATE = "modified_date";
  @SerializedName(SERIALIZED_NAME_MODIFIED_DATE)
  private OffsetDateTime modifiedDate;

  public DocumentFieldAnnotation() { 
  }

  
  public DocumentFieldAnnotation(
     Integer pk, 
     UUID uid, 
     Integer projectId, 
     String projectName, 
     String documentId, 
     String documentName, 
     String documentType, 
     String documentStatus, 
     String fieldId, 
     String fieldName, 
     String statusName, 
     String assigneeName, 
     String modifiedById, 
     OffsetDateTime modifiedDate
  ) {
    this();
    this.pk = pk;
    this.uid = uid;
    this.projectId = projectId;
    this.projectName = projectName;
    this.documentId = documentId;
    this.documentName = documentName;
    this.documentType = documentType;
    this.documentStatus = documentStatus;
    this.fieldId = fieldId;
    this.fieldName = fieldName;
    this.statusName = statusName;
    this.assigneeName = assigneeName;
    this.modifiedById = modifiedById;
    this.modifiedDate = modifiedDate;
  }

   /**
   * Get pk
   * @return pk
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getPk() {
    return pk;
  }




   /**
   * Get uid
   * @return uid
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public UUID getUid() {
    return uid;
  }




   /**
   * Get projectId
   * @return projectId
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getProjectId() {
    return projectId;
  }




   /**
   * Get projectName
   * @return projectName
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getProjectName() {
    return projectName;
  }




   /**
   * Get documentId
   * @return documentId
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getDocumentId() {
    return documentId;
  }




   /**
   * Get documentName
   * @return documentName
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getDocumentName() {
    return documentName;
  }




   /**
   * Get documentType
   * @return documentType
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getDocumentType() {
    return documentType;
  }




   /**
   * Get documentStatus
   * @return documentStatus
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getDocumentStatus() {
    return documentStatus;
  }




   /**
   * Get fieldId
   * @return fieldId
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getFieldId() {
    return fieldId;
  }




   /**
   * Get fieldName
   * @return fieldName
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getFieldName() {
    return fieldName;
  }




  public DocumentFieldAnnotation value(Object value) {
    
    this.value = value;
    return this;
  }

   /**
   * Get value
   * @return value
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Object getValue() {
    return value;
  }


  public void setValue(Object value) {
    this.value = value;
  }


  public DocumentFieldAnnotation locationStart(Integer locationStart) {
    
    this.locationStart = locationStart;
    return this;
  }

   /**
   * Get locationStart
   * minimum: 0
   * maximum: 2147483647
   * @return locationStart
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getLocationStart() {
    return locationStart;
  }


  public void setLocationStart(Integer locationStart) {
    this.locationStart = locationStart;
  }


  public DocumentFieldAnnotation locationEnd(Integer locationEnd) {
    
    this.locationEnd = locationEnd;
    return this;
  }

   /**
   * Get locationEnd
   * minimum: 0
   * maximum: 2147483647
   * @return locationEnd
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getLocationEnd() {
    return locationEnd;
  }


  public void setLocationEnd(Integer locationEnd) {
    this.locationEnd = locationEnd;
  }


  public DocumentFieldAnnotation locationText(String locationText) {
    
    this.locationText = locationText;
    return this;
  }

   /**
   * Get locationText
   * @return locationText
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getLocationText() {
    return locationText;
  }


  public void setLocationText(String locationText) {
    this.locationText = locationText;
  }


  public DocumentFieldAnnotation assigneeId(Integer assigneeId) {
    
    this.assigneeId = assigneeId;
    return this;
  }

   /**
   * Get assigneeId
   * @return assigneeId
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getAssigneeId() {
    return assigneeId;
  }


  public void setAssigneeId(Integer assigneeId) {
    this.assigneeId = assigneeId;
  }


  public DocumentFieldAnnotation assignDate(OffsetDateTime assignDate) {
    
    this.assignDate = assignDate;
    return this;
  }

   /**
   * Get assignDate
   * @return assignDate
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public OffsetDateTime getAssignDate() {
    return assignDate;
  }


  public void setAssignDate(OffsetDateTime assignDate) {
    this.assignDate = assignDate;
  }


  public DocumentFieldAnnotation statusId(Integer statusId) {
    
    this.statusId = statusId;
    return this;
  }

   /**
   * Get statusId
   * @return statusId
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getStatusId() {
    return statusId;
  }


  public void setStatusId(Integer statusId) {
    this.statusId = statusId;
  }


   /**
   * Get statusName
   * @return statusName
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getStatusName() {
    return statusName;
  }




   /**
   * Get assigneeName
   * @return assigneeName
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getAssigneeName() {
    return assigneeName;
  }




   /**
   * Get modifiedById
   * @return modifiedById
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getModifiedById() {
    return modifiedById;
  }




   /**
   * Get modifiedDate
   * @return modifiedDate
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public OffsetDateTime getModifiedDate() {
    return modifiedDate;
  }




  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    DocumentFieldAnnotation documentFieldAnnotation = (DocumentFieldAnnotation) o;
    return Objects.equals(this.pk, documentFieldAnnotation.pk) &&
        Objects.equals(this.uid, documentFieldAnnotation.uid) &&
        Objects.equals(this.projectId, documentFieldAnnotation.projectId) &&
        Objects.equals(this.projectName, documentFieldAnnotation.projectName) &&
        Objects.equals(this.documentId, documentFieldAnnotation.documentId) &&
        Objects.equals(this.documentName, documentFieldAnnotation.documentName) &&
        Objects.equals(this.documentType, documentFieldAnnotation.documentType) &&
        Objects.equals(this.documentStatus, documentFieldAnnotation.documentStatus) &&
        Objects.equals(this.fieldId, documentFieldAnnotation.fieldId) &&
        Objects.equals(this.fieldName, documentFieldAnnotation.fieldName) &&
        Objects.equals(this.value, documentFieldAnnotation.value) &&
        Objects.equals(this.locationStart, documentFieldAnnotation.locationStart) &&
        Objects.equals(this.locationEnd, documentFieldAnnotation.locationEnd) &&
        Objects.equals(this.locationText, documentFieldAnnotation.locationText) &&
        Objects.equals(this.assigneeId, documentFieldAnnotation.assigneeId) &&
        Objects.equals(this.assignDate, documentFieldAnnotation.assignDate) &&
        Objects.equals(this.statusId, documentFieldAnnotation.statusId) &&
        Objects.equals(this.statusName, documentFieldAnnotation.statusName) &&
        Objects.equals(this.assigneeName, documentFieldAnnotation.assigneeName) &&
        Objects.equals(this.modifiedById, documentFieldAnnotation.modifiedById) &&
        Objects.equals(this.modifiedDate, documentFieldAnnotation.modifiedDate);
  }

  private static <T> boolean equalsNullable(JsonNullable<T> a, JsonNullable<T> b) {
    return a == b || (a != null && b != null && a.isPresent() && b.isPresent() && Objects.deepEquals(a.get(), b.get()));
  }

  @Override
  public int hashCode() {
    return Objects.hash(pk, uid, projectId, projectName, documentId, documentName, documentType, documentStatus, fieldId, fieldName, value, locationStart, locationEnd, locationText, assigneeId, assignDate, statusId, statusName, assigneeName, modifiedById, modifiedDate);
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
    sb.append("class DocumentFieldAnnotation {\n");
    sb.append("    pk: ").append(toIndentedString(pk)).append("\n");
    sb.append("    uid: ").append(toIndentedString(uid)).append("\n");
    sb.append("    projectId: ").append(toIndentedString(projectId)).append("\n");
    sb.append("    projectName: ").append(toIndentedString(projectName)).append("\n");
    sb.append("    documentId: ").append(toIndentedString(documentId)).append("\n");
    sb.append("    documentName: ").append(toIndentedString(documentName)).append("\n");
    sb.append("    documentType: ").append(toIndentedString(documentType)).append("\n");
    sb.append("    documentStatus: ").append(toIndentedString(documentStatus)).append("\n");
    sb.append("    fieldId: ").append(toIndentedString(fieldId)).append("\n");
    sb.append("    fieldName: ").append(toIndentedString(fieldName)).append("\n");
    sb.append("    value: ").append(toIndentedString(value)).append("\n");
    sb.append("    locationStart: ").append(toIndentedString(locationStart)).append("\n");
    sb.append("    locationEnd: ").append(toIndentedString(locationEnd)).append("\n");
    sb.append("    locationText: ").append(toIndentedString(locationText)).append("\n");
    sb.append("    assigneeId: ").append(toIndentedString(assigneeId)).append("\n");
    sb.append("    assignDate: ").append(toIndentedString(assignDate)).append("\n");
    sb.append("    statusId: ").append(toIndentedString(statusId)).append("\n");
    sb.append("    statusName: ").append(toIndentedString(statusName)).append("\n");
    sb.append("    assigneeName: ").append(toIndentedString(assigneeName)).append("\n");
    sb.append("    modifiedById: ").append(toIndentedString(modifiedById)).append("\n");
    sb.append("    modifiedDate: ").append(toIndentedString(modifiedDate)).append("\n");
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

