"""Handlers for the app's external root, ``/fastapi-bootcamp/``."""

from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from safir.dependencies.logger import logger_dependency
from safir.metadata import Metadata as SafirMetadata
from safir.metadata import get_metadata
from safir.slack.webhook import SlackRouteErrorHandler
from structlog.stdlib import BoundLogger

from fastapibootcamp.dependencies.pagination import (
    Pagination,
    SortOrder,
    pagination_dependency,
)

from ..config import config
from ..dependencies.singletondependency import example_singleton_dependency
from ..exceptions import DemoInternalError

# The APIRouter is what the individual endpoints are attached to. In main.py,
# this external_router is mounted at the path "/fastapi-bootcamp". When we
# deploy this on Kubernetes, that "/fastapi-bootcamp" path is available
# through an Ingress, and therefore becomes available over the internet
# (hence why we call these the external endpoints)
#
# Note the custom route class, SlackRouteErrorHandler. This is a Safir
# API that reports exceptions to a Slack channel. See Lesson 5 for more.

external_router = APIRouter(route_class=SlackRouteErrorHandler)
"""FastAPI router for all external handlers."""


# In the default template, there's a "models" module that holds all Pydantic
# models. For this router, we're going to co-locate models and path operation
# functions in the same module to make the demo easier to follow. For a real
# application, I recommend keeping models in their own module, but instead of
# a single root-level "models" module, keep the API models next to the
# handlers, and have internal models elsewhere in the "domain" and "storage"
# interface subpackages. Keeping a separation between your API, your
# application's internal domain and storage, and models for interfacing with
# other services will make it easier to grow the codebase without
# breaking the API.


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


# =============================================================================
# Lesson 1: A simple GET endpoint.
#
# This function handles a GET request to the /hello endpoint. Since the
# external_router is mounted at "/fastapi-bootcamp" (in main.py), the full URL
# The full path ends up being /fastapi-bootcamp/hello. The function returns
# simple string (*). You can try it out by visiting:
#   http://localhost:8000/fastapi-bootcamp/hello
#
# (*) Well actually, FastAPI is built for JSON APIs and converts return values
# to JSON. So even though we're returning a string, FastAPI will convert it to
# a JSON string object. To return a true string, you can use a
# fastapi.responses.PlainTextResponse object. FastAPI has other specialized
# responses like HTMLResponse, StreamingResponse, and RedirectResponse.
# https://fastapi.tiangolo.com/advanced/custom-response/


@external_router.get("/hello", summary="Get a friendly greeting.")
async def get_greeting() -> str:
    return "Hello, SQuaRE Services Bootcamp!"


# =============================================================================
# Lesson 2: A GET endpoint with a JSON response
#
# In a web API, the response type will typically be a JSON object. With
# FastAPI, you'll model JSON with Pydantic models. Here, GreetingResponseModel
# is a Pydantic model with two JSON fields. The `language` field is an Enum,
# which is a good way to restrict the possible values of a field. We tell
# FastAPI what the model is with the response_model parameter and/or the return
# type annotation.
#
# Try it out by visiting:
#   http://localhost:8000/fastapi-bootcamp/en-greeting


class Language(str, Enum):
    """Supported languages for the greeting endpoint."""

    en = "en"
    es = "es"
    fr = "fr"


class GreetingResponseModel(BaseModel):
    """Response model for the greeting endpoint."""

    greeting: str = Field(..., title="The greeting message")

    language: Language = Field(..., title="Language of the greeting")


@external_router.get(
    "/en-greeting",
    summary="Get a greeting in English.",
    response_model=GreetingResponseModel,
)
async def get_english_greeting() -> GreetingResponseModel:
    return GreetingResponseModel(
        greeting="Hello, SQuaRE Services Bootcamp!", language=Language.en
    )


# =============================================================================
# Lesson 2a: A GET endpoint with a JSON response and query parameters.
#
# To let the user pick the language, we support a query parameter. This is an
# argument to the path function. The type annotation with fastapi.Query
# indicates its a query parameter.
#
# Try it out by visiting:
#   http://localhost:8000/fastapi-bootcamp/greeting?language=es


@external_router.get(
    "/greeting",
    summary="Get a greeting in several languages by using a query parameter.",
    response_model=GreetingResponseModel,
)
async def get_multilingual_greeting(
    language: Annotated[Language, Query()] = Language.en,
) -> GreetingResponseModel:
    """You can get the greeting in English, Spanish, or French."""
    greetings = {
        Language.en: "Hello, SQuaRE Services Bootcamp!",
        Language.es: "¡Hola, SQuaRE Services Bootcamp!",
        Language.fr: "Bonjour, SQuaRE Services Bootcamp!",
    }

    return GreetingResponseModel(
        greeting=greetings[language], language=language
    )


