"""The observer service."""

from __future__ import annotations

from datetime import datetime

from astropy.coordinates import SkyCoord
from structlog.stdlib import BoundLogger

from fastapibootcamp.dependencies.pagination import Pagination

from ..domain.models import Observer, ObserversPage, TargetObservability
from ..exceptions import ObserverNotFoundError
from ..storage.observerstore import ObserverStore

# The service layer is what orchestrates the application's "business logic".
# By orchestration, we mean that the service layer will get data from the
# storage layer, call the domain to do the actual work, and then store that
# result and/or return a domain object to the caller.
#
# The service layer helps separate your application's domain from the web API.
# In fact, the service layer could also be called by a command-line interface,
# be run through an async task queue like arq or celery, or of course be called
# in tests.


class ObserverService:
    """A service to orchestrating the Astroplan observer domain."""

    def __init__(
        self, *, observer_store: ObserverStore, logger: BoundLogger
    ) -> None:
        self._logger = logger
        self._observer_store = observer_store

    async def get_observer_by_id(self, observer_id: str) -> Observer:
        """Get an observer by site ID."""
        observer = await self._observer_store.get_observer_by_id(observer_id)
        if observer is None:
            raise ObserverNotFoundError(observer_id)
        return observer

    async def get_observers(
        self,
        *,
        name_pattern: str | None = None,
        pagination: Pagination,
    ) -> ObserversPage:
        """Get observers, possibly filtering on attributes.

        Parameters
        ----------
        name_pattern
            A pattern to match against observer names.
        pagination
            The pagination parameters.

        Returns
        -------
        list of Observer
            Observers that match any query patterns, or all observers if no
            query is provided.
        """
        return await self._observer_store.get_observers(
            name_pattern=name_pattern,
            pagination=pagination,
        )

    async def get_target_observability(
        self, observer_id: str, sky_coord: SkyCoord, time: datetime
    ) -> TargetObservability:
        """Get the observability of a target for an observer.

        Parameters
        ----------
        observer_id
            The ID of the observer.
        sky_coord
            The target's coordinates.
        time
            The time of observation.

        Returns
        -------
        TargetObservability
            The observability domain model based on observer, target, and time.
        """
        observer = await self.get_observer_by_id(observer_id)
        return TargetObservability.compute(
            observer=observer, target=sky_coord, time=time
        )
