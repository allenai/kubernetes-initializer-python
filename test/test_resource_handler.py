import unittest
from unittest.mock import Mock

from ai2.kubernetes.initializer.resource_handler import ResourceHandler


class TestResourceHandler(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()

    def test_pod_handler(self):
        """Test that a pod handler can be created."""
        handler = ResourceHandler.pod_handler(self.mock_client)
        self.assertEqual(handler.name, "pod")

    def test_service_handler(self):
        """Test that a service handler can be created."""
        handler = ResourceHandler.service_handler(self.mock_client)
        self.assertEqual(handler.name, "service")

    def test_config_map_handler(self):
        """Test that a config map handler can be created."""
        handler = ResourceHandler.config_map_handler(self.mock_client)
        self.assertEqual(handler.name, "configmap")

    def test_job_handler(self):
        """Test that a job handler can be created."""
        handler = ResourceHandler.job_handler(self.mock_client)
        self.assertEqual(handler.name, "job")

    def test_deployment_handler(self):
        """Test that a deployment handler can be created."""
        handler = ResourceHandler.deployment_handler(self.mock_client)
        self.assertEqual(handler.name, "deployment")

    def test_daemon_set_handler(self):
        """Test that a daemon set handler can be created."""
        handler = ResourceHandler.daemon_set_handler(self.mock_client)
        self.assertEqual(handler.name, "daemonset")

    def test_cron_job_handler(self):
        """Test that a job job handler can be created."""
        handler = ResourceHandler.cron_job_handler(self.mock_client)
        self.assertEqual(handler.name, "cronjob")
