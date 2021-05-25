"""
    Contraxsuite API

    Contraxsuite API  # noqa: E501

    The version of the OpenAPI document: 2.0.0
    Generated by: https://openapi-generator.tech
"""


import unittest

import openapi_client
from openapi_client.api.task_api import TaskApi  # noqa: E501


class TestTaskApi(unittest.TestCase):
    """TaskApi unit test stubs"""

    def setUp(self):
        self.api = TaskApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_task_clean_tasks_post(self):
        """Test case for task_clean_tasks_post

        """
        pass

    def test_task_load_dictionaries_post(self):
        """Test case for task_load_dictionaries_post

        """
        pass

    def test_task_load_documents_get(self):
        """Test case for task_load_documents_get

        """
        pass

    def test_task_load_documents_post(self):
        """Test case for task_load_documents_post

        """
        pass

    def test_task_locate_get(self):
        """Test case for task_locate_get

        """
        pass

    def test_task_locate_post(self):
        """Test case for task_locate_post

        """
        pass

    def test_task_process_text_extraction_results_request_id_post(self):
        """Test case for task_process_text_extraction_results_request_id_post

        """
        pass

    def test_task_purge_task_post(self):
        """Test case for task_purge_task_post

        """
        pass

    def test_task_recall_task_get(self):
        """Test case for task_recall_task_get

        """
        pass

    def test_task_recall_task_post(self):
        """Test case for task_recall_task_post

        """
        pass

    def test_task_reindexroutines_check_schedule_post(self):
        """Test case for task_reindexroutines_check_schedule_post

        """
        pass

    def test_task_task_log_get(self):
        """Test case for task_task_log_get

        """
        pass

    def test_task_task_status_get(self):
        """Test case for task_task_status_get

        """
        pass

    def test_task_tasks_get(self):
        """Test case for task_tasks_get

        """
        pass

    def test_task_tasks_id_get(self):
        """Test case for task_tasks_id_get

        """
        pass

    def test_task_tasks_project_project_id_active_tasks_get(self):
        """Test case for task_tasks_project_project_id_active_tasks_get

        """
        pass

    def test_task_tasks_project_project_id_tasks_get(self):
        """Test case for task_tasks_project_project_id_tasks_get

        """
        pass

    def test_task_update_elastic_index_get(self):
        """Test case for task_update_elastic_index_get

        """
        pass

    def test_task_update_elastic_index_post(self):
        """Test case for task_update_elastic_index_post

        """
        pass


if __name__ == '__main__':
    unittest.main()