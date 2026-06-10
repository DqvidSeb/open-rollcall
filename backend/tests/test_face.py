"""Tests básicos del endpoint de estado de reconocimiento facial."""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_face_status_requires_auth(client: AsyncClient):
    response = await client.get(f"/api/v1/face/status/{uuid.uuid4()}")
    assert response.status_code == 401
