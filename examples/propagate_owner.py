#!/usr/bin/env python3

from main_loop import main_loop

from ai2.kubernetes.initializer import (InitializerController, Rejection, ResourceHandler,
                                        SimpleResourceController)


def main():
    """
    Runs a controller that copies 'owner' labels to pods owned by deployments.

    Note: Jobs' templates are immutable, so we can't implement this for them.
    """

    def handle_item(item):
        """
        Updates the given item by copying its 'owner' label to its pod template.

        This requires that the item have a nonempty 'owner' label.

        Args:
            item: A Kubernetes object with a metadata field and a spec.template.metadata field.
        """
        owner = item.metadata.labels.get('owner')
        if not owner:
            raise Rejection("Label 'owner' missing from {}:{}".format(
                item.metadata.namespace, item.metadata.name), 'MissingOwner')

        # Update the item's template. All deployments should have a template with labels; we will
        # update the 'owner' label iff it's not present.
        # If the label is present and doesn't match the deployment's label, raise an error, since we
        # don't want to figure out if it's used in the deployment's selector before mutating.

        template_metadata = item.spec.template.metadata

        if 'owner' not in template_metadata.labels:
            # Set the template's owner label.
            template_metadata.labels['owner'] = owner
        elif template_metadata.labels['owner'] != owner:
            raise Rejection(
                'Template label owner={} does not match Deployment label owner={}'.format(
                    owner, template_metadata.labels['owner']), 'MismatchedOwner')

        # Return the updated / validated item.
        return item

    def build_initializer(api_client):
        # Build the controller.
        deployment_controller = SimpleResourceController(
            ResourceHandler.deployment_handler(api_client), handle_item)
        # The name here should match what you've configurd in your InitializerConfiguration.
        return InitializerController('owner.propagate.example', [deployment_controller])

    main_loop(build_initializer)


if __name__ == '__main__':
    main()
