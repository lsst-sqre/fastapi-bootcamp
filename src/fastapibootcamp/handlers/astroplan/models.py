"""Web API models for the astroplan router."""

# In a FastAPI application, you'll have lots of Pydantic models or dataclasses.
# These are your "models." It's wise to maintain separate models for different
# areas of your application. In this module we're defining the Pydantic models
# that define the request and response JSON payloads for the web API. Notice
# how the response models have class methods that convert domain (internal)
# models to the web API model. Using this pattern lets you change how data is
# represented internally or in databases without inadverently changing the
# public web API.

from __future__ import annotations

from fastapi import Request
from pydantic import BaseModel, Field

from fastapibootcamp.domain.models import Observer

__all__ = ["ObserverModel"]


class ObserverModel(BaseModel):
    """Model for an observer resource response."""

    id: str = Field(..., description="URL-safe identifier of the site.")

    name: str = Field(..., description="Short name of the observation site.")

    aliases: list[str] = Field(
        description="Aliases for the observation site.", default_factory=list
    )

    local_timezone: str = Field(
        ..., description="Local timezone of the observation site."
    )

    longitude: float = Field(
        description="Longitude of the observation site (degrees)."
    )

    latitude: float = Field(
        description="Latitude of the observation site (degrees)."
    )

    elevation: float = Field(
        description="Elevation of the observation site (meters)."
    )

    self_url: str = Field(description="URL to the observer resource.")

    # This class method consructs the API model for the observer resource
    # from the internal domain, which is astropy's Observer object here.
    # Passing the FastAPI request lets us construct URLs to related resources.

    @classmethod
    def from_domain(
        cls, *, observer: Observer, request: Request
    ) -> ObserverModel:
        """Create a model from an astroplain Observer domain object."""
        return cls(
            id=observer.observer_id,
            name=observer.name,
            aliases=observer.aliases,
            local_timezone=observer.local_timezone,
            longitude=observer.longitude.deg,
            latitude=observer.latitude.deg,
            elevation=observer.elevation.to_value("m"),
            # Including URLs to related responses, and even the response
            # itself, is a good practice. This allows clients to make requests
            # to without having to construct URLs themselves.
            self_url=str(
                request.url_for(
                    "get_observer", observer_id=observer.observer_id
                )
            ),
        )
