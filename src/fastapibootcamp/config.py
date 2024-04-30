"""Configuration definition."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from safir.logging import LogLevel, Profile

__all__ = ["Config", "config"]


class Config(BaseSettings):
    """Configuration for fastapi-bootcamp."""

    name: str = Field("fastapi-bootcamp", title="Name of application")

    path_prefix: str = Field(
        "/fastapi-bootcamp", title="URL prefix for application"
    )

    profile: Profile = Field(
        Profile.development, title="Application logging profile"
    )

    log_level: LogLevel = Field(
        LogLevel.INFO, title="Log level of the application's logger"
    )

    clear_iers_on_startup: bool = Field(
        False,
        title="Clear IERS cache on application startup",
        description=(
            "The IERS cache is used by Astropy and Astroplan. In development "
            "this cache can be cleared on startup to exercise populating it. "
            "Generally the cache is not pre-existing in production, so this "
            "option is not needed."
        ),
    )

    model_config = SettingsConfigDict(
        env_prefix="FASTAPI_BOOTCAMP_", case_sensitive=False
    )


config = Config()
"""Configuration for fastapi-bootcamp."""
