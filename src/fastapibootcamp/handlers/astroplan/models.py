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
from urllib.parse import urlencode

from astropy.coordinates import SkyCoord
from fastapi import Request
from pydantic import BaseModel, Field, field_validator, model_validator
from safir.datetime import current_datetime
from safir.pydantic import normalize_isodatetime

from fastapibootcamp.dependencies.pagination import SortOrder
from fastapibootcamp.domain.models import (
    Observer,
    ObserversPage,
    TargetObservability,
)

__all__ = [
    "ObserverModel",
    "ObservationRequestModel",
    "ObservabilityResponseModel",
]


class ObserverModel(BaseModel):
    """Model for an observer resource response."""

    id: str = Field(
        ...,
        description="URL-safe identifier of the site.",
        examples=["rubin", "rubin-auxtel"],
    )

    name: str = Field(
        ...,
        description="Short name of the observation site.",
        examples=["Rubin Observatory"],
    )

    aliases: list[str] = Field(
        description="Aliases for the observation site.",
        default_factory=list,
        examples=[["LSST", "LSST 8.4m", "Rubin"]],
    )

    local_timezone: str = Field(
        ...,
        description="Local timezone of the observation site.",
        examples=["Chile/Continental"],
    )

    longitude: float = Field(
        description="Longitude of the observation site (degrees).",
        examples=[-70.74772222222225],
    )

    latitude: float = Field(
        description="Latitude of the observation site (degrees).",
        examples=[-30.244633333333333],
    )

    elevation: float = Field(
        description="Elevation of the observation site (meters).",
        examples=[2662.75],
    )

    self_url: str = Field(description="URL to the observer resource.")

    # This class method consructs the API model for the observer resource
    # from the internal domain, which is astropy's Observer object here.
    # Passing the FastAPI request lets us construct URLs to related resources.

    @classmethod
    def from_domain(cls, *, observer: Observer, request: Request) -> Self:
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


class PaginationModel(BaseModel):
    """Model for collection pagination information."""

    total: int = Field(..., description="Total number of resources.")

    page: int = Field(..., description="Page number.")

    limit: int = Field(
        ..., description="Limit to number of resources per page."
    )

    next_url: str | None = Field(
        None, description="URL to the next page of resources."
    )

    prev_url: str | None = Field(
        None, description="URL to the previous page of resources."
    )


class ObserverCollectionResponseModel(BaseModel):
    """Model for a collection of observer resources."""

    data: list[ObserverModel] = Field(
        ..., description="List of observer resources."
    )

    pagination: PaginationModel = Field(
        ..., description="Pagination information."
    )

    # This class method constructs the API model for the observer collection
    # response from the internal domain, which is a list of astropy Observer
    # objects here. Passing the FastAPI request lets us construct URLs to
    # related resources.

    @classmethod
    def from_domain(
        cls,
        *,
        observers_page: ObserversPage,
        request: Request,
        name_pattern: str | None,
    ) -> Self:
        """Create a model from an ObserversPage domain object."""
        return cls(
            data=[
                ObserverModel.from_domain(observer=observer, request=request)
                for observer in observers_page.observers
            ],
            pagination=PaginationModel(
                total=observers_page.total,
                page=observers_page.page,
                limit=observers_page.limit,
                next_url=cls._next_url(observers_page, request, name_pattern),
                prev_url=cls._prev_url(observers_page, request, name_pattern),
            ),
        )

    @classmethod
    def _next_url(
        cls,
        observers_page: ObserversPage,
        request: Request,
        name_pattern: str | None,
    ) -> str | None:
        """Get the URL to the next page of observers."""
        next_page = (
            observers_page.page + 1
            if (observers_page.page * observers_page.limit)
            < observers_page.total
            else None
        )
        return cls._url_for_page(
            limit=observers_page.limit,
            request=request,
            page=next_page,
            name_pattern=name_pattern,
            sort_ascending=observers_page.sort_ascending,
        )

    @classmethod
    def _prev_url(
        cls,
        observers_page: ObserversPage,
        request: Request,
        name_pattern: str | None,
    ) -> str | None:
        """Get the URL to the previous page of observers."""
        prev_page = (
            observers_page.page - 1 if observers_page.page > 1 else None
        )
        return cls._url_for_page(
            limit=observers_page.limit,
            request=request,
            page=prev_page,
            name_pattern=name_pattern,
            sort_ascending=observers_page.sort_ascending,
        )

    @classmethod
    def _url_for_page(
        cls,
        *,
        limit: int,
        request: Request,
        page: int | None = None,
        sort_ascending: bool = True,
        name_pattern: str | None = None,
    ) -> str | None:
        """Get the URL for a specific page of observers."""
        if page is None:
            return None

        base_url = request.url_for("get_observers")
        query_params = {
            "limit": limit,
            "page": page,
            "order": SortOrder.asc.value
            if sort_ascending
            else SortOrder.desc.value,
        }
        if name_pattern:
            query_params["name"] = name_pattern
        return f"{base_url}?{urlencode(query_params)}"


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
        examples=["2024-04-24T00:00:00Z"],
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
        examples=["2024-04-24T00:00:00Z"],
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
    ) -> Self:
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
