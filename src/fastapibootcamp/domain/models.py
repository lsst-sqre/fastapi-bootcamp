"""Models for the Astroplan-related app domain."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from astroplan import Observer as AstroplanObserver
from astropy.coordinates import AltAz, Angle, SkyCoord
from astropy.time import Time

# We're re-exporting Observer from the app's domain models to simulate the idea
# that the Astroplan Observer is the app's domain model (i.e., this is a
# pecularity of this demo to make it look like we've coded Astroplan in the
# app itself).
__all__ = ["Observer", "TargetObservability"]


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


@dataclass(kw_only=True)
class TargetObservability:
    """The observability of a target for an observer."""

    observer: Observer
    target: SkyCoord
    time: datetime
    airmass: float | None
    altaz: AltAz
    is_above_horizon: bool
    is_night: bool
    moon_up: bool
    moon_separation: Angle
    moon_altaz: AltAz
    moon_illumination: float

    @classmethod
    def compute(
        cls,
        observer: Observer,
        target: SkyCoord,
        time: datetime,
    ) -> TargetObservability:
        """Compute the observability of a target for an observer."""
        astropy_time = Time(time)
        is_up = observer.target_is_up(astropy_time, target)

        altaz = target.transform_to(
            AltAz(obstime=astropy_time, location=observer.location)
        )
        airmass = altaz.secz if is_up else None

        is_night = observer.is_night(astropy_time)

        moon_altaz = observer.moon_altaz(astropy_time)
        moon_up = moon_altaz.alt > 0
        moon_separation = altaz.separation(moon_altaz)
        moon_illumination = observer.moon_illumination(astropy_time)

        return cls(
            observer=observer,
            target=target,
            time=time,
            is_above_horizon=is_up,
            airmass=airmass,
            altaz=altaz,
            is_night=is_night,
            moon_up=moon_up,
            moon_separation=moon_separation,
            moon_altaz=moon_altaz,
            moon_illumination=moon_illumination,
        )
