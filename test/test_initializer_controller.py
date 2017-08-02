import unittest
from unittest.mock import Mock

from kubernetes.client.models.v1_initializer import V1Initializer
from kubernetes.client.models.v1_initializers import V1Initializers

from ai2.kubernetes.initializer.initializer_controller import InitializerController
from ai2.kubernetes.initializer.rejection import Rejection


class TestInitializerController(unittest.TestCase):
    def mock_resource_controller(self, name, list_results):
        """Return a mocked ResourceController with the given name returning the given item list."""
        mock_controller = Mock()
        mock_controller.name = name
        mock_list_result = Mock()
        mock_list_result.items = list_results
        mock_controller.list_all_items.return_value = mock_list_result
        return mock_controller

    def mock_item(self, name):
        """Return a mocked resource item with a name+namespace set."""
        mock_item = Mock()
        mock_item.metadata.name = name
        mock_item.metadata.namespace = '{}-space'.format(name)
        return mock_item

    def test_handles_items(self):
        """Tests that an uninitialized item is handled."""
        initializer_name = 'fooey'

        mock_item = self.mock_item('pendy')
        mock_item.metadata.initializers = V1Initializers(
            pending=[V1Initializer(name=initializer_name),
                     V1Initializer(name='foo')])
        mock_result = self.mock_item('updated')
        mock_result.metadata.initializers = V1Initializers(
            pending=[V1Initializer(name='should_be_deleted')])

        mock_controller = self.mock_resource_controller('ctrl', [mock_item])
        mock_controller.handle_item.return_value = mock_result

        test_controller = InitializerController(initializer_name, [mock_controller])
        test_controller.handle_update()

        mock_controller.update_item.assert_called_once_with(mock_result)
        # mock_result should've had the pending list updated.
        self.assertEqual(mock_result.metadata.initializers.pending, [V1Initializer(name='foo')])

    def test_handles_only_marked_items(self):
        """Tests that only uninitialized items with our initializer listed first are handled."""
        initializer_name = 'fooey'

        # We're an initializer, but not first in the list.
        mock_skipped_1 = self.mock_item('should_skip_1')
        mock_skipped_1.metadata.initializers = V1Initializers(
            pending=[V1Initializer(name='foo'),
                     V1Initializer(name=initializer_name)])
        mock_controller_1 = self.mock_resource_controller('ctrl1', [mock_skipped_1])

        # We're the only initializer.
        mock_handled = self.mock_item('should_handle')
        mock_handled.metadata.initializers = V1Initializers(
            pending=[V1Initializer(name=initializer_name)])
        mock_result = self.mock_item('updated')
        # This should be set to None before update.
        mock_result.metadata.initializers = V1Initializers(
            pending=[V1Initializer(name=initializer_name)])
        mock_controller_2 = self.mock_resource_controller('ctrl2', [mock_handled])
        mock_controller_2.handle_item.return_value = mock_result

        # No initializers.
        mock_skipped_2 = self.mock_item('should_skip_2')
        mock_skipped_2.metadata.initializers = None
        mock_controller_3 = self.mock_resource_controller('ctrl3', [mock_skipped_2])

        test_controller = InitializerController(
            initializer_name, [mock_controller_1, mock_controller_2, mock_controller_3])
        test_controller.handle_update()

        mock_controller_2.update_item.assert_called_once_with(mock_result)
        # mock_result should've had its initializers wiped.
        self.assertEqual(mock_result.metadata.initializers, None)

        # Other controllers should have had items listed, but no items updated.
        mock_controller_1.list_all_items.assert_called()
        mock_controller_1.update_item.assert_not_called()
        mock_controller_3.list_all_items.assert_called()
        mock_controller_3.update_item.assert_not_called()

    def test_updates_with_rejections(self):
        """Tests that rejections are handled correctly."""
        initializer_name = 'fooey'

        # Three items, the middle of which should be rejected.
        mock_skipped_1 = self.mock_item('should_skip_1')
        mock_skipped_1.metadata.initializers = None
        mock_handled = self.mock_item('should_handle')
        mock_handled.metadata.initializers = V1Initializers(
            pending=[V1Initializer(name=initializer_name)])
        mock_skipped_2 = self.mock_item('should_skip_2')
        mock_skipped_2.metadata.initializers = None
        mock_controller = self.mock_resource_controller(
            'ctrl', [mock_skipped_1, mock_handled, mock_skipped_2])
        fake_rejection = Rejection(message='failure!')
        mock_controller.handle_item.side_effect = fake_rejection

        test_controller = InitializerController(initializer_name, [mock_controller])
        test_controller.handle_update()

        mock_controller.update_item.assert_called_once_with(mock_handled)
        # mock_handled should've had its initializers updated with the status.
        self.assertEqual(mock_handled.metadata.initializers.result, fake_rejection.status)
