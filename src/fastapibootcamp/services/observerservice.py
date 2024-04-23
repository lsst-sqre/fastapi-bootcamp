"""The observer service."""

from __future__ import annotations

from structlog.stdlib import BoundLogger

from ..domain.models import Observer
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
        self, name_pattern: str | None = None
    ) -> list[Observer]:
        """Get all observers, possibly filtering on attributes.

        Parameters
        ----------
        name_pattern
            A pattern to match against observer names.

        Returns
        -------
        list of Observer
            Observers that match any query patterns, or all observers if no
            query is provided.
        """
        return await self._observer_store.get_observers(
            name_pattern=name_pattern
        )
