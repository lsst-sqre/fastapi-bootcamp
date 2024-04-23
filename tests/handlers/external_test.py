"""Tests for the fastapibootcamp.handlers.external module and routes."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from fastapibootcamp.config import config


@pytest.mark.asyncio
async def test_get_index(client: AsyncClient) -> None:
    """Test ``GET /fastapi-bootcamp/``."""
    response = await client.get("/fastapi-bootcamp/")
    assert response.status_code == 200
    data = response.json()
    metadata = data["metadata"]
    assert metadata["name"] == config.name
    assert isinstance(metadata["version"], str)
    assert isinstance(metadata["description"], str)
    assert isinstance(metadata["repository_url"], str)
    assert isinstance(metadata["documentation_url"], str)


@pytest.mark.asyncio
async def test_get_greeting(client: AsyncClient) -> None:
    """Test ``GET /fastapi-bootcamp/hello``."""
    response = await client.get("/fastapi-bootcamp/hello")
    assert response.status_code == 200
    assert response.text == '"Hello, SQuaRE Services Bootcamp!"'


@pytest.mark.asyncio
async def test_get_multilingual_greeting_es(client: AsyncClient) -> None:
    """Test ``GET /fastapi-bootcamp/greeting?language=es``."""
    response = await client.get("/fastapi-bootcamp/greeting?language=es")
    assert response.status_code == 200
    data = response.json()
    assert data["greeting"] == "¡Hola, SQuaRE Services Bootcamp!"
    assert data["language"] == "es"


@pytest.mark.asyncio
async def test_get_multilingual_greeting_path_fr(client: AsyncClient) -> None:
    """Test ``GET /fastapi-bootcamp/greeting/fr``."""
    response = await client.get("/fastapi-bootcamp/greeting?language=fr")
    assert response.status_code == 200
    data = response.json()
    assert data["greeting"] == "Bonjour, SQuaRE Services Bootcamp!"
    assert data["language"] == "fr"


@pytest.mark.asyncio
async def post_greeting(client: AsyncClient) -> None:
    """Test ``POST /fastapi-bootcamp/greeting``."""
    response = await client.post(
        "/fastapi-bootcamp/greeting",
        json={"name": "SQuaRE", "language": "es"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["greeting"] == "¡Hola, SQuaRE!"
    assert data["language"] == "es"
