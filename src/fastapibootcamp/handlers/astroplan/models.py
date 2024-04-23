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

from datetime import datetime
from typing import Self

from astropy.coordinates import SkyCoord
from fastapi import Request
from pydantic import BaseModel, Field, field_validator, model_validator
from safir.datetime import current_datetime
from safir.pydantic import normalize_isodatetime

from fastapibootcamp.domain.models import Observer, TargetObservability

__all__ = [
    "ObserverModel",
    "ObservationRequestModel",
    "ObservabilityResponseModel",
]


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


class ObservationRequestModel(BaseModel):
    """Model for an observation request."""

    ra: str = Field(
        ...,
        description="Target right ascension (HHhMMmSSs).",
        examples=["5h23m34.6s"],
    )

    dec: str = Field(
        ...,
        description="Target declination (DDdMMmSSm).",
        examples=["-69d45m22s"],
    )

    time: datetime = Field(
        description="Time of the observation. Defaults to now if unset.",
        default_factory=current_datetime,
    )

    # This ensures that the time is always provided in UTC.

    _normalize_time = field_validator("time", mode="before")(
        normalize_isodatetime
    )

    @model_validator(mode="after")
    def validate_coordinate(self) -> Self:
        # Validate ra and dec by try to parse them into an astropy SkyCoord
        # object. If they're invalid, this will raise a ValueError.
        try:
            self.get_target()
        except Exception as e:
            raise ValueError(
                f"Invalid coordinates: ra={self.ra}, dec={self.dec}"
            ) from e
        return self

    def get_target(self) -> SkyCoord:
        """Get the target RA and Dec as an astropy SkyCoord."""
        return SkyCoord(
            self.ra,
            self.dec,
            frame="icrs",
        )


class ObservabilityResponseModel(BaseModel):
    """Model for an observability response."""

    ra: str = Field(
        ...,
        description="Target right ascension (HHhMMmSSs).",
        examples=["5h23m34.6s"],
    )

    dec: str = Field(
        ...,
        description="Target declination (DDdMMmSSm).",
        examples=["-69d45m22s"],
    )

    time: datetime = Field(
        ...,
        description="Time of the observation (UTC).",
    )

    is_night: bool = Field(
        ...,
        description="Whether it is night time at the time of the observation.",
    )

    above_horizon: bool = Field(
        ..., description="Whether the target is above the horizon."
    )

    airmass: float | None = Field(
        None, description="Airmass of the target (null if below horizon)."
    )

    alt: float = Field(..., description="Altitude of the target (degrees).")

    az: float = Field(..., description="Azimuth of the target (degrees).")

    moon_separation: float = Field(
        ..., description="Separation from the moon (degrees)."
    )

    moon_illumination: float = Field(
        ..., description="Illumination of the moon (fraction)."
    )

    observer_url: str = Field(..., description="URL to the observer resource.")

    @classmethod
    def from_domain(
        cls, *, observability: TargetObservability, request: Request
    ) -> ObservabilityResponseModel:
        """Create a model from a TargetObservability domain object."""
        return cls(
            ra=observability.target.ra.to_string(unit="hourangle"),
            dec=observability.target.dec.to_string(unit="degree"),
            time=observability.time,
            above_horizon=observability.is_above_horizon,
            is_night=observability.is_night,
            airmass=observability.airmass,
            alt=observability.altaz.alt.deg,
            az=observability.altaz.az.deg,
            moon_separation=observability.moon_separation.deg,
            moon_illumination=observability.moon_illumination,
            observer_url=str(
                request.url_for(
                    "get_observer",
                    observer_id=observability.observer.observer_id,
                )
            ),
        )
