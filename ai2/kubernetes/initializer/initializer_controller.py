import logging

import kubernetes
from kubernetes.watch.watch import iter_resp_lines
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

    def __init__(self, initializer_name, controllers, request_timeout_seconds=30):
        """
        Builds a InitializerController handling the given initializer name with the given
        controllers.

        Args:
            initializer_name: The name of the initializer in the InitializerConfiguration. Only
                resources returned by the controllers that have this name in their pending
                initializers will be modified (per the dynamic admission controller contract).
            controllers: The ResourceControllers to delegate update logic to.
            request_timeout_seconds: The amount of time to allow requests to be idle before
                reconnecting.
        """
        self.initializer_name = initializer_name
        self.controllers = controllers
        self._request_timeout_seconds = request_timeout_seconds

    def async_handle_updates(self, error_callback):
        """
        Runs an asynchronous update loop, updating all controllers' items as they are created.

        This can be stopped by calling halt_async_handle_updates.

        Args:
            error_callback: The function to invoke with any exception caught.  This should log the
                exception and / or invoke halt_async_handle_items, as desired.
        """

        self._halt = False
        for controller in self.controllers:
            self._async_handle_updates(error_callback, controller)

    def halt_async_handle_updates(self):
        """Stops asynchronous processing of updates."""
        self._halt = True

    def _async_handle_updates(self, error_callback, controller):
        """Runs an asynchronous update loop using the given controller."""

        def handle_response(response):
            """Handles the response of a watch request."""
            try:
                watch = kubernetes.watch.Watch()
                return_type = watch.get_return_type(controller.list_all_items_fn)
                # This will leave a watch connection open indefinitely.
                for line in iter_resp_lines(response):
                    # Stop if requested.
                    if self._halt:
                        return

                    event = watch.unmarshal_event(line, return_type)
                    event_type = event['type']
                    if event_type == 'MODIFIED' or event_type == 'ADDED':
                        item = event['object']
                        self._handle_single_item(controller, item)
                    else:
                        logger.debug('Ignored event type {} for item {}:{}'.format(
                            event_type, item.metadata.namespace, item.metadata.name))
            except urllib3.exceptions.ReadTimeoutError as timeout:
                # This is expected to occur when we hit _request_timeout below. We need to have a
                # request timeout, else we won't detect dropped network connections or restarted API
                # servers.
                logger.debug('Request timeout; ignoring.')
            except Exception as e:
                error_callback(e)
            finally:
                response.close()
                response.release_conn()
            if not self._halt:
                # We expect to break out repeatedly (after every _request_timeout_seconds of idle
                # time).
                controller.list_all_items_fn(
                    include_uninitialized=True,
                    watch=True,
                    callback=handle_response,
                    _request_timeout=self._request_timeout_seconds,
                    _preload_content=False)

        controller.list_all_items_fn(
            include_uninitialized=True,
            watch=True,
            callback=handle_response,
            _request_timeout=self._request_timeout_seconds,
            _preload_content=False)

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
            self._handle_single_item(controller, item)

    def _handle_single_item(self, controller, item):
        """Updates the given item, if needed, using the given controller.

        Args:
            controller: The controller to update the item with.
            item: The item to handle.

        Raises:
            urllib3.exceptions.HTTPError: If any HTTP calls throw an error.
        """
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
