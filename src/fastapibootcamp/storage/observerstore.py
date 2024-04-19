"""The storage for observer objects."""

from __future__ import annotations

import json
from pathlib import Path

import astropy.units as u
from astropy.coordinates import EarthLocation
from slugify import slugify
from structlog.stdlib import BoundLogger

from ..domain.models import Observer

# The storage layer is where your application gets and stores data in external
# systems. Often the store will be a database (SQLAlchemy, Redis, etc.).
# It can also be other web APIs. In a store, you'll have methods for getting
# and storing the domain models. The store might adapt your application's
# internal domain models into the format required by the external system,
# like a SQLAlchemy ORM model or a JSON object for a web API.
#
# For this bootcamp application, we don't want to have external depednencies
# so we'll pretend that astroplan has a database, and use the store to get
# "Observer" domain objects.


class ObserverStore:
    """A store for Astroplan observer objects.

    Parameters
    ----------
    logger
        The structlog logger.
    """

    def __init__(self, logger: BoundLogger) -> None:
        self._logger = logger

        # For this demo, we're loading the data from a JSON file embedded in
        # the app to avoid the complexity of a database. Sometimes stores
        # actually are text files from configuration; in that case you'd
        # set the path to that data in the app's configuration and have a
        # classmethod constructor for the store that loads the data from
        # that location.
        site_data = json.loads(
            Path(__file__).parent.joinpath("sites.json").read_text()
        )
        self._sites = {slugify(key): value for key, value in site_data.items()}

    async def get_observer_by_id(self, observer_id: str) -> Observer | None:
        """Get an observer from the store.

        Parameters
        ----------
        observer_id
            The ID of the observer to get. This is the URL-safe slug.

        Returns
        -------
        Observer or None
            The observer object. If the observer is not found, returns None.
        """
        site_info = self._sites.get(observer_id)
        if site_info is None:
            return None

        location = EarthLocation.from_geodetic(
            site_info["longitude"] * u.Unit(site_info["longitude_unit"]),
            site_info["latitude"] * u.Unit(site_info["latitude_unit"]),
            site_info["elevation"] * u.Unit(site_info["elevation_unit"]),
        )
        name = site_info["name"]
        return Observer(
            observer_id=observer_id,
            location=location,
            name=name,
            aliases=site_info["aliases"],
            local_timezone=site_info["timezone"],
        )

    def _get_observer_ids(self) -> list[str]:
        """Get the sorted list of ID of all observers in the Astropy site
        store.
        """
        return sorted(self._sites.keys())
