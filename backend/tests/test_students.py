"""Tests básicos del CRUD de estudiantes."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_student_requires_auth(client: AsyncClient):
    """Sin token debe retornar 401."""
    response = await client.post(
        "/api/v1/students",
        json={
            "first_name": "Ana",
            "last_name": "Gómez",
            "student_code": "STU001",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_students_requires_auth(client: AsyncClient):
    response = await client.get("/api/v1/students")
    assert response.status_code == 401
