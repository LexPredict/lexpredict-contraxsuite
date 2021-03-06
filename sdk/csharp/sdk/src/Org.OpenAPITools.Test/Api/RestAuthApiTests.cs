/* 
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 1.0.0
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
    ///  Class for testing RestAuthApi
    /// </summary>
    /// <remarks>
    /// This file is automatically generated by OpenAPI Generator (https://openapi-generator.tech).
    /// Please update the test case below to test the API endpoint.
    /// </remarks>
    public class RestAuthApiTests
    {
        private RestAuthApi instance;

        /// <summary>
        /// Setup before each unit test
        /// </summary>
        [SetUp]
        public void Init()
        {
            instance = new RestAuthApi();
        }

        /// <summary>
        /// Clean up after each unit test
        /// </summary>
        [TearDown]
        public void Cleanup()
        {

        }

        /// <summary>
        /// Test an instance of RestAuthApi
        /// </summary>
        [Test]
        public void InstanceTest()
        {
            // TODO uncomment below to test 'IsInstanceOf' RestAuthApi
            //Assert.IsInstanceOf(typeof(RestAuthApi), instance);
        }

        
        /// <summary>
        /// Test RestAuthLoginPOST
        /// </summary>
        [Test]
        public void RestAuthLoginPOSTTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //Login login = null;
            //var response = instance.RestAuthLoginPOST(login);
            //Assert.IsInstanceOf(typeof(LoginResponse), response, "response is LoginResponse");
        }
        
        /// <summary>
        /// Test RestAuthLogoutGET
        /// </summary>
        [Test]
        public void RestAuthLogoutGETTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //var response = instance.RestAuthLogoutGET();
            //Assert.IsInstanceOf(typeof(List<RestAuthCommonResponse>), response, "response is List<RestAuthCommonResponse>");
        }
        
        /// <summary>
        /// Test RestAuthLogoutPOST
        /// </summary>
        [Test]
        public void RestAuthLogoutPOSTTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //Dictionary<string, Object> requestBody = null;
            //var response = instance.RestAuthLogoutPOST(requestBody);
            //Assert.IsInstanceOf(typeof(RestAuthCommonResponse), response, "response is RestAuthCommonResponse");
        }
        
        /// <summary>
        /// Test RestAuthPasswordChangePOST
        /// </summary>
        [Test]
        public void RestAuthPasswordChangePOSTTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //CustomPasswordChange customPasswordChange = null;
            //var response = instance.RestAuthPasswordChangePOST(customPasswordChange);
            //Assert.IsInstanceOf(typeof(RestAuthCommonResponse), response, "response is RestAuthCommonResponse");
        }
        
        /// <summary>
        /// Test RestAuthPasswordResetConfirmPOST
        /// </summary>
        [Test]
        public void RestAuthPasswordResetConfirmPOSTTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //CustomPasswordResetConfirm customPasswordResetConfirm = null;
            //var response = instance.RestAuthPasswordResetConfirmPOST(customPasswordResetConfirm);
            //Assert.IsInstanceOf(typeof(RestAuthCommonResponse), response, "response is RestAuthCommonResponse");
        }
        
        /// <summary>
        /// Test RestAuthPasswordResetPOST
        /// </summary>
        [Test]
        public void RestAuthPasswordResetPOSTTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //CustomPasswordReset customPasswordReset = null;
            //var response = instance.RestAuthPasswordResetPOST(customPasswordReset);
            //Assert.IsInstanceOf(typeof(RestAuthCommonResponse), response, "response is RestAuthCommonResponse");
        }
        
        /// <summary>
        /// Test RestAuthRegistrationPOST
        /// </summary>
        [Test]
        public void RestAuthRegistrationPOSTTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //Register register = null;
            //var response = instance.RestAuthRegistrationPOST(register);
            //Assert.IsInstanceOf(typeof(Register), response, "response is Register");
        }
        
        /// <summary>
        /// Test RestAuthRegistrationVerifyEmailPOST
        /// </summary>
        [Test]
        public void RestAuthRegistrationVerifyEmailPOSTTest()
        {
            // TODO uncomment below to test the method and replace null with proper value
            //VerifyEmail verifyEmail = null;
            //var response = instance.RestAuthRegistrationVerifyEmailPOST(verifyEmail);
            //Assert.IsInstanceOf(typeof(VerifyEmail), response, "response is VerifyEmail");
        }
        
    }

}
