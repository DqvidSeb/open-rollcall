"""Tests básicos del CRUD de personas."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_create_person_requires_auth(client: AsyncClient):
    """Sin token debe retornar 401."""
    response = await client.post(
        "/api/v1/persons",
        json={
            "first_name": "Juan",
            "last_name": "Pérez",
            "employee_code": "EMP001",
        },
    )
    assert response.status_code == 401
