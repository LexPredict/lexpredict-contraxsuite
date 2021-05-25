/*
 * Contraxsuite API
 *
 * Contraxsuite API
 *
 * The version of the OpenAPI document: 2.0.0
 * 
 * Generated by: https://github.com/openapitools/openapi-generator.git
 */

using System;
using System.IO;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Reflection;
using RestSharp;
using NUnit.Framework;

using Org.OpenAPITools.Client;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Model;

namespace Org.OpenAPITools.Test
{
    /// <summary>
    ///  Class for testing SimilarityApi
    /// </summary>
    /// <remarks>
    /// This file is automatically generated by OpenAPI Generator (https://openapi-generator.tech).
    /// Please update the test case below to test the API endpoint.
    /// </remarks>
    public class SimilarityApiTests
    {
        private SimilarityApi instance;

        /// <summary>
        /// Setup before each unit test
        /// </summary>
        [SetUp]
        public void Init()
        {
            instance = new SimilarityApi();
        }

        /// <summary>
        /// Clean up after each unit test
        /// </summary>
        [TearDown]
        public void Cleanup()
        {

        }

        /// <summary>
        /// Test an instance of SimilarityApi
        /// </summary>
        [Test]
        public void InstanceTest()
        {
            // TODO uncomment below to test 'IsInstanceOf' SimilarityApi
            //Assert.IsInstanceOf(typeof(SimilarityApi), instance);
        }

        
        /// <summary>
        /// Test SimilarityDocumentSimilarityByFeaturesGET
        /// </summary>
        [Test]
        public void SimilarityDocumentSimilarityByFeaturesGETTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //var response = instance.SimilarityDocumentSimilarityByFeaturesGET();
            //Assert.IsInstanceOf(typeof(Dictionary<string, Object>), response, "response is Dictionary<string, Object>");
        }
        
        /// <summary>
        /// Test SimilarityDocumentSimilarityByFeaturesPOST
        /// </summary>
        [Test]
        public void SimilarityDocumentSimilarityByFeaturesPOSTTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //DocumentSimilarityByFeaturesForm documentSimilarityByFeaturesForm = null;
            //var response = instance.SimilarityDocumentSimilarityByFeaturesPOST(documentSimilarityByFeaturesForm);
            //Assert.IsInstanceOf(typeof(SimilarityPOSTObjectResponse), response, "response is SimilarityPOSTObjectResponse");
        }
        
        /// <summary>
        /// Test SimilarityPartySimilarityGET
        /// </summary>
        [Test]
        public void SimilarityPartySimilarityGETTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //var response = instance.SimilarityPartySimilarityGET();
            //Assert.IsInstanceOf(typeof(Dictionary<string, Object>), response, "response is Dictionary<string, Object>");
        }
        
        /// <summary>
        /// Test SimilarityPartySimilarityPOST
        /// </summary>
        [Test]
        public void SimilarityPartySimilarityPOSTTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //PartySimilarityForm partySimilarityForm = null;
            //var response = instance.SimilarityPartySimilarityPOST(partySimilarityForm);
            //Assert.IsInstanceOf(typeof(SimilarityPOSTObjectResponse), response, "response is SimilarityPOSTObjectResponse");
        }
        
        /// <summary>
        /// Test SimilarityProjectDocumentsSimilarityByVectorsGET
        /// </summary>
        [Test]
        public void SimilarityProjectDocumentsSimilarityByVectorsGETTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //var response = instance.SimilarityProjectDocumentsSimilarityByVectorsGET();
            //Assert.IsInstanceOf(typeof(Dictionary<string, Object>), response, "response is Dictionary<string, Object>");
        }
        
        /// <summary>
        /// Test SimilarityProjectDocumentsSimilarityByVectorsPOST
        /// </summary>
        [Test]
        public void SimilarityProjectDocumentsSimilarityByVectorsPOSTTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //ProjectDocumentsSimilarityByVectorsForm projectDocumentsSimilarityByVectorsForm = null;
            //var response = instance.SimilarityProjectDocumentsSimilarityByVectorsPOST(projectDocumentsSimilarityByVectorsForm);
            //Assert.IsInstanceOf(typeof(SimilarityPOSTObjectResponse), response, "response is SimilarityPOSTObjectResponse");
        }
        
        /// <summary>
        /// Test SimilarityProjectTextUnitsSimilarityByVectorsGET
        /// </summary>
        [Test]
        public void SimilarityProjectTextUnitsSimilarityByVectorsGETTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //var response = instance.SimilarityProjectTextUnitsSimilarityByVectorsGET();
            //Assert.IsInstanceOf(typeof(Dictionary<string, Object>), response, "response is Dictionary<string, Object>");
        }
        
        /// <summary>
        /// Test SimilarityProjectTextUnitsSimilarityByVectorsPOST
        /// </summary>
        [Test]
        public void SimilarityProjectTextUnitsSimilarityByVectorsPOSTTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //ProjectTextUnitsSimilarityByVectorsForm projectTextUnitsSimilarityByVectorsForm = null;
            //var response = instance.SimilarityProjectTextUnitsSimilarityByVectorsPOST(projectTextUnitsSimilarityByVectorsForm);
            //Assert.IsInstanceOf(typeof(SimilarityPOSTObjectResponse), response, "response is SimilarityPOSTObjectResponse");
        }
        
        /// <summary>
        /// Test SimilaritySimilarityGET
        /// </summary>
        [Test]
        public void SimilaritySimilarityGETTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //var response = instance.SimilaritySimilarityGET();
            //Assert.IsInstanceOf(typeof(Dictionary<string, Object>), response, "response is Dictionary<string, Object>");
        }
        
        /// <summary>
        /// Test SimilaritySimilarityPOST
        /// </summary>
        [Test]
        public void SimilaritySimilarityPOSTTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //SimilarityForm similarityForm = null;
            //var response = instance.SimilaritySimilarityPOST(similarityForm);
            //Assert.IsInstanceOf(typeof(SimilarityPOSTObjectResponse), response, "response is SimilarityPOSTObjectResponse");
        }
        
        /// <summary>
        /// Test SimilarityTextUnitSimilarityByFeaturesGET
        /// </summary>
        [Test]
        public void SimilarityTextUnitSimilarityByFeaturesGETTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //var response = instance.SimilarityTextUnitSimilarityByFeaturesGET();
            //Assert.IsInstanceOf(typeof(Dictionary<string, Object>), response, "response is Dictionary<string, Object>");
        }
        
        /// <summary>
        /// Test SimilarityTextUnitSimilarityByFeaturesPOST
        /// </summary>
        [Test]
        public void SimilarityTextUnitSimilarityByFeaturesPOSTTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //TextUnitSimilarityByFeaturesForm textUnitSimilarityByFeaturesForm = null;
            //var response = instance.SimilarityTextUnitSimilarityByFeaturesPOST(textUnitSimilarityByFeaturesForm);
            //Assert.IsInstanceOf(typeof(SimilarityPOSTObjectResponse), response, "response is SimilarityPOSTObjectResponse");
        }
        
    }

}