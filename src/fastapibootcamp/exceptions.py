"""Exceptions for the FastAPI Bootcamp app."""

from safir.fastapi import ClientRequestError

__all__ = [
    "ObserverNotFoundError",
]


class ObserverNotFoundError(ClientRequestError):
    """Raised when an observing site is not found."""

    status_code = 404

    error = "unknown_observer"
