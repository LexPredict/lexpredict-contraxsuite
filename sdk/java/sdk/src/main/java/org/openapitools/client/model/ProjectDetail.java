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
import org.openapitools.client.model.ProjectDetailOwnersData;
import org.openapitools.client.model.ProjectListStatusData;
import org.openapitools.client.model.ProjectListTypeData;
import org.openapitools.jackson.nullable.JsonNullable;
import org.threeten.bp.OffsetDateTime;

/**
 * ProjectDetail
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-09-21T17:23:12.379447+03:00[Europe/Moscow]")
public class ProjectDetail {
  public static final String SERIALIZED_NAME_PK = "pk";
  @SerializedName(SERIALIZED_NAME_PK)
  private Integer pk;

  public static final String SERIALIZED_NAME_NAME = "name";
  @SerializedName(SERIALIZED_NAME_NAME)
  private String name;

  public static final String SERIALIZED_NAME_DESCRIPTION = "description";
  @SerializedName(SERIALIZED_NAME_DESCRIPTION)
  private String description;

  public static final String SERIALIZED_NAME_CREATED_DATE = "created_date";
  @SerializedName(SERIALIZED_NAME_CREATED_DATE)
  private OffsetDateTime createdDate;

  public static final String SERIALIZED_NAME_CREATED_BY_NAME = "created_by_name";
  @SerializedName(SERIALIZED_NAME_CREATED_BY_NAME)
  private String createdByName;

  public static final String SERIALIZED_NAME_MODIFIED_DATE = "modified_date";
  @SerializedName(SERIALIZED_NAME_MODIFIED_DATE)
  private OffsetDateTime modifiedDate;

  public static final String SERIALIZED_NAME_MODIFIED_BY_NAME = "modified_by_name";
  @SerializedName(SERIALIZED_NAME_MODIFIED_BY_NAME)
  private String modifiedByName;

  public static final String SERIALIZED_NAME_SEND_EMAIL_NOTIFICATION = "send_email_notification";
  @SerializedName(SERIALIZED_NAME_SEND_EMAIL_NOTIFICATION)
  private Boolean sendEmailNotification;

  public static final String SERIALIZED_NAME_HIDE_CLAUSE_REVIEW = "hide_clause_review";
  @SerializedName(SERIALIZED_NAME_HIDE_CLAUSE_REVIEW)
  private Boolean hideClauseReview;

  public static final String SERIALIZED_NAME_STATUS = "status";
  @SerializedName(SERIALIZED_NAME_STATUS)
  private Integer status;

  public static final String SERIALIZED_NAME_STATUS_DATA = "status_data";
  @SerializedName(SERIALIZED_NAME_STATUS_DATA)
  private ProjectListStatusData statusData;

  public static final String SERIALIZED_NAME_OWNERS = "owners";
  @SerializedName(SERIALIZED_NAME_OWNERS)
  private List<Integer> owners = null;

  public static final String SERIALIZED_NAME_OWNERS_DATA = "owners_data";
  @SerializedName(SERIALIZED_NAME_OWNERS_DATA)
  private List<ProjectDetailOwnersData> ownersData = null;

  public static final String SERIALIZED_NAME_REVIEWERS = "reviewers";
  @SerializedName(SERIALIZED_NAME_REVIEWERS)
  private List<Integer> reviewers = null;

  public static final String SERIALIZED_NAME_REVIEWERS_DATA = "reviewers_data";
  @SerializedName(SERIALIZED_NAME_REVIEWERS_DATA)
  private List<ProjectDetailOwnersData> reviewersData = null;

  public static final String SERIALIZED_NAME_SUPER_REVIEWERS = "super_reviewers";
  @SerializedName(SERIALIZED_NAME_SUPER_REVIEWERS)
  private List<Integer> superReviewers = null;

  public static final String SERIALIZED_NAME_SUPER_REVIEWERS_DATA = "super_reviewers_data";
  @SerializedName(SERIALIZED_NAME_SUPER_REVIEWERS_DATA)
  private List<ProjectDetailOwnersData> superReviewersData = null;

  public static final String SERIALIZED_NAME_JUNIOR_REVIEWERS = "junior_reviewers";
  @SerializedName(SERIALIZED_NAME_JUNIOR_REVIEWERS)
  private List<Integer> juniorReviewers = null;

  public static final String SERIALIZED_NAME_JUNIOR_REVIEWERS_DATA = "junior_reviewers_data";
  @SerializedName(SERIALIZED_NAME_JUNIOR_REVIEWERS_DATA)
  private List<ProjectDetailOwnersData> juniorReviewersData = null;

  public static final String SERIALIZED_NAME_TYPE = "type";
  @SerializedName(SERIALIZED_NAME_TYPE)
  private String type;

  public static final String SERIALIZED_NAME_TYPE_DATA = "type_data";
  @SerializedName(SERIALIZED_NAME_TYPE_DATA)
  private ProjectListTypeData typeData;

  public static final String SERIALIZED_NAME_PROGRESS = "progress";
  @SerializedName(SERIALIZED_NAME_PROGRESS)
  private String progress;

  public static final String SERIALIZED_NAME_USER_PERMISSIONS = "user_permissions";
  @SerializedName(SERIALIZED_NAME_USER_PERMISSIONS)
  private String userPermissions;

  public static final String SERIALIZED_NAME_TERM_TAGS = "term_tags";
  @SerializedName(SERIALIZED_NAME_TERM_TAGS)
  private List<Integer> termTags = null;

  public static final String SERIALIZED_NAME_DOCUMENT_TRANSFORMER = "document_transformer";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_TRANSFORMER)
  private Integer documentTransformer;

  public static final String SERIALIZED_NAME_TEXT_UNIT_TRANSFORMER = "text_unit_transformer";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_TRANSFORMER)
  private Integer textUnitTransformer;

  public static final String SERIALIZED_NAME_COMPANYTYPE_TAGS = "companytype_tags";
  @SerializedName(SERIALIZED_NAME_COMPANYTYPE_TAGS)
  private List<Integer> companytypeTags = null;

  public static final String SERIALIZED_NAME_APP_VARS = "app_vars";
  @SerializedName(SERIALIZED_NAME_APP_VARS)
  private String appVars;

  public static final String SERIALIZED_NAME_DOCUMENT_SIMILARITY_RUN_PARAMS = "document_similarity_run_params";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_SIMILARITY_RUN_PARAMS)
  private String documentSimilarityRunParams;

  public static final String SERIALIZED_NAME_TEXT_UNIT_SIMILARITY_RUN_PARAMS = "text_unit_similarity_run_params";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_SIMILARITY_RUN_PARAMS)
  private String textUnitSimilarityRunParams;

  public static final String SERIALIZED_NAME_DOCUMENT_SIMILARITY_PROCESS_ALLOWED = "document_similarity_process_allowed";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_SIMILARITY_PROCESS_ALLOWED)
  private String documentSimilarityProcessAllowed;

  public static final String SERIALIZED_NAME_TEXT_UNIT_SIMILARITY_PROCESS_ALLOWED = "text_unit_similarity_process_allowed";
  @SerializedName(SERIALIZED_NAME_TEXT_UNIT_SIMILARITY_PROCESS_ALLOWED)
  private String textUnitSimilarityProcessAllowed;


   /**
   * Get pk
   * @return pk
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getPk() {
    return pk;
  }




  public ProjectDetail name(String name) {
    
    this.name = name;
    return this;
  }

   /**
   * Get name
   * @return name
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getName() {
    return name;
  }


  public void setName(String name) {
    this.name = name;
  }


  public ProjectDetail description(String description) {
    
    this.description = description;
    return this;
  }

   /**
   * Get description
   * @return description
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getDescription() {
    return description;
  }


  public void setDescription(String description) {
    this.description = description;
  }


  public ProjectDetail createdDate(OffsetDateTime createdDate) {
    
    this.createdDate = createdDate;
    return this;
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


  public void setCreatedDate(OffsetDateTime createdDate) {
    this.createdDate = createdDate;
  }


  public ProjectDetail createdByName(String createdByName) {
    
    this.createdByName = createdByName;
    return this;
  }

   /**
   * Get createdByName
   * @return createdByName
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getCreatedByName() {
    return createdByName;
  }


  public void setCreatedByName(String createdByName) {
    this.createdByName = createdByName;
  }


  public ProjectDetail modifiedDate(OffsetDateTime modifiedDate) {
    
    this.modifiedDate = modifiedDate;
    return this;
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


  public void setModifiedDate(OffsetDateTime modifiedDate) {
    this.modifiedDate = modifiedDate;
  }


  public ProjectDetail modifiedByName(String modifiedByName) {
    
    this.modifiedByName = modifiedByName;
    return this;
  }

   /**
   * Get modifiedByName
   * @return modifiedByName
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public String getModifiedByName() {
    return modifiedByName;
  }


  public void setModifiedByName(String modifiedByName) {
    this.modifiedByName = modifiedByName;
  }


  public ProjectDetail sendEmailNotification(Boolean sendEmailNotification) {
    
    this.sendEmailNotification = sendEmailNotification;
    return this;
  }

   /**
   * Get sendEmailNotification
   * @return sendEmailNotification
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Boolean getSendEmailNotification() {
    return sendEmailNotification;
  }


  public void setSendEmailNotification(Boolean sendEmailNotification) {
    this.sendEmailNotification = sendEmailNotification;
  }


  public ProjectDetail hideClauseReview(Boolean hideClauseReview) {
    
    this.hideClauseReview = hideClauseReview;
    return this;
  }

   /**
   * Get hideClauseReview
   * @return hideClauseReview
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Boolean getHideClauseReview() {
    return hideClauseReview;
  }


  public void setHideClauseReview(Boolean hideClauseReview) {
    this.hideClauseReview = hideClauseReview;
  }


  public ProjectDetail status(Integer status) {
    
    this.status = status;
    return this;
  }

   /**
   * Get status
   * @return status
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getStatus() {
    return status;
  }


  public void setStatus(Integer status) {
    this.status = status;
  }


  public ProjectDetail statusData(ProjectListStatusData statusData) {
    
    this.statusData = statusData;
    return this;
  }

   /**
   * Get statusData
   * @return statusData
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public ProjectListStatusData getStatusData() {
    return statusData;
  }


  public void setStatusData(ProjectListStatusData statusData) {
    this.statusData = statusData;
  }


  public ProjectDetail owners(List<Integer> owners) {
    
    this.owners = owners;
    return this;
  }

  public ProjectDetail addOwnersItem(Integer ownersItem) {
    if (this.owners == null) {
      this.owners = new ArrayList<Integer>();
    }
    this.owners.add(ownersItem);
    return this;
  }

   /**
   * Get owners
   * @return owners
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public List<Integer> getOwners() {
    return owners;
  }


  public void setOwners(List<Integer> owners) {
    this.owners = owners;
  }


   /**
   * Get ownersData
   * @return ownersData
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public List<ProjectDetailOwnersData> getOwnersData() {
    return ownersData;
  }




  public ProjectDetail reviewers(List<Integer> reviewers) {
    
    this.reviewers = reviewers;
    return this;
  }

  public ProjectDetail addReviewersItem(Integer reviewersItem) {
    if (this.reviewers == null) {
      this.reviewers = new ArrayList<Integer>();
    }
    this.reviewers.add(reviewersItem);
    return this;
  }

   /**
   * Get reviewers
   * @return reviewers
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public List<Integer> getReviewers() {
    return reviewers;
  }


  public void setReviewers(List<Integer> reviewers) {
    this.reviewers = reviewers;
  }


   /**
   * Get reviewersData
   * @return reviewersData
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public List<ProjectDetailOwnersData> getReviewersData() {
    return reviewersData;
  }




  public ProjectDetail superReviewers(List<Integer> superReviewers) {
    
    this.superReviewers = superReviewers;
    return this;
  }

  public ProjectDetail addSuperReviewersItem(Integer superReviewersItem) {
    if (this.superReviewers == null) {
      this.superReviewers = new ArrayList<Integer>();
    }
    this.superReviewers.add(superReviewersItem);
    return this;
  }

   /**
   * Get superReviewers
   * @return superReviewers
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public List<Integer> getSuperReviewers() {
    return superReviewers;
  }


  public void setSuperReviewers(List<Integer> superReviewers) {
    this.superReviewers = superReviewers;
  }


   /**
   * Get superReviewersData
   * @return superReviewersData
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public List<ProjectDetailOwnersData> getSuperReviewersData() {
    return superReviewersData;
  }




  public ProjectDetail juniorReviewers(List<Integer> juniorReviewers) {
    
    this.juniorReviewers = juniorReviewers;
    return this;
  }

  public ProjectDetail addJuniorReviewersItem(Integer juniorReviewersItem) {
    if (this.juniorReviewers == null) {
      this.juniorReviewers = new ArrayList<Integer>();
    }
    this.juniorReviewers.add(juniorReviewersItem);
    return this;
  }

   /**
   * Get juniorReviewers
   * @return juniorReviewers
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public List<Integer> getJuniorReviewers() {
    return juniorReviewers;
  }


  public void setJuniorReviewers(List<Integer> juniorReviewers) {
    this.juniorReviewers = juniorReviewers;
  }


   /**
   * Get juniorReviewersData
   * @return juniorReviewersData
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public List<ProjectDetailOwnersData> getJuniorReviewersData() {
    return juniorReviewersData;
  }




  public ProjectDetail type(String type) {
    
    this.type = type;
    return this;
  }

   /**
   * Get type
   * @return type
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getType() {
    return type;
  }


  public void setType(String type) {
    this.type = type;
  }


  public ProjectDetail typeData(ProjectListTypeData typeData) {
    
    this.typeData = typeData;
    return this;
  }

   /**
   * Get typeData
   * @return typeData
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public ProjectListTypeData getTypeData() {
    return typeData;
  }


  public void setTypeData(ProjectListTypeData typeData) {
    this.typeData = typeData;
  }


   /**
   * Get progress
   * @return progress
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getProgress() {
    return progress;
  }




   /**
   * Get userPermissions
   * @return userPermissions
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getUserPermissions() {
    return userPermissions;
  }




  public ProjectDetail termTags(List<Integer> termTags) {
    
    this.termTags = termTags;
    return this;
  }

  public ProjectDetail addTermTagsItem(Integer termTagsItem) {
    if (this.termTags == null) {
      this.termTags = new ArrayList<Integer>();
    }
    this.termTags.add(termTagsItem);
    return this;
  }

   /**
   * Get termTags
   * @return termTags
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public List<Integer> getTermTags() {
    return termTags;
  }


  public void setTermTags(List<Integer> termTags) {
    this.termTags = termTags;
  }


  public ProjectDetail documentTransformer(Integer documentTransformer) {
    
    this.documentTransformer = documentTransformer;
    return this;
  }

   /**
   * Get documentTransformer
   * @return documentTransformer
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getDocumentTransformer() {
    return documentTransformer;
  }


  public void setDocumentTransformer(Integer documentTransformer) {
    this.documentTransformer = documentTransformer;
  }


  public ProjectDetail textUnitTransformer(Integer textUnitTransformer) {
    
    this.textUnitTransformer = textUnitTransformer;
    return this;
  }

   /**
   * Get textUnitTransformer
   * @return textUnitTransformer
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public Integer getTextUnitTransformer() {
    return textUnitTransformer;
  }


  public void setTextUnitTransformer(Integer textUnitTransformer) {
    this.textUnitTransformer = textUnitTransformer;
  }


  public ProjectDetail companytypeTags(List<Integer> companytypeTags) {
    
    this.companytypeTags = companytypeTags;
    return this;
  }

  public ProjectDetail addCompanytypeTagsItem(Integer companytypeTagsItem) {
    if (this.companytypeTags == null) {
      this.companytypeTags = new ArrayList<Integer>();
    }
    this.companytypeTags.add(companytypeTagsItem);
    return this;
  }

   /**
   * Get companytypeTags
   * @return companytypeTags
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public List<Integer> getCompanytypeTags() {
    return companytypeTags;
  }


  public void setCompanytypeTags(List<Integer> companytypeTags) {
    this.companytypeTags = companytypeTags;
  }


   /**
   * Get appVars
   * @return appVars
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getAppVars() {
    return appVars;
  }




   /**
   * Get documentSimilarityRunParams
   * @return documentSimilarityRunParams
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getDocumentSimilarityRunParams() {
    return documentSimilarityRunParams;
  }




   /**
   * Get textUnitSimilarityRunParams
   * @return textUnitSimilarityRunParams
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getTextUnitSimilarityRunParams() {
    return textUnitSimilarityRunParams;
  }




   /**
   * Get documentSimilarityProcessAllowed
   * @return documentSimilarityProcessAllowed
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getDocumentSimilarityProcessAllowed() {
    return documentSimilarityProcessAllowed;
  }




   /**
   * Get textUnitSimilarityProcessAllowed
   * @return textUnitSimilarityProcessAllowed
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getTextUnitSimilarityProcessAllowed() {
    return textUnitSimilarityProcessAllowed;
  }




  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    ProjectDetail projectDetail = (ProjectDetail) o;
    return Objects.equals(this.pk, projectDetail.pk) &&
        Objects.equals(this.name, projectDetail.name) &&
        Objects.equals(this.description, projectDetail.description) &&
        Objects.equals(this.createdDate, projectDetail.createdDate) &&
        Objects.equals(this.createdByName, projectDetail.createdByName) &&
        Objects.equals(this.modifiedDate, projectDetail.modifiedDate) &&
        Objects.equals(this.modifiedByName, projectDetail.modifiedByName) &&
        Objects.equals(this.sendEmailNotification, projectDetail.sendEmailNotification) &&
        Objects.equals(this.hideClauseReview, projectDetail.hideClauseReview) &&
        Objects.equals(this.status, projectDetail.status) &&
        Objects.equals(this.statusData, projectDetail.statusData) &&
        Objects.equals(this.owners, projectDetail.owners) &&
        Objects.equals(this.ownersData, projectDetail.ownersData) &&
        Objects.equals(this.reviewers, projectDetail.reviewers) &&
        Objects.equals(this.reviewersData, projectDetail.reviewersData) &&
        Objects.equals(this.superReviewers, projectDetail.superReviewers) &&
        Objects.equals(this.superReviewersData, projectDetail.superReviewersData) &&
        Objects.equals(this.juniorReviewers, projectDetail.juniorReviewers) &&
        Objects.equals(this.juniorReviewersData, projectDetail.juniorReviewersData) &&
        Objects.equals(this.type, projectDetail.type) &&
        Objects.equals(this.typeData, projectDetail.typeData) &&
        Objects.equals(this.progress, projectDetail.progress) &&
        Objects.equals(this.userPermissions, projectDetail.userPermissions) &&
        Objects.equals(this.termTags, projectDetail.termTags) &&
        Objects.equals(this.documentTransformer, projectDetail.documentTransformer) &&
        Objects.equals(this.textUnitTransformer, projectDetail.textUnitTransformer) &&
        Objects.equals(this.companytypeTags, projectDetail.companytypeTags) &&
        Objects.equals(this.appVars, projectDetail.appVars) &&
        Objects.equals(this.documentSimilarityRunParams, projectDetail.documentSimilarityRunParams) &&
        Objects.equals(this.textUnitSimilarityRunParams, projectDetail.textUnitSimilarityRunParams) &&
        Objects.equals(this.documentSimilarityProcessAllowed, projectDetail.documentSimilarityProcessAllowed) &&
        Objects.equals(this.textUnitSimilarityProcessAllowed, projectDetail.textUnitSimilarityProcessAllowed);
  }

  private static <T> boolean equalsNullable(JsonNullable<T> a, JsonNullable<T> b) {
    return a == b || (a != null && b != null && a.isPresent() && b.isPresent() && a.get().getClass().isArray() ? Arrays.equals((T[])a.get(), (T[])b.get()) : Objects.equals(a.get(), b.get()));
  }

  @Override
  public int hashCode() {
    return Objects.hash(pk, name, description, createdDate, createdByName, modifiedDate, modifiedByName, sendEmailNotification, hideClauseReview, status, statusData, owners, ownersData, reviewers, reviewersData, superReviewers, superReviewersData, juniorReviewers, juniorReviewersData, type, typeData, progress, userPermissions, termTags, documentTransformer, textUnitTransformer, companytypeTags, appVars, documentSimilarityRunParams, textUnitSimilarityRunParams, documentSimilarityProcessAllowed, textUnitSimilarityProcessAllowed);
  }

  private static <T> int hashCodeNullable(JsonNullable<T> a) {
    if (a == null) {
      return 1;
    }
    return a.isPresent()
      ? (a.get().getClass().isArray() ? Arrays.hashCode((T[])a.get()) : Objects.hashCode(a.get()))
      : 31;
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class ProjectDetail {\n");
    sb.append("    pk: ").append(toIndentedString(pk)).append("\n");
    sb.append("    name: ").append(toIndentedString(name)).append("\n");
    sb.append("    description: ").append(toIndentedString(description)).append("\n");
    sb.append("    createdDate: ").append(toIndentedString(createdDate)).append("\n");
    sb.append("    createdByName: ").append(toIndentedString(createdByName)).append("\n");
    sb.append("    modifiedDate: ").append(toIndentedString(modifiedDate)).append("\n");
    sb.append("    modifiedByName: ").append(toIndentedString(modifiedByName)).append("\n");
    sb.append("    sendEmailNotification: ").append(toIndentedString(sendEmailNotification)).append("\n");
    sb.append("    hideClauseReview: ").append(toIndentedString(hideClauseReview)).append("\n");
    sb.append("    status: ").append(toIndentedString(status)).append("\n");
    sb.append("    statusData: ").append(toIndentedString(statusData)).append("\n");
    sb.append("    owners: ").append(toIndentedString(owners)).append("\n");
    sb.append("    ownersData: ").append(toIndentedString(ownersData)).append("\n");
    sb.append("    reviewers: ").append(toIndentedString(reviewers)).append("\n");
    sb.append("    reviewersData: ").append(toIndentedString(reviewersData)).append("\n");
    sb.append("    superReviewers: ").append(toIndentedString(superReviewers)).append("\n");
    sb.append("    superReviewersData: ").append(toIndentedString(superReviewersData)).append("\n");
    sb.append("    juniorReviewers: ").append(toIndentedString(juniorReviewers)).append("\n");
    sb.append("    juniorReviewersData: ").append(toIndentedString(juniorReviewersData)).append("\n");
    sb.append("    type: ").append(toIndentedString(type)).append("\n");
    sb.append("    typeData: ").append(toIndentedString(typeData)).append("\n");
    sb.append("    progress: ").append(toIndentedString(progress)).append("\n");
    sb.append("    userPermissions: ").append(toIndentedString(userPermissions)).append("\n");
    sb.append("    termTags: ").append(toIndentedString(termTags)).append("\n");
    sb.append("    documentTransformer: ").append(toIndentedString(documentTransformer)).append("\n");
    sb.append("    textUnitTransformer: ").append(toIndentedString(textUnitTransformer)).append("\n");
    sb.append("    companytypeTags: ").append(toIndentedString(companytypeTags)).append("\n");
    sb.append("    appVars: ").append(toIndentedString(appVars)).append("\n");
    sb.append("    documentSimilarityRunParams: ").append(toIndentedString(documentSimilarityRunParams)).append("\n");
    sb.append("    textUnitSimilarityRunParams: ").append(toIndentedString(textUnitSimilarityRunParams)).append("\n");
    sb.append("    documentSimilarityProcessAllowed: ").append(toIndentedString(documentSimilarityProcessAllowed)).append("\n");
    sb.append("    textUnitSimilarityProcessAllowed: ").append(toIndentedString(textUnitSimilarityProcessAllowed)).append("\n");
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

