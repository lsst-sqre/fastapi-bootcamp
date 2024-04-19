"""Models for the Astroplan-related app domain."""

from __future__ import annotations

from typing import Any

from astroplan import Observer as AstroplanObserver

# We're re-exporting Observer from the app's domain models to simulate the idea
# that the Astroplan Observer is the app's domain model (i.e., this is a
# pecularity of this demo to make it look like we've coded Astroplan in the
# app itself).
__all__ = ["Observer"]


class Observer(AstroplanObserver):
    """The observer domain model."""

    def __init__(
        self,
        observer_id: str,
        local_timezone: str,
        aliases: list[str] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.observer_id = observer_id
        self.aliases = list(aliases) if aliases else []
        self.local_timezone = local_timezone
