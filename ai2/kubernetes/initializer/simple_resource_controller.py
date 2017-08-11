from .resource_controller import ResourceController


class SimpleResourceController(ResourceController):
    """
    A ResourceController implementation that delegates handle_item to a provided function.
    """

    def __init__(self, resource_handler, handle_item_function):
        super().__init__(resource_handler)
        self.handle_item = handle_item_function
