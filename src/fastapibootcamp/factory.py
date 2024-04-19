"""Component factory for the application."""

from httpx import AsyncClient
from structlog.stdlib import BoundLogger

from .services.observerservice import ObserverService
from .storage.observerstore import ObserverStore

# Your FastAPI app will have a lot of components: services, and stores. The
# Factory is a convenient pattern for creating these components. For example
# a service might need a store, so the factory can encapsululate the
# pattern of creating both.


class Factory:
    """A factory for the application components."""

    def __init__(
        self, *, logger: BoundLogger, http_client: AsyncClient
    ) -> None:
        self.logger = logger
        self.http_client = http_client

    def create_observer_service(self) -> ObserverService:
        """Create an observer service."""
        return ObserverService(
            logger=self.logger, observer_store=self.create_observer_store()
        )

    def create_observer_store(self) -> ObserverStore:
        """Create an observer store."""
        return ObserverStore(logger=self.logger)
