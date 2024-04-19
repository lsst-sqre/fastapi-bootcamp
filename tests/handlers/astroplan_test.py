"""Tests for the astroplan router."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from fastapibootcamp.config import config


@pytest.mark.asyncio
async def test_get_observer_rubin(client: AsyncClient) -> None:
    """Test ``GET /astroplan/observers/rubin``."""
    path = f"{config.path_prefix}/astroplan/observers/rubin"
    response = await client.get(path)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Rubin Observatory"
    assert data["id"] == "rubin"
    assert data["self_url"].endswith(path)


@pytest.mark.asyncio
async def test_get_observer_not_found(client: AsyncClient) -> None:
    """Test ``GET /astroplan/observers/not-a-site``."""
    path = f"{config.path_prefix}/astroplan/observers/not-a-site"
    response = await client.get(path)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"][0]["type"] == "unknown_observer"
    assert data["detail"][0]["loc"] == ["path", "observer_id"]
