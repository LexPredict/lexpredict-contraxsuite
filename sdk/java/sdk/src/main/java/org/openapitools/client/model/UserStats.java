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
import java.math.BigDecimal;

/**
 * UserStats
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2022-01-19T15:46:46.101102+03:00[Europe/Moscow]")
public class UserStats {
  public static final String SERIALIZED_NAME_ID = "id";
  @SerializedName(SERIALIZED_NAME_ID)
  private Integer id;

  public static final String SERIALIZED_NAME_USER_NAME = "user_name";
  @SerializedName(SERIALIZED_NAME_USER_NAME)
  private String userName;

  public static final String SERIALIZED_NAME_GROUP_NAME = "group_name";
  @SerializedName(SERIALIZED_NAME_GROUP_NAME)
  private String groupName;

  public static final String SERIALIZED_NAME_TOTAL_PROJECTS = "total_projects";
  @SerializedName(SERIALIZED_NAME_TOTAL_PROJECTS)
  private Integer totalProjects;

  public static final String SERIALIZED_NAME_DOCUMENTS_ASSIGNED = "documents_assigned";
  @SerializedName(SERIALIZED_NAME_DOCUMENTS_ASSIGNED)
  private Integer documentsAssigned;

  public static final String SERIALIZED_NAME_DOCUMENTS_COMPLETED = "documents_completed";
  @SerializedName(SERIALIZED_NAME_DOCUMENTS_COMPLETED)
  private Integer documentsCompleted;

  public static final String SERIALIZED_NAME_DOCUMENTS_TODO = "documents_todo";
  @SerializedName(SERIALIZED_NAME_DOCUMENTS_TODO)
  private Integer documentsTodo;

  public static final String SERIALIZED_NAME_DOCUMENTS_COMPLETED_PCNT = "documents_completed_pcnt";
  @SerializedName(SERIALIZED_NAME_DOCUMENTS_COMPLETED_PCNT)
  private BigDecimal documentsCompletedPcnt;

  public static final String SERIALIZED_NAME_DOCUMENTS_TODO_PCNT = "documents_todo_pcnt";
  @SerializedName(SERIALIZED_NAME_DOCUMENTS_TODO_PCNT)
  private BigDecimal documentsTodoPcnt;

  public static final String SERIALIZED_NAME_CLAUSES_ASSIGNED = "clauses_assigned";
  @SerializedName(SERIALIZED_NAME_CLAUSES_ASSIGNED)
  private Integer clausesAssigned;

  public static final String SERIALIZED_NAME_CLAUSES_COMPLETED = "clauses_completed";
  @SerializedName(SERIALIZED_NAME_CLAUSES_COMPLETED)
  private Integer clausesCompleted;

  public static final String SERIALIZED_NAME_CLAUSES_TODO = "clauses_todo";
  @SerializedName(SERIALIZED_NAME_CLAUSES_TODO)
  private Integer clausesTodo;

  public static final String SERIALIZED_NAME_CLAUSES_COMPLETED_PCNT = "clauses_completed_pcnt";
  @SerializedName(SERIALIZED_NAME_CLAUSES_COMPLETED_PCNT)
  private BigDecimal clausesCompletedPcnt;

  public static final String SERIALIZED_NAME_CLAUSES_TODO_PCNT = "clauses_todo_pcnt";
  @SerializedName(SERIALIZED_NAME_CLAUSES_TODO_PCNT)
  private BigDecimal clausesTodoPcnt;

  public UserStats() { 
  }

  public UserStats id(Integer id) {
    
    this.id = id;
    return this;
  }

   /**
   * Get id
   * @return id
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getId() {
    return id;
  }


  public void setId(Integer id) {
    this.id = id;
  }


  public UserStats userName(String userName) {
    
    this.userName = userName;
    return this;
  }

   /**
   * Get userName
   * @return userName
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getUserName() {
    return userName;
  }


  public void setUserName(String userName) {
    this.userName = userName;
  }


  public UserStats groupName(String groupName) {
    
    this.groupName = groupName;
    return this;
  }

   /**
   * Get groupName
   * @return groupName
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(required = true, value = "")

  public String getGroupName() {
    return groupName;
  }


  public void setGroupName(String groupName) {
    this.groupName = groupName;
  }


  public UserStats totalProjects(Integer totalProjects) {
    
    this.totalProjects = totalProjects;
    return this;
  }

   /**
   * Get totalProjects
   * @return totalProjects
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getTotalProjects() {
    return totalProjects;
  }


  public void setTotalProjects(Integer totalProjects) {
    this.totalProjects = totalProjects;
  }


  public UserStats documentsAssigned(Integer documentsAssigned) {
    
    this.documentsAssigned = documentsAssigned;
    return this;
  }

   /**
   * Get documentsAssigned
   * @return documentsAssigned
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getDocumentsAssigned() {
    return documentsAssigned;
  }


  public void setDocumentsAssigned(Integer documentsAssigned) {
    this.documentsAssigned = documentsAssigned;
  }


  public UserStats documentsCompleted(Integer documentsCompleted) {
    
    this.documentsCompleted = documentsCompleted;
    return this;
  }

   /**
   * Get documentsCompleted
   * @return documentsCompleted
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getDocumentsCompleted() {
    return documentsCompleted;
  }


  public void setDocumentsCompleted(Integer documentsCompleted) {
    this.documentsCompleted = documentsCompleted;
  }


  public UserStats documentsTodo(Integer documentsTodo) {
    
    this.documentsTodo = documentsTodo;
    return this;
  }

   /**
   * Get documentsTodo
   * @return documentsTodo
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getDocumentsTodo() {
    return documentsTodo;
  }


  public void setDocumentsTodo(Integer documentsTodo) {
    this.documentsTodo = documentsTodo;
  }


  public UserStats documentsCompletedPcnt(BigDecimal documentsCompletedPcnt) {
    
    this.documentsCompletedPcnt = documentsCompletedPcnt;
    return this;
  }

   /**
   * Get documentsCompletedPcnt
   * @return documentsCompletedPcnt
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDocumentsCompletedPcnt() {
    return documentsCompletedPcnt;
  }


  public void setDocumentsCompletedPcnt(BigDecimal documentsCompletedPcnt) {
    this.documentsCompletedPcnt = documentsCompletedPcnt;
  }


  public UserStats documentsTodoPcnt(BigDecimal documentsTodoPcnt) {
    
    this.documentsTodoPcnt = documentsTodoPcnt;
    return this;
  }

   /**
   * Get documentsTodoPcnt
   * @return documentsTodoPcnt
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getDocumentsTodoPcnt() {
    return documentsTodoPcnt;
  }


  public void setDocumentsTodoPcnt(BigDecimal documentsTodoPcnt) {
    this.documentsTodoPcnt = documentsTodoPcnt;
  }


  public UserStats clausesAssigned(Integer clausesAssigned) {
    
    this.clausesAssigned = clausesAssigned;
    return this;
  }

   /**
   * Get clausesAssigned
   * @return clausesAssigned
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getClausesAssigned() {
    return clausesAssigned;
  }


  public void setClausesAssigned(Integer clausesAssigned) {
    this.clausesAssigned = clausesAssigned;
  }


  public UserStats clausesCompleted(Integer clausesCompleted) {
    
    this.clausesCompleted = clausesCompleted;
    return this;
  }

   /**
   * Get clausesCompleted
   * @return clausesCompleted
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getClausesCompleted() {
    return clausesCompleted;
  }


  public void setClausesCompleted(Integer clausesCompleted) {
    this.clausesCompleted = clausesCompleted;
  }


  public UserStats clausesTodo(Integer clausesTodo) {
    
    this.clausesTodo = clausesTodo;
    return this;
  }

   /**
   * Get clausesTodo
   * @return clausesTodo
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public Integer getClausesTodo() {
    return clausesTodo;
  }


  public void setClausesTodo(Integer clausesTodo) {
    this.clausesTodo = clausesTodo;
  }


  public UserStats clausesCompletedPcnt(BigDecimal clausesCompletedPcnt) {
    
    this.clausesCompletedPcnt = clausesCompletedPcnt;
    return this;
  }

   /**
   * Get clausesCompletedPcnt
   * @return clausesCompletedPcnt
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getClausesCompletedPcnt() {
    return clausesCompletedPcnt;
  }


  public void setClausesCompletedPcnt(BigDecimal clausesCompletedPcnt) {
    this.clausesCompletedPcnt = clausesCompletedPcnt;
  }


  public UserStats clausesTodoPcnt(BigDecimal clausesTodoPcnt) {
    
    this.clausesTodoPcnt = clausesTodoPcnt;
    return this;
  }

   /**
   * Get clausesTodoPcnt
   * @return clausesTodoPcnt
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getClausesTodoPcnt() {
    return clausesTodoPcnt;
  }


  public void setClausesTodoPcnt(BigDecimal clausesTodoPcnt) {
    this.clausesTodoPcnt = clausesTodoPcnt;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    UserStats userStats = (UserStats) o;
    return Objects.equals(this.id, userStats.id) &&
        Objects.equals(this.userName, userStats.userName) &&
        Objects.equals(this.groupName, userStats.groupName) &&
        Objects.equals(this.totalProjects, userStats.totalProjects) &&
        Objects.equals(this.documentsAssigned, userStats.documentsAssigned) &&
        Objects.equals(this.documentsCompleted, userStats.documentsCompleted) &&
        Objects.equals(this.documentsTodo, userStats.documentsTodo) &&
        Objects.equals(this.documentsCompletedPcnt, userStats.documentsCompletedPcnt) &&
        Objects.equals(this.documentsTodoPcnt, userStats.documentsTodoPcnt) &&
        Objects.equals(this.clausesAssigned, userStats.clausesAssigned) &&
        Objects.equals(this.clausesCompleted, userStats.clausesCompleted) &&
        Objects.equals(this.clausesTodo, userStats.clausesTodo) &&
        Objects.equals(this.clausesCompletedPcnt, userStats.clausesCompletedPcnt) &&
        Objects.equals(this.clausesTodoPcnt, userStats.clausesTodoPcnt);
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, userName, groupName, totalProjects, documentsAssigned, documentsCompleted, documentsTodo, documentsCompletedPcnt, documentsTodoPcnt, clausesAssigned, clausesCompleted, clausesTodo, clausesCompletedPcnt, clausesTodoPcnt);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class UserStats {\n");
    sb.append("    id: ").append(toIndentedString(id)).append("\n");
    sb.append("    userName: ").append(toIndentedString(userName)).append("\n");
    sb.append("    groupName: ").append(toIndentedString(groupName)).append("\n");
    sb.append("    totalProjects: ").append(toIndentedString(totalProjects)).append("\n");
    sb.append("    documentsAssigned: ").append(toIndentedString(documentsAssigned)).append("\n");
    sb.append("    documentsCompleted: ").append(toIndentedString(documentsCompleted)).append("\n");
    sb.append("    documentsTodo: ").append(toIndentedString(documentsTodo)).append("\n");
    sb.append("    documentsCompletedPcnt: ").append(toIndentedString(documentsCompletedPcnt)).append("\n");
    sb.append("    documentsTodoPcnt: ").append(toIndentedString(documentsTodoPcnt)).append("\n");
    sb.append("    clausesAssigned: ").append(toIndentedString(clausesAssigned)).append("\n");
    sb.append("    clausesCompleted: ").append(toIndentedString(clausesCompleted)).append("\n");
    sb.append("    clausesTodo: ").append(toIndentedString(clausesTodo)).append("\n");
    sb.append("    clausesCompletedPcnt: ").append(toIndentedString(clausesCompletedPcnt)).append("\n");
    sb.append("    clausesTodoPcnt: ").append(toIndentedString(clausesTodoPcnt)).append("\n");
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

