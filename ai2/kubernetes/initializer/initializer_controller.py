import logging
import urllib3

from .exceptions import HttpError
from .rejection import Rejection

logger = logging.getLogger(__name__)


class InitializerController(object):
    """
    InitializerController is responsible for delegating validation logic to type-specific
    controllers.

    This handles the core initializer logic, matching the initializer list for retrieved resources
    against the configured initializer name, while delegating API calls and logic to the
    sub-controller.

    The entry method is handle_update, which runs a single lookup-update loop over all controllers.
    """

    def __init__(self, initializer_name, controllers):
        """
        Builds a InitializerController handling the given initializer name with the given
        controllers.

        Args:
            initializer_name: The name of the initializer in the InitializerConfiguration. Only
                resources returned by the controllers that have this name in their pending
                initializers will be modified (per the dynamic admission controller contract).
            controllers: The ResourceControllers to delegate update logic to.
        """
        self.initializer_name = initializer_name
        self.controllers = controllers

    def handle_update(self):
        """Finds and updates all items in need of update, using the wrapped controllers.

        Raises:
            initializer.HttpError: If an HTTP error is encountered.
        """
        try:
            for controller in self.controllers:
                self._handle_single_update(controller)
        except urllib3.exceptions.HTTPError as http_error:
            raise HttpError('Error talking to Kubernetes', http_error) from http_error

    def _handle_single_update(self, controller):
        """Finds and updates all items in need of update, using the given controller.

        Args:
            controller: The controller to fetch items from and run updates with.

        Raises:
            urllib3.exceptions.HTTPError: If any HTTP calls throw an error.
        """
        result = controller.list_all_items()
        # TODO(jkinkead): Validate `result`? It's unclear if ALL errors will result in an HTTPError,
        # or if some will result in a response field indicating an error.
        logger.debug('Got %s results from %s lookup.', len(result.items), controller.name)
        for item in result.items:
            initializers = item.metadata.initializers
            if (initializers and initializers.pending
                    and initializers.pending[0].name == self.initializer_name):
                logger.debug('Processing %s %s:%s.', controller.name, item.metadata.namespace,
                             item.metadata.name)
                try:
                    updated_item = controller.handle_item(item)
                    logger.debug('Controller returned a value.')
                except Rejection as rejection:
                    logger.debug('Controller rejected.')
                    # Update the unmodified item, using the provided rejection reason.
                    updated_item = item
                    updated_item.metadata.initializers.result = rejection.status
                # The API contract is to clear `initializers` completely if we had a successful run
                # and we're the last initializer.
                updated_initializers = updated_item.metadata.initializers
                if not updated_initializers.result and len(initializers.pending) == 1:
                    # Successful run and no more initializers; clear the initializers object.
                    updated_item.metadata.initializers = None
                else:
                    # There are more initializers, or we saw an error. Update the list to remove the
                    # first item.
                    updated_initializers.pending = initializers.pending[1:]

                # Save the results back to the server.
                controller.update_item(updated_item)
