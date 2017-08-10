#!/usr/bin/env python3

from main_loop import main_loop

from ai2.kubernetes.initializer import (InitializerController, Rejection, ResourceHandler,
                                        SimpleResourceController)


def main():
    """
    Runs a controller that requires jobs, deployments, and pods to have a non-empty 'owner' label.
    """

    def handle_item(item):
        """
        Requires that the given item have a non-empty 'owner' label.

        Args:
            item: A Kubernetes object with standard metadata attached.
        """
        if not item.metadata.labels.get('owner'):
            raise Rejection("Label 'owner' missing from {}:{}".format(
                item.metadata.namespace, item.metadata.name), 'MissingOwner')

        # We aren't changing any data, so simply return the item.
        return item

    def build_initializer(api_client):
        # All of our controllers can use the same handler function, since it only operates on
        # top-level metadata. You will probably need separate handler functions for more interesting
        # controllers.
        pod_controller = SimpleResourceController(
            ResourceHandler.pod_handler(api_client), handle_item)
        job_controller = SimpleResourceController(
            ResourceHandler.job_handler(api_client), handle_item)
        deployment_controller = SimpleResourceController(
            ResourceHandler.deployment_handler(api_client), handle_item)
        all_controllers = [pod_controller, job_controller, deployment_controller]
        # The name here should match what you've configurd in your InitializerConfiguration.
        return InitializerController('owner.require.example', all_controllers)

    main_loop(build_initializer)


if __name__ == '__main__':
    main()
