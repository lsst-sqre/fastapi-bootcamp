"""A class-based FastAPI dependency for demonstration purposes."""

from __future__ import annotations

import random

from ..exceptions import DemoInternalError

__all__ = ["example_singleton_dependency", "ExampleSingletonDependency"]


class ExampleSingletonDependency:
    """A stateful FastAPI dependency for demonstration purposes.

    See lesson 6 in src/fastapibootcamp/handlers/example.py for usage.
    """

    def __init__(self) -> None:
        # For this demo we're just using a semi-random string as the state. In
        # real applications, this could be a database connection, a client
        # to a remote service, etc. This "state" is reused over the life of
        # this application instance (i.e. a Kubernetes pod). It's not shared
        # between instances, though.
        self._state: str | None = None

    async def init(self) -> None:
        """Initialize the dependency.

        This initialization is called in main.py in the lifespan context
        manager.
        """
        self._state = f"{random.choice(ADJECTIVES)} {random.choice(ANIMALS)}"

    async def __call__(self) -> str:
        """Provide the dependency.

        This gets called by the fastapi Depends() function when your
        path operation function is called.
        """
        if self._state is None:
            raise DemoInternalError(
                "ExampleSingletonDependency not initialized."
            )

        return self._state

    async def aclose(self) -> None:
        """Clean up the dependency.

        If needed, this method is called when the application is shutting down
        to close connections, etc.. This is called in the lifespan context
        manager in main.py
        """
        self._state = None


# This is the singleton instance of the dependency that's referenced in path
# operation functions with the fastapi.Depends() function. Note that it needs
# to be initialized before it can be used. This is done in the lifespan context
# manager in main.py. Another option is to initialize it on the first use.
example_singleton_dependency = ExampleSingletonDependency()


ADJECTIVES = [
    "speedy",
    "ponderous",
    "furious",
    "careful",
    "mammoth",
    "crafty",
]

ANIMALS = [
    "cat",
    "dog",
    "sloth",
    "snail",
    "rabbit",
    "turtle",
]
