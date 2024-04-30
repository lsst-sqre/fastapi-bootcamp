"""Manage IERS the caching for Astropy."""

from __future__ import annotations

from astropy.utils import iers
from astropy.utils.data import clear_download_cache
from structlog.stdlib import BoundLogger


class IersCacheManager:
    """Manage IERS the caching for Astropy.

    The Astropy and Astroplan calculations of target observability, as well
    as the location of the Sun and Moon, use IERS data. To provide good
    predictions, we configure IERS to cache the IERS tables, but to update
    them as necessary. This class also allows us to prime the cache with
    current IERS data. Requests that trigger an IERS download will take longer
    and will block the app since Astropy downloads IERS data synchronously.

    Another approach would be to rely on data from `astropy-iers-data`
    exclusively, and regularly release and deploy new versions of this app
    to include that data.

    Yet another approach might be to use a separate service to maintain the
    IERS cache e.g. in Redis and provide it to the app as a service.
    """

    def __init__(self, logger: BoundLogger) -> None:
        self._logger = logger

    def config_iers_cache(self) -> None:
        """Configure the IERS cache."""
        iers.conf.auto_download = True
        iers.conf.auto_max_age = 30  # days

    def download_iers_data(self) -> None:
        """Download the IERS data.

        This method downloads and caches IERS data that gives predictions
        valid up to a year in the future.

        Note that requesting observability predictions for dates outside this
        range may trigger a download of new IERS data.
        """
        self._logger.info("Downloading IERS data.")
        iers.IERS_Auto.open()
        self._logger.info("IERS data download complete.")

    def clear_iers_cache(self) -> None:
        """Clear the IERS cache."""
        clear_download_cache()
        self._logger.info("IERS cache cleared.")
