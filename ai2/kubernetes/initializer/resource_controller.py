from .rejection import Rejection


class ResourceController(object):
    """
    A ResourceController is responsible for all logic to accept or reject an uninitialized resource.

    Subclasses should override handle_item.
    """

    def __init__(self, resource_handler):
        """Construct a resource controller wrapping the given handler."""
        self._resource_handler = resource_handler

    @property
    def name(self):
        """The name of the resource type being handled."""
        return self._resource_handler.name

    def list_all_items(self):
        """Returns the list of all items of the handled type in the Kubernetes server."""
        return self._resource_handler.list_all_items()

    def update_item(self, item):
        """
        Sends an update for the given item to the Kubernetes API.

        Args:
            item: The updated item to send. This must have valid metadata.

        Returns:
            The response from the API server to the request.
        """
        return self._resource_handler.update_item(item)

    def handle_item(self, item):
        """
        Given a resource item, either return the item for admission, or raise a Rejection.

        The caller is responsible for updating the item's `initializers` object, so it should be
        returned unchanged.

        Args:
            item: The item under consideration by the admission controller.

        Returns:
            The item to post back to the Kubernetes API. This should be the provided item, with any
            modifications made.

        Raises:
            Rejection: The reason for rejecting the item from the Kubernetes cluster. If this is
                raised, the caller will populate `initializers.result` with a `Failed` value holding
                the contents of this exception.
        """
        raise Rejection(
            message='Handler not implemented; rejecting {}.'.format(item.metadata.name),
            reason='RejectAll')
