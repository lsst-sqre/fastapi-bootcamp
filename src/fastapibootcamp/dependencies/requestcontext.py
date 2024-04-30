"""Request context FastAPI dependency."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import Depends, Request, Response
from httpx import AsyncClient
from safir.dependencies.http_client import http_client_dependency
from safir.dependencies.logger import logger_dependency
from structlog.stdlib import BoundLogger

from ..factory import Factory

# This RequestContext dataclass is what will be provided by the
# context_dependency FastAPI dependency. This is a useful pattern that wraps
# up multiple FastAPI dependencies into one container, and is a useful
# place to put methods that work on those dependencies (e.g., like
# binding context to the logger.
#
# The RequestContext would hold the sqlalchemy Session for apps that use
# databases, or a Redis client, etc.


@dataclass
class RequestContext:
    """Holds the incoming request and its surrounding context.

    The primary reason for the existence of this class is to allow the
    functions involved in request processing to repeatedly rebind the request
    logger to include more information, without having to pass both the
    request and the logger separately to every function.
    """

    request: Request
    """The incoming request."""

    response: Response
    """The response to be returned.

    The response can be modified to include additional headers or status codes.
    """

    logger: BoundLogger
    """The request logger, rebound with discovered context."""

    http_client: AsyncClient
    """The HTTPX async HTTP client."""

    factory: Factory
    """The component factory."""

    def rebind_logger(self, **values: Any) -> None:
        """Add the given values to the logging context.

        Also updates the logging context stored in the request object in case
        the request context later needs to be recreated from the request.

        Parameters
        ----------
        **values
            Additional values that should be added to the logging context.
        """
        self.logger = self.logger.bind(**values)


# This is the FastAPI dependency that provides the RequestContext. Notice
# how dependency function signatures look like FastAPI path operations.
# This context dependency takes the request and response arguemnts available
# to path operations, and also depends on other dependencies.


async def context_dependency(
    request: Request,
    response: Response,
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
    http_client: Annotated[AsyncClient, Depends(http_client_dependency)],
) -> RequestContext:
    """Provide a RequestContext as a dependency."""
    return RequestContext(
        request=request,
        response=response,
        logger=logger,
        http_client=http_client,
        factory=Factory(logger=logger, http_client=http_client),
    )
