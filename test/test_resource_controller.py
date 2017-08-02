import unittest
from unittest.mock import Mock

from ai2.kubernetes.initializer.rejection import Rejection
from ai2.kubernetes.initializer.resource_controller import ResourceController


class TestResourceController(unittest.TestCase):
    def setUp(self):
        self.mock_handler = Mock()
        self.mock_handler.name = 'Namey'
        self.mock_handler.list_all_items.return_value = [1, 3, 6]

    def test_controller_delegates(self):
        """Test that a controller delegates appropriately to the wrapped ResourceHandler."""
        test_controller = ResourceController(self.mock_handler)
        self.assertEqual(test_controller.name, self.mock_handler.name)
        self.assertEqual(test_controller.list_all_items(), self.mock_handler.list_all_items())
        fake_item = {'a': 1}
        test_controller.update_item(fake_item)
        self.mock_handler.update_item.assert_called_with(fake_item)

    def test_rejects_all(self):
        """Test that a controller throws an appropriate Rejection by default."""
        test_controller = ResourceController(self.mock_handler)
        mock_item = Mock()
        mock_item.metadata.name = 'A name'
        try:
            test_controller.handle_item(mock_item)
            self.fail('Expected a Rejection to be thrown')
        except Rejection as rejection:
            self.assertEqual(rejection.status.reason, 'RejectAll')
