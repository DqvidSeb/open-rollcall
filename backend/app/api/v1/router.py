"""Router principal de la API v1."""

from fastapi import APIRouter

from app.api.v1.endpoints import attendance, auth, employees, face, persons, users

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(employees.router)
api_router.include_router(persons.router)
api_router.include_router(face.router)
api_router.include_router(attendance.router)