# =============================================================================
# Lesson 2b: A GET endpoint with path parameters.
#
# Path parameters are used to specify a resource in the URL. Let's pretend that
# languages are different resources, and let the user pick the language with a
# path parameter instead of a query parameter.
#
# With path parameters, we template the name of the parameter in the URL path
# and specify its type in the function signature. FastAPI will validate and
# convert the parameter to the correct type and pass it to the function.
#
# Try it out by visiting:
#   http://localhost:8000/fastapi-bootcamp/greeting/en
#
# If you visit the wrong URL, FastAPI will return a 404 error. Try it out by
# visiting:
#   http://localhost:8000/fastapi-bootcamp/greeting/de
#
# Note: Query parameters and path parameters have different use cases in
# RESTful APIs. Path parameters are used to specify a resource, while query
# parameters are used to filter. So although we've interchanged them here for
# demonstration, in real RESTful APIs they have distinct purposes.


@external_router.get(
    "/greeting/{language}",
    summary="Get a greeting in several languages by using a path parameter.",
    response_model=GreetingResponseModel,
)
async def get_multilingual_greeting_path(
    language: Language,
) -> GreetingResponseModel:
    """You can get the greeting in English, Spanish, or French."""
    greetings = {
        Language.en: "Hello, SQuaRE Services Bootcamp!",
        Language.es: "¡Hola, SQuaRE Services Bootcamp!",
        Language.fr: "Bonjour, SQuaRE Services Bootcamp!",
    }

    return GreetingResponseModel(
        greeting=greetings[language], language=language
    )


# =============================================================================
# Lesson 3: A POST endpoint with a JSON request body.
#
# POST requests are used to create a new resource. In RESTful APIs, the request
# body is a JSON object that represents the new resource. FastAPI will
# validate and convert the request body to the correct type and pass it to the
# function.
#
# To send a POST request you need an HTTP client. Curl is a command-line
# app that comes with most platforms:
#  curl -X POST --json '{"name": "Rubin", "language": "en"}' \
#    http://localhost:8000/fastapi-bootcamp/greeting
#
# Older versions of curl may not have the --json flag. In that case, use -H
# to set the Content-Type header:
#  curl -X POST -H "Content-Type: application/json" -d \
#    '{"name": "Rubin", "language": "en"}' \
#    http://localhost:8000/fastapi-bootcamp/greeting
#
# I like to use httpie, a more user-friendly REST API client
# (https://httpie.io/ and 'brew install httpie' or 'pip install httpie'):
#   http post :8000/fastapi-bootcamp/greeting name=Rubin language=en


class GreetingRequestModel(BaseModel):
    """Request model for the greeting POST endpoint."""

    name: str = Field(..., title="Your name")

    language: Language = Field(Language.en, title="Language of the greeting")


@external_router.post(
    "/greeting",
    summary="Get a greeting in several languages using an HTTP POST.",
    response_model=GreetingResponseModel,
)
async def post_greeting(
    data: GreetingRequestModel,
) -> GreetingResponseModel:
    """You can get the greeting in English, Spanish, or French."""
    greeting_templates = {
        Language.en: "Hello, {name}!",
        Language.es: "¡Hola, {name}!",
        Language.fr: "Bonjour, {name}!",
    }

    return GreetingResponseModel(
        greeting=greeting_templates[data.language].format(name=data.name),
        language=data.language,
    )


# =============================================================================
# Lesson 4: Logging
#
# Logging is an important part of any application. With Safir, we use
# structlog to create structured logging. Structured log messages are
# JSON-formatted and let you add fields that are easily searchable and
# fitlerable.
#
# Safir provides a logger as a FastAPI dependency. Dependencies are also
# arguments to FastAPI path operation functions, set up with FastAPI's Depends
# function.
#
# Try it out while looking at the console output for `tox run -e run`:
#   http post :8000/fastapi-bootcamp/log-demo name=Rubin language=en
@external_router.post(
    "/log-demo", summary="Log a message.", response_model=GreetingResponseModel
)
async def post_log_demo(
    data: GreetingRequestModel,
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
) -> GreetingResponseModel:
    # With structlog, keyword argumemnts become fields in the log message.
    #
    # Why model_dump(mode="json")? This gives us a dict, but serializes the
    # values the same way they would be in JSON. This formats the Enum values
    # as strings.
    logger.info("The log message", payload=data.model_dump(mode="json"))

    # You can "bind" fields to a logger to include them in all log messages.
    # This is useful for establishing context. Safir binds some data for you
    # like the request_id and Gafaelfawer user ID (if available).
    logger = logger.bind(name=data.name, language=data.language)
    logger.info("The log message with bound fields")
    logger.info("Another log message with bound fields")

    greeting_templates = {
        Language.en: "Hello, {name}!",
        Language.es: "¡Hola, {name}!",
        Language.fr: "Bonjour, {name}!",
    }

    return GreetingResponseModel(
        greeting=greeting_templates[data.language].format(name=data.name),
        language=data.language,
    )


