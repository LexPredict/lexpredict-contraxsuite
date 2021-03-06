# coding: utf-8

"""

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest
import datetime

import openapi_client
from openapi_client.models.text_unit_cluster import TextUnitCluster  # noqa: E501
from openapi_client.rest import ApiException

class TestTextUnitCluster(unittest.TestCase):
    """TextUnitCluster unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test TextUnitCluster
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = openapi_client.models.text_unit_cluster.TextUnitCluster()  # noqa: E501
        if include_optional :
            return TextUnitCluster(
                pk = 56, 
                cluster_id = -2147483648, 
                name = '0', 
                self_name = '0', 
                description = '0', 
                cluster_by = '0', 
                using = '0', 
                created_date = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                text_unit_count = '0', 
                text_unit_data = '0'
            )
        else :
            return TextUnitCluster(
                name = '0',
                self_name = '0',
                description = '0',
                cluster_by = '0',
                using = '0',
        )

    def testTextUnitCluster(self):
        """Test TextUnitCluster"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
