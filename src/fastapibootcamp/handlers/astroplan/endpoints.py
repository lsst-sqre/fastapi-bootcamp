"""Path operations for the astroplan router."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from safir.models import ErrorLocation

from fastapibootcamp.dependencies.requestcontext import (
    RequestContext,
    context_dependency,
)
from fastapibootcamp.exceptions import ObserverNotFoundError

from .models import (
    ObservabilityResponseModel,
    ObservationRequestModel,
    ObserverModel,
)

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


# RESTFul APIs commonly let clients list all resources of a type, usually
# in conjunction with filtering. This endpoint lets the user list all
# observing sites, optionally filtering by name or alias.
#
# e.g. GET /astroplan/observers?name=rubin
#
# Note: in a production you'll usually implement "pagination" to limit the
# response size. This isn't done here, but could be a good exercise for
# an advanced bootcamp class.


@astroplan_router.get(
    "/observers",
    summary="Get all observering sites.",
    response_model=list[ObserverModel],
)
async def get_observers(
    context: Annotated[RequestContext, Depends(context_dependency)],
    name_pattern: Annotated[
        str | None,
        Query(
            alias="name",
            description="Filter by observing site name or alias.",
            examples=["rubin", "lsst", "gemini"],
        ),
    ] = None,
) -> list[ObserverModel]:
    factory = context.factory
    observer_service = factory.create_observer_service()

    observers = await observer_service.get_observers(name_pattern=name_pattern)

    return [
        ObserverModel.from_domain(observer=observer, request=context.request)
        for observer in observers
    ]


# This is a POST endpoint. A POST request lets the client send a JSON payload.
# Often this is used to create a new resource, but in this case we're using it
# to trigger a calculation that's too complex to be done in a query string.
#
# e.g. POST /astroplan/observers/rubin/observable


@astroplan_router.post(
    "/observers/{observer_id}/observable",
    summary=(
        "Check if a coordinate is observable for an observer at a given time."
    ),
    response_model=ObservabilityResponseModel,
)
async def post_observable(
    observer_id: str,
    request_data: ObservationRequestModel,
    context: Annotated[RequestContext, Depends(context_dependency)],
) -> ObservabilityResponseModel:
    factory = context.factory
    observer_service = factory.create_observer_service()

    observability = await observer_service.get_target_observability(
        observer_id=observer_id,
        sky_coord=request_data.get_target(),
        time=request_data.time,
    )

    return ObservabilityResponseModel.from_domain(
        observability=observability, request=context.request
    )
