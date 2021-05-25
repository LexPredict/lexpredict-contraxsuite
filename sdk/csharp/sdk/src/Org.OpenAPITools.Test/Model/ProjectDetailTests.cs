/*
 * Contraxsuite API
 *
 * Contraxsuite API
 *
 * The version of the OpenAPI document: 2.0.0
 * 
 * Generated by: https://github.com/openapitools/openapi-generator.git
 */


using NUnit.Framework;

using System;
using System.Linq;
using System.IO;
using System.Collections.Generic;
using Org.OpenAPITools.Api;
using Org.OpenAPITools.Model;
using Org.OpenAPITools.Client;
using System.Reflection;
using Newtonsoft.Json;

namespace Org.OpenAPITools.Test
{
    /// <summary>
    ///  Class for testing ProjectDetail
    /// </summary>
    /// <remarks>
    /// This file is automatically generated by OpenAPI Generator (https://openapi-generator.tech).
    /// Please update the test case below to test the model.
    /// </remarks>
    public class ProjectDetailTests
    {
        // TODO uncomment below to declare an instance variable for ProjectDetail
        //private ProjectDetail instance;

        /// <summary>
        /// Setup before each test
        /// </summary>
        [SetUp]
        public void Init()
        {
            // TODO uncomment below to create an instance of ProjectDetail
            //instance = new ProjectDetail();
        }

        /// <summary>
        /// Clean up after each test
        /// </summary>
        [TearDown]
        public void Cleanup()
        {

        }

        /// <summary>
        /// Test an instance of ProjectDetail
        /// </summary>
        [Test]
        public void ProjectDetailInstanceTest()
        {
            // TODO uncomment below to test "IsInstanceOf" ProjectDetail
            //Assert.IsInstanceOf(typeof(ProjectDetail), instance);
        }


