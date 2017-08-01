from kubernetes.client.models.v1_status import V1Status


class Rejection(Exception):
    """Exception holding a `status` value for an `initializers.result` initializer rejection.

    This is used only to communicate results back from a ResourceHandler, and is not thrown outside
    of the module.
    """

    def __init__(self, message, reason=None, code=400, details=None):
        """
        Create a Rejection for an item being validated by an initializer.

        Args:
            message: The human-readable message for this failure.
            reason: A machine-readable reason for this failure. Defaults to the value of `message`.
            code: The HTTP status code to use in this response. Defaults to 400 (Bad Request).
            details: A V1StatusDetails instance with more error details.
        """
        super().__init__(message)
        if not reason:
            reason = message
        self.status = V1Status(
            message=message, reason=reason, code=code, details=details, status='Failure')
