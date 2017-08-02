"""
Exceptions used by the initializer module.

Exports:
    InitializerError: The base exception for this module. All exceptions inherit from this, apart
        from Rejection, which inherits from Exception.
    HttpError: Wraps exceptions from urllib3.
"""


class InitializerError(Exception):
    """Base exception for all errors thrown by this module."""
    pass


class HttpError(InitializerError):
    """
    Exception thrown when an urllib3 HTTPError is encountered.

    The wrapped exception is available as the http_error field.
    """

    def __init__(self, message, http_error):
        super().__init__(message)
        self.http_error = http_error