# =============================================================================
# Lesson 5: Handling internal errors
#
# Sometimes things go wrong in your application. A database doesn't respond,
# an external service is down, or some bug in your code causes an exception.
# By default, FastAPI returns a 500 Internal Server Error response when an
# uncaught exception occurs. Safir provides the ability to report these
# uncaught errors to a Slack channel through an incoming webhook.
#
# To hook up this Slack reporting, you need to take the following steps:
#
# 1. Add a slack_webhook_url field to the configuration (config.py)
# 2. In main.py, configure SlackRouteErrorHandler
# 3. Add SlackRouteErrorHandler to the APIRouter in your handlers/endpoints
#    module to automatically report any uncaught exception to Slack.
# 4. Optionally, create custom SlackException subclasses for your application
#    (usually in exceptions.py). Custom exceptions are great adding extra
#    information to the error message, but you can also raise other
#    exceptions too.
# 5. Raise these exceptions in your application code
#
# If your error is caused by user input, you typically don't want to report
# it to Slack, but instead to the user. In the astroplan application we'll
# explore the ClientRequestError exception for this purpose in
# handlers/astroplan/endpoints.py's get_observer function.
#
# Try it out:
#   http post :8000/fastapi-bootcamp/error-demo custom_error:=true
#
# Compare this to raising a "regular" exception:
#   http post :8000/fastapi-bootcamp/error-demo custom_error:=false


class ErrorRequestModel(BaseModel):
    """Request model for the error POST endpoint."""

    custom_error: bool = Field(
        True, title="If true, raise the custom SlackException."
    )


@external_router.post(
    "/error-demo", summary="Raise an internal service exception."
)
async def post_error_demo(data: ErrorRequestModel) -> JSONResponse:
    """Use the custom_error field to compare the difference between raising
    a custom SlackException and a generic exception.
    """
    if data.custom_error:
        raise DemoInternalError(
            "A custom error occurred.", custom_data="Hello error!"
        )

    raise RuntimeError("A generic error occurred.")


# =============================================================================
# Lesson 6: Custom dependencies
#
# FastAPI dependencies are a way to add reusable code to your path operation
# that's aware of the current request. Safir provides several dependencies,
# see https://safir.lsst.io/api.html#module-safir.dependencies.arq etc.
#
# - arq_dependency provides a client to the Arq distributed job queue
# - db_session_dependency provides a SQLAlchemy session
# - auth_delegated_token_dependency provides a delegated token
# - auth_dependency provides info about the current user
# - auth_logger_dependency provides a logger with user info bound
# - http_client_dependency provides an HTTPX async client
# - logger_dependency provides a structlog logger (see Lesson 4)
#
# Besides these, you can create your own dependencies. In the astroplan
# application we'll explore the request context dependency pattern.
#
# There are two types of dependencies you'll develop:
#
# - functional dependencies that are scoped to the current request
# - singleton class-based dependencies that can hold
#   persistent state that's reused across multiple requests.
#
# Try it out:
#   http get :8000/fastapi-bootcamp/dependency-demo X-Custom-Header:foo

# See src/fastapibootcamp/dependencies/singletondependency.py for the
# dependency that holds a persistent value. Below is a functional dependency:


class DependencyDemoResponseModel(BaseModel):
    """Response model for the dependency demo endpoint."""

    page: int = Field(
        ..., title="The page number from the pagination.", examples=[1, 2, 3]
    )

    limit: int = Field(
        ..., title="The limit from the pagination.", examples=[10, 20, 50]
    )

    order: SortOrder = Field(
        ...,
        title="The order from the pagination.",
        examples=[SortOrder.asc, SortOrder.desc],
    )

    persistent_value: str = Field(
        ...,
        title="A persistent value provided by the dependency.",
        examples=["crafty sloth"],
    )


@external_router.get(
    "/dependency-demo",
    summary="Demonstrate custom dependencies.",
    response_model=DependencyDemoResponseModel,
)
async def get_dependency_demo(
    # This is the functional dependency defined in
    # src/fastapibootcamp/dependencies/pagination.py. It adds pagination
    # query string parameters to a FastAPI path operation. Look at the
    # generated API documentation to see that the documentation from the
    # dependency is included in this endpoint's documentation.
    pagination: Annotated[Pagination, Depends(pagination_dependency)],
    # This is the singleton class-based dependency defined in
    # src/fastapibootcamp/dependencies/singletondependency.py
    persistent_value: Annotated[str, Depends(example_singleton_dependency)],
    # This is a dependency from Safir
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
) -> DependencyDemoResponseModel:
    logger.info(
        "Dependency demo",
        pagination=pagination,
        persistent_value=persistent_value,
    )

    return DependencyDemoResponseModel(
        page=pagination.page,
        limit=pagination.limit,
        order=pagination.order,
        persistent_value=persistent_value,
    )


# =============================================================================
# This covers the basics of writing endpoints in FastAPI. Next, we'll explore
# how to structure a larger application with an API/service/storage/domain
# architecture. We'll see you there at src/fastapibootcamp/handlers/astroplan.