        /// <summary>
        /// Test the property 'Pk'
        /// </summary>
        [Test]
        public void PkTest()
        {
            // TODO unit test for the property 'Pk'
        }
        /// <summary>
        /// Test the property 'Name'
        /// </summary>
        [Test]
        public void NameTest()
        {
            // TODO unit test for the property 'Name'
        }
        /// <summary>
        /// Test the property 'Description'
        /// </summary>
        [Test]
        public void DescriptionTest()
        {
            // TODO unit test for the property 'Description'
        }
        /// <summary>
        /// Test the property 'CreatedDate'
        /// </summary>
        [Test]
        public void CreatedDateTest()
        {
            // TODO unit test for the property 'CreatedDate'
        }
        /// <summary>
        /// Test the property 'CreatedByName'
        /// </summary>
        [Test]
        public void CreatedByNameTest()
        {
            // TODO unit test for the property 'CreatedByName'
        }
        /// <summary>
        /// Test the property 'ModifiedDate'
        /// </summary>
        [Test]
        public void ModifiedDateTest()
        {
            // TODO unit test for the property 'ModifiedDate'
        }
        /// <summary>
        /// Test the property 'ModifiedByName'
        /// </summary>
        [Test]
        public void ModifiedByNameTest()
        {
            // TODO unit test for the property 'ModifiedByName'
        }
        /// <summary>
        /// Test the property 'SendEmailNotification'
        /// </summary>
        [Test]
        public void SendEmailNotificationTest()
        {
            // TODO unit test for the property 'SendEmailNotification'
        }
        /// <summary>
        /// Test the property 'HideClauseReview'
        /// </summary>
        [Test]
        public void HideClauseReviewTest()
        {
            // TODO unit test for the property 'HideClauseReview'
        }
        /// <summary>
        /// Test the property 'Status'
        /// </summary>
        [Test]
        public void StatusTest()
        {
            // TODO unit test for the property 'Status'
        }
        /// <summary>
        /// Test the property 'StatusData'
        /// </summary>
        [Test]
        public void StatusDataTest()
        {
            // TODO unit test for the property 'StatusData'
        }
        /// <summary>
        /// Test the property 'Owners'
        /// </summary>
        [Test]
        public void OwnersTest()
        {
            // TODO unit test for the property 'Owners'
        }
        /// <summary>
        /// Test the property 'OwnersData'
        /// </summary>
        [Test]
        public void OwnersDataTest()
        {
            // TODO unit test for the property 'OwnersData'
        }
        /// <summary>
        /// Test the property 'Reviewers'
        /// </summary>
        [Test]
        public void ReviewersTest()
        {
            // TODO unit test for the property 'Reviewers'
        }
        /// <summary>
        /// Test the property 'ReviewersData'
        /// </summary>
        [Test]
        public void ReviewersDataTest()
        {
            // TODO unit test for the property 'ReviewersData'
        }
        /// <summary>
        /// Test the property 'SuperReviewers'
        /// </summary>
        [Test]
        public void SuperReviewersTest()
        {
            // TODO unit test for the property 'SuperReviewers'
        }
        /// <summary>
        /// Test the property 'SuperReviewersData'
        /// </summary>
        [Test]
        public void SuperReviewersDataTest()
        {
            // TODO unit test for the property 'SuperReviewersData'
        }
        /// <summary>
        /// Test the property 'JuniorReviewers'
        /// </summary>
        [Test]
        public void JuniorReviewersTest()
        {
            // TODO unit test for the property 'JuniorReviewers'
        }
        /// <summary>
        /// Test the property 'JuniorReviewersData'
        /// </summary>
        [Test]
        public void JuniorReviewersDataTest()
        {
            // TODO unit test for the property 'JuniorReviewersData'
        }
        /// <summary>
        /// Test the property 'Type'
        /// </summary>
        [Test]
        public void TypeTest()
        {
            // TODO unit test for the property 'Type'
        }
        /// <summary>
        /// Test the property 'TypeData'
        /// </summary>
        [Test]
        public void TypeDataTest()
        {
            // TODO unit test for the property 'TypeData'
        }
        /// <summary>
        /// Test the property 'Progress'
        /// </summary>
        [Test]
        public void ProgressTest()
        {
            // TODO unit test for the property 'Progress'
        }
        /// <summary>
        /// Test the property 'UserPermissions'
        /// </summary>
        [Test]
        public void UserPermissionsTest()
        {
            // TODO unit test for the property 'UserPermissions'
        }
        /// <summary>
        /// Test the property 'TermTags'
        /// </summary>
        [Test]
        public void TermTagsTest()
        {
            // TODO unit test for the property 'TermTags'
        }
        /// <summary>
        /// Test the property 'DocumentTransformer'
        /// </summary>
        [Test]
        public void DocumentTransformerTest()
        {
            // TODO unit test for the property 'DocumentTransformer'
        }
        /// <summary>
        /// Test the property 'TextUnitTransformer'
        /// </summary>
        [Test]
        public void TextUnitTransformerTest()
        {
            // TODO unit test for the property 'TextUnitTransformer'
        }
        /// <summary>
        /// Test the property 'CompanytypeTags'
        /// </summary>
        [Test]
        public void CompanytypeTagsTest()
        {
            // TODO unit test for the property 'CompanytypeTags'
        }
        /// <summary>
        /// Test the property 'AppVars'
        /// </summary>
        [Test]
        public void AppVarsTest()
        {
            // TODO unit test for the property 'AppVars'
        }
        /// <summary>
        /// Test the property 'DocumentSimilarityRunParams'
        /// </summary>
        [Test]
        public void DocumentSimilarityRunParamsTest()
        {
            // TODO unit test for the property 'DocumentSimilarityRunParams'
        }
        /// <summary>
        /// Test the property 'TextUnitSimilarityRunParams'
        /// </summary>
        [Test]
        public void TextUnitSimilarityRunParamsTest()
        {
            // TODO unit test for the property 'TextUnitSimilarityRunParams'
        }
        /// <summary>
        /// Test the property 'DocumentSimilarityProcessAllowed'
        /// </summary>
        [Test]
        public void DocumentSimilarityProcessAllowedTest()
        {
            // TODO unit test for the property 'DocumentSimilarityProcessAllowed'
        }
        /// <summary>
        /// Test the property 'TextUnitSimilarityProcessAllowed'
        /// </summary>
        [Test]
        public void TextUnitSimilarityProcessAllowedTest()
        {
            // TODO unit test for the property 'TextUnitSimilarityProcessAllowed'
        }

    }

}