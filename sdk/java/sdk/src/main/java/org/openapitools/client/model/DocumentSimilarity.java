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
import java.math.BigDecimal;
import org.openapitools.client.model.DocumentSimilarityRun;

/**
 * DocumentSimilarity
 */
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2021-09-21T17:23:12.379447+03:00[Europe/Moscow]")
public class DocumentSimilarity {
  public static final String SERIALIZED_NAME_DOCUMENT_A_NAME = "document_a__name";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_A_NAME)
  private String documentAName;

  public static final String SERIALIZED_NAME_DOCUMENT_A_PK = "document_a__pk";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_A_PK)
  private String documentAPk;

  public static final String SERIALIZED_NAME_DOCUMENT_B_NAME = "document_b__name";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_B_NAME)
  private String documentBName;

  public static final String SERIALIZED_NAME_DOCUMENT_B_PK = "document_b__pk";
  @SerializedName(SERIALIZED_NAME_DOCUMENT_B_PK)
  private String documentBPk;

  public static final String SERIALIZED_NAME_SIMILARITY = "similarity";
  @SerializedName(SERIALIZED_NAME_SIMILARITY)
  private BigDecimal similarity;

  public static final String SERIALIZED_NAME_RUN = "run";
  @SerializedName(SERIALIZED_NAME_RUN)
  private DocumentSimilarityRun run;


   /**
   * Get documentAName
   * @return documentAName
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getDocumentAName() {
    return documentAName;
  }




   /**
   * Get documentAPk
   * @return documentAPk
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getDocumentAPk() {
    return documentAPk;
  }




   /**
   * Get documentBName
   * @return documentBName
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getDocumentBName() {
    return documentBName;
  }




   /**
   * Get documentBPk
   * @return documentBPk
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public String getDocumentBPk() {
    return documentBPk;
  }




  public DocumentSimilarity similarity(BigDecimal similarity) {
    
    this.similarity = similarity;
    return this;
  }

   /**
   * Get similarity
   * @return similarity
  **/
  @javax.annotation.Nonnull
  @ApiModelProperty(required = true, value = "")

  public BigDecimal getSimilarity() {
    return similarity;
  }


  public void setSimilarity(BigDecimal similarity) {
    this.similarity = similarity;
  }


  public DocumentSimilarity run(DocumentSimilarityRun run) {
    
    this.run = run;
    return this;
  }

   /**
   * Get run
   * @return run
  **/
  @javax.annotation.Nullable
  @ApiModelProperty(value = "")

  public DocumentSimilarityRun getRun() {
    return run;
  }


  public void setRun(DocumentSimilarityRun run) {
    this.run = run;
  }


  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    DocumentSimilarity documentSimilarity = (DocumentSimilarity) o;
    return Objects.equals(this.documentAName, documentSimilarity.documentAName) &&
        Objects.equals(this.documentAPk, documentSimilarity.documentAPk) &&
        Objects.equals(this.documentBName, documentSimilarity.documentBName) &&
        Objects.equals(this.documentBPk, documentSimilarity.documentBPk) &&
        Objects.equals(this.similarity, documentSimilarity.similarity) &&
        Objects.equals(this.run, documentSimilarity.run);
  }

  @Override
  public int hashCode() {
    return Objects.hash(documentAName, documentAPk, documentBName, documentBPk, similarity, run);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class DocumentSimilarity {\n");
    sb.append("    documentAName: ").append(toIndentedString(documentAName)).append("\n");
    sb.append("    documentAPk: ").append(toIndentedString(documentAPk)).append("\n");
    sb.append("    documentBName: ").append(toIndentedString(documentBName)).append("\n");
    sb.append("    documentBPk: ").append(toIndentedString(documentBPk)).append("\n");
    sb.append("    similarity: ").append(toIndentedString(similarity)).append("\n");
    sb.append("    run: ").append(toIndentedString(run)).append("\n");
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

