"""Contains the main method for example handlers."""

import logging
import time

import kubernetes


def main_loop(controller_constructor):
    """
    Build a controller, and run update loop for the initializer.

    This looks for a local kubernetes config file. If you wish to run on a cluster, you'll want to
    replace the load_kube_config call with a load_incluster_config call.

    The update loop is run every 5 seconds. Since create resource requests will block until all
    initializers complete, we want this to be frequent.

    Args:
        controller_constructor: A function that takes a single argument, the kubernetes ApiClient,
            and returns the InitializerController to be run.
    """

    # Format logs in a less-Pythonic way.
    logging.basicConfig(
        level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(name)s:%(lineno)s - %(message)s')

    # Reduce log level for dependency libraries.
    logging.getLogger('kubernetes').setLevel(logging.INFO)

    # Optional: Set the log level for 'ai2.kubernetes.initializer':
    # logging.getLogger('ai2.kubernetes.initializer').setLevel(logging.INFO)

    # Load the Kubernetes configuration from your local kubeconfig file.
    kubernetes.config.load_kube_config()

    api_client = kubernetes.client.api_client.ApiClient()
    controller = controller_constructor(api_client)

    # We want this loop to run frequently enough that clients aren't timing out while waiting for
    # the initializer to complete.
    # This uses a 5-second loop period, but you may wish for a shorter loop.
    while True:
        # A production-quality handler should catch exceptions here.
        controller.handle_update()
        time.sleep(5)


if __name__ == "__main__":
    main()
