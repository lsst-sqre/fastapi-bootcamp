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


@pytest.mark.asyncio
async def test_get_observers_rubin(client: AsyncClient) -> None:
    """Test finding observing sites with Rubin in name."""
    response = await client.get(
        f"{config.path_prefix}/astroplan/observers?name=rubin"
    )
    assert response.status_code == 200
    response_json = response.json()
    data = response_json["data"]
    pagination = response_json["pagination"]
    assert len(data) == 2
    assert data[0]["name"] == "Rubin AuxTel"
    assert data[1]["name"] == "Rubin Observatory"

    assert pagination["total"] == 2
    assert pagination["page"] == 1
    assert pagination["next_url"] is None
    assert pagination["prev_url"] is None


@pytest.mark.asyncio
async def test_get_observers_pagination(client: AsyncClient) -> None:
    """Test paginating through all observing sites."""
    observers = []
    url = f"{config.path_prefix}/astroplan/observers"
    while url is not None:
        response = await client.get(url)
        assert response.status_code == 200
        response_json = response.json()
        data = response_json["data"]
        pagination = response_json["pagination"]
        observers.extend(data)
        url = pagination["next_url"]
    assert len(observers) == pagination["total"]  # type: ignore[unreachable]


@pytest.mark.asyncio
async def test_get_observers_with_aliases(client: AsyncClient) -> None:
    """Test finding observing sites with LSST in their aliases."""
    response = await client.get(
        f"{config.path_prefix}/astroplan/observers?name=lsst"
    )
    assert response.status_code == 200
    response_json = response.json()
    data = response_json["data"]

    assert len(data) == 2
    assert data[0]["name"] == "Rubin AuxTel"
    assert data[1]["name"] == "Rubin Observatory"


@pytest.mark.asyncio
async def test_rubin_lmc_observability(client: AsyncClient) -> None:
    """Test ``POST /astroplan/observers/rubin/observable``."""
    path = f"{config.path_prefix}/astroplan/observers/rubin/observable"
    response = await client.post(
        path,
        json={
            "ra": "05h23m34.6s",
            "dec": "-69d45m22s",
            "time": "2024-04-24T00:00:00Z",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_night"] is True
    assert data["above_horizon"] is True
    assert data["observer_url"].endswith("/astroplan/observers/rubin")
