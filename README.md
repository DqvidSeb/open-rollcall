<div align="center">

<img src="https://img.shields.io/badge/RollCall-Facial%20Attendance-0A84FF?style=for-the-badge&labelColor=0A1628&color=0A84FF" alt="RollCall"/>

**Sistema de control de asistencia por reconocimiento facial**

[![Python](https://img.shields.io/badge/Python-3.11+-0A84FF?style=flat-square&logo=python&logoColor=white&labelColor=0A1628)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-0A84FF?style=flat-square&logo=fastapi&logoColor=white&labelColor=0A1628)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-0A84FF?style=flat-square&logo=postgresql&logoColor=white&labelColor=0A1628)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-required-0A84FF?style=flat-square&logo=docker&logoColor=white&labelColor=0A1628)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-0A84FF?style=flat-square&labelColor=0A1628)](LICENSE)

</div>

---

RollCall es un sistema de asistencia empresarial que registra entradas y salidas de empleados mediante reconocimiento facial en tiempo real. La cámara detecta el rostro, extrae un embedding biométrico con ArcFace y lo compara contra la base de datos por distancia coseno con pgvector. No se almacenan fotos, solo vectores.

## Estructura del repositorio

```
RollCall/
├── backend/            # API REST (FastAPI) + cliente de cámara
│   ├── app/            # Código fuente de la API
│   ├── alembic/        # Migraciones de base de datos
│   ├── camera_client.py
│   └── README.md       ← documentación técnica completa
├── frontend/           # (próximamente — Next.js)
├── docker-compose.yml  # Base de datos PostgreSQL + pgvector
└── README.md
```

## Stack general

| Capa | Tecnología |
|---|---|
| API | FastAPI + Uvicorn |
| Base de datos | PostgreSQL 18 + pgvector |
| ORM / migraciones | SQLAlchemy 2 async + Alembic |
| Reconocimiento facial | DeepFace / ArcFace + TensorFlow |
| Contenerización | Docker + Docker Compose |
| Frontend (próximo) | Next.js + React |

## Documentación

- [Backend — instalación y despliegue](backend/README.md)
- Frontend — próximamente

## Licencia

MIT
