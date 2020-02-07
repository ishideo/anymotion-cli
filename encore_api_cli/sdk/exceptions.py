class ClientException(Exception):
    """Base class for exceptions in the SDK package."""


class FileTypeError(ClientException):
    """Raised when trying to use an unallowable file type."""


class RequestsError(ClientException):
    """Raised when an HTTP request fails."""


class ResponseError(ClientException):
    """Raised when an HTTP response is invalid."""
