import unittest
from unittest.mock import Mock

from ai2.kubernetes.initializer.simple_resource_controller import SimpleResourceController


class TestSimpleResourceController(unittest.TestCase):
    def test_constructor(self):
        """Tests SimpleResourceController delegates to its constructor args."""
        mock_handler = Mock()
        mock_handle_item = Mock()

        test_controller = SimpleResourceController(mock_handler, mock_handle_item)

        self.assertEqual(test_controller._resource_handler, mock_handler)
        self.assertEqual(test_controller.handle_item, mock_handle_item)
