"""Path operations for the astroplan router."""

from typing import Annotated

from fastapi import APIRouter, Depends
from safir.models import ErrorLocation

from fastapibootcamp.dependencies.requestcontext import (
    RequestContext,
    context_dependency,
)
from fastapibootcamp.exceptions import ObserverNotFoundError

from .models import ObserverModel

astroplan_router = APIRouter()

# The core of a RESTful API is the "resource". In this API, observing sites are
# the resource. This first endpoint lets the user retrieve an existing
# observing site resource by its ID.
#
# e.g. GET /astroplan/observers/rubin


@astroplan_router.get(
    "/observers/{observer_id}",
    summary="Get an observer by site ID.",
    response_model=ObserverModel,
)
async def get_observer(
    observer_id: str,
    context: Annotated[RequestContext, Depends(context_dependency)],
) -> ObserverModel:
    # Use the request context and factory patterns to get an observer service.
    factory = context.factory
    observer_service = factory.create_observer_service()

    try:
        # Run a method on the observer service to get the observer
        observer = await observer_service.get_observer_by_id(observer_id)
    except ObserverNotFoundError as e:
        # The service, and components it calls, can raise exceptions because
        # the user input is invalid. To provide a meaningful error response,
        # the handler augments the exception with information about what
        # user input caused the error.
        #
        # The model for this error message is declared on the router in
        # main.py.
        e.location = ErrorLocation.path
        e.field_path = ["observer_id"]
        raise

    # Transform the domain object into a response object.
    response_data = ObserverModel.from_domain(
        observer=observer, request=context.request
    )
    # Make any modifications to the response headers or status code.
    context.response.headers["Location"] = response_data.self_url

    # Return the response object. FastAPI takes care of serializing it to JSON.
    return response_data
