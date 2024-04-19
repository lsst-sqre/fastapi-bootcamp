"""The main application factory for the fastapi-bootcamp service.

Notes
-----
Be aware that, following the normal pattern for FastAPI services, the app is
constructed when this module is loaded and is not deferred until a function is
called.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from importlib.metadata import metadata, version

from fastapi import FastAPI
from safir.dependencies.http_client import http_client_dependency
from safir.fastapi import ClientRequestError, client_request_error_handler
from safir.logging import configure_logging, configure_uvicorn_logging
from safir.middleware.x_forwarded import XForwardedMiddleware
from safir.models import ErrorModel

# Notice how the the config instance is imported early so it's both
# instantiated on app start-up and available to set up the app.
from .config import config
from .handlers.astroplan import astroplan_router
from .handlers.external import external_router
from .handlers.internal import internal_router

__all__ = ["app", "config"]

# The lifespan context manager is used to set up and tear down anything that
# lives for the duration of the application. This is where you would put
# database connections, etc.


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Set up and tear down the application."""
    # Any code here will be run when the application starts up.

    yield

    # Any code here will be run when the application shuts down.
    await http_client_dependency.aclose()


# The Safir library helps you set up logging around structlog,
# https://www.structlog.org/en/stable/

configure_logging(
    profile=config.profile,
    log_level=config.log_level,
    name="fastapibootcamp",
)
configure_uvicorn_logging(config.log_level)

# The FastAPI application is created here. In our Docker image, we run the
# application by running the Uvicorn server that points to the `app` instance
# in this module.

app = FastAPI(
    title="fastapi-bootcamp",
    description=metadata("fastapi-bootcamp")["Summary"],
    version=version("fastapi-bootcamp"),
    openapi_url=f"{config.path_prefix}/openapi.json",
    docs_url=f"{config.path_prefix}/docs",
    redoc_url=f"{config.path_prefix}/redoc",
    lifespan=lifespan,
)
"""The main FastAPI application for fastapi-bootcamp."""

# Attach the routers to the FastAPI application.
# Each router is associated with path operation functions (HTTP endpoints).
# Generally different routers are grouped around different URL path prefixes.
# The internal router doesn't have a URL path prefix. It isn't exposed to the
# internet since the Kubernetes Ingress typically routes to a path. We use
# this for health checks and internal monitoring.
app.include_router(internal_router)
# The external router is the main router for the service. It has a URL path
# prefix that is the same as the Kubernetes Ingress path. Generally your REST
# API will be built around this external router.
app.include_router(external_router, prefix=f"{config.path_prefix}")
# We're building a more "realistic" demonstration API around the Astroplan
# package. To help keep the code organized, we've created a separate router,
# but you generally won't do this for your own apps.
app.include_router(
    astroplan_router,
    prefix=f"{config.path_prefix}/astroplan",
    # Common errors are modelled around Safir's ErrorModel class, so we can
    # set that here for all endpoints on this router.
    responses={
        404: {"description": "Not found", "model": ErrorModel},
    },
)

# Add middleware.
app.add_middleware(XForwardedMiddleware)

# Add exception handler for Safir's ClientRequestError.
app.exception_handler(ClientRequestError)(client_request_error_handler)
