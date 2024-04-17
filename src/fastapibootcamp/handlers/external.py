"""Handlers for the app's external root, ``/fastapi-bootcamp/``."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from safir.dependencies.logger import logger_dependency
from safir.metadata import Metadata as SafirMetadata
from safir.metadata import get_metadata
from structlog.stdlib import BoundLogger

from ..config import config

__all__ = ["get_index", "external_router"]

external_router = APIRouter()
"""FastAPI router for all external handlers."""


# In the default template there's a "models" module that defines the Pydantic
# models. For this router, we're going to co-locate models and path operation
# function in the same module to make the demo easier to follow. For a real
# application, I recommend keeping models in their own module, but instead of
# a single root-level "models" module, keep the API models next to the
# handlers, and have internal models elsewhere in the "domain" and "storage"
# interface subpackages.


class Index(BaseModel):
    """Metadata returned by the external root URL of the application.

    Notes
    -----
    As written, this is not very useful. Add additional metadata that will be
    helpful for a user exploring the application, or replace this model with
    some other model that makes more sense to return from the application API
    root.
    """

    metadata: SafirMetadata = Field(..., title="Package metadata")


@external_router.get(
    "/",
    description=(
        "Document the top-level API here. By default it only returns metadata"
        " about the application."
    ),
    response_model=Index,
    response_model_exclude_none=True,
    summary="Application metadata",
)
async def get_index(
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
) -> Index:
    """GET ``/fastapi-bootcamp/`` (the app's external root).

    Customize this handler to return whatever the top-level resource of your
    application should return. For example, consider listing key API URLs.
    When doing so, also change or customize the response model in
    `fastapibootcamp.models.Index`.

    By convention, the root of the external API includes a field called
    ``metadata`` that provides the same Safir-generated metadata as the
    internal root endpoint.
    """
    # There is no need to log simple requests since uvicorn will do this
    # automatically, but this is included as an example of how to use the
    # logger for more complex logging.
    logger.info("Request for application metadata")

    metadata = get_metadata(
        package_name="fastapi-bootcamp",
        application_name=config.name,
    )
    return Index(metadata=metadata)
