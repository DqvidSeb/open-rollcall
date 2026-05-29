<div align="center">

<img src="https://img.shields.io/badge/Open%20Roll%20Call-Reconocimiento%20Facial-0A84FF?style=for-the-badge&labelColor=0A1628&color=0A84FF" alt="Open Roll Call"/>

**Sistema de control de asistencia por reconocimiento facial**

[![Python](https://img.shields.io/badge/Python-3.11+-0A84FF?style=flat-square&logo=python&logoColor=white&labelColor=0A1628)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-0A84FF?style=flat-square&logo=fastapi&logoColor=white&labelColor=0A1628)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-0A84FF?style=flat-square&logo=postgresql&logoColor=white&labelColor=0A1628)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-required-0A84FF?style=flat-square&logo=docker&logoColor=white&labelColor=0A1628)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-0A84FF?style=flat-square&labelColor=0A1628)](LICENSE)

</div>

---

**Open Roll Call** es un sistema de asistencia por reconocimiento facial en tiempo real, diseñado para funcionar en universidades, colegios, empresas y cualquier entorno que necesite registrar la presencia de personas de forma automatizada. La cámara detecta el rostro, extrae un embedding biométrico con ArcFace y lo compara contra la base de datos por distancia coseno con pgvector. No se almacenan fotos, solo vectores.

El sistema es completamente configurable: cada instalación define su propio horario (hora de entrada, hora de salida y zona horaria), y el cliente de cámara lo carga automáticamente desde la API al arrancar.

## ¿Para quién es?

Open Roll Call está pensado para cualquier organización que necesite tomar asistencia de personas con reconocimiento facial:

- **Universidades** — registro de asistencia de estudiantes por clase o jornada.
- **Colegios** — control de entrada y salida de alumnos.
- **Empresas** — marcación de entrada/salida de colaboradores.
- **Eventos y espacios controlados** — acceso restringido con registro biométrico.

La arquitectura es genérica: la entidad que pasa lista se llama `Person` (y su especialización `Employee`), pero el modelo se adapta a cualquier dominio.

## Estructura del repositorio

```
RollCall/
├── backend/                    # API REST (FastAPI) + cliente de cámara
│   ├── app/
│   │   ├── api/v1/endpoints/   # Routers FastAPI (Swagger en /docs)
│   │   ├── models/             # Modelos SQLAlchemy (3FN)
│   │   ├── repositories/       # Capa de acceso a datos
│   │   ├── schemas/            # Schemas Pydantic
│   │   └── services/           # Lógica de negocio
│   ├── alembic/                # Migraciones de base de datos
│   ├── camera_client.py        # Cliente de cámara (corre en el nodo local)
│   └── README.md               ← documentación técnica completa
├── frontend/                   # (próximamente — Next.js)
├── docker-compose.example.yml  # Plantilla — copiar a docker-compose.yml
└── README.md
```

## Stack general

| Capa | Tecnología |
|---|---|
| API | FastAPI + Uvicorn |
| Documentación | Swagger UI (`/docs`) + ReDoc (`/redoc`) |
| Base de datos | PostgreSQL 18 + pgvector |
| ORM / migraciones | SQLAlchemy 2 async + Alembic |
| Reconocimiento facial | DeepFace / ArcFace + TensorFlow |
| Contenerización | Docker + Docker Compose |
| Frontend (próximo) | Next.js + React |

## Configuración de horarios (Schedule)

Cada instalación define sus propias ventanas horarias desde la API. Los horarios se persisten en base de datos (tabla `schedule`, normalizada en 3FN) y el cliente de cámara los consulta automáticamente al arrancar.

**Crear un horario:**

```http
POST /api/v1/schedules
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Jornada mañana",
  "timezone": "America/Bogota",
  "check_in_start": "07:00:00",
  "check_in_end": "09:30:00",
  "checkout_start": "16:00:00",
  "checkout_end": "20:00:00",
  "is_active": true
}
```

| Campo | Descripción |
|---|---|
| `name` | Nombre descriptivo (único por instalación) |
| `timezone` | Zona horaria IANA del nodo de cámara (`America/Bogota`, `Europe/Madrid`, etc.) |
| `check_in_start` / `check_in_end` | Ventana válida para registrar entrada |
| `checkout_start` / `checkout_end` | Ventana válida para registrar salida |
| `is_active` | `true` = horario activo del sistema (solo uno a la vez) |

Solo puede existir un horario activo a la vez; activar uno desactiva el anterior automáticamente. El endpoint `GET /api/v1/schedules/active` es **público** (sin token) para que `camera_client.py` lo consulte al arrancar. El servidor también valida que cada evento de reconocimiento caiga dentro de la ventana configurada antes de registrarlo.

## Inicio rápido

```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd RollCall

# 2. Configurar la base de datos
cp docker-compose.example.yml docker-compose.yml
# Editar docker-compose.yml con credenciales reales
docker compose up -d

# 3. Configurar el backend
cd backend
cp .env.example .env
# Editar .env (SECRET_KEY, credenciales de BD, etc.)

# 4. Instalar dependencias y correr migraciones
pip install -e ".[dev]"
alembic upgrade head

# 5. Arrancar el servidor
uvicorn app.main:app --reload

# 6. Abrir la documentación interactiva
# http://localhost:8000/docs
```

## Seguridad — credenciales en Git

`docker-compose.yml` está en `.gitignore` porque contiene credenciales reales. Usa siempre `docker-compose.example.yml` como plantilla y nunca subas el archivo real al repositorio.

Si accidentalmente ya subiste credenciales, elimínalas del historial completo con [`git-filter-repo`](https://github.com/newren/git-filter-repo):

```bash
# Instalar
pip install git-filter-repo

# Eliminar el archivo del historial de todas las ramas
git filter-repo --path docker-compose.yml --invert-paths --force

# Forzar push
git push origin --force --all
git push origin --force --tags
```

Después de esto **rota todas las contraseñas y tokens** que hayan quedado expuestos, independientemente de la limpieza del historial.

## Documentación

- [Backend — instalación y despliegue](backend/README.md)
- Swagger UI: `http://localhost:8000/docs` (solo en entornos no-producción)
- Frontend — próximamente

## Licencia

MIT
