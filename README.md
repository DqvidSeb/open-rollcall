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
│   ├── Dockerfile
│   ├── .env.example
│   └── README.md               ← documentación técnica completa del backend
├── frontend/                   # Interfaz web (Next.js + React)
│   ├── src/
│   │   ├── app/[locale]/        # Rutas (App Router) — auth + dashboard
│   │   ├── components/          # Layout y componentes UI base
│   │   ├── features/            # Módulos por dominio (persons, departments, ...)
│   │   └── lib/                  # Cliente API, endpoints, i18n
│   ├── messages/                 # Traducciones (en.json, es.json)
│   ├── Dockerfile
│   ├── .env.example
│   └── README.md               ← documentación técnica completa del frontend
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
| Frontend | Next.js 16 + React 19 + Tailwind CSS |
| i18n | next-intl (Español / Inglés) |
| Contenerización | Docker + Docker Compose |

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

## Despliegue completo con Docker (Windows y Linux)

Esta guía levanta el **stack completo** (base de datos + backend + frontend) usando Docker y Docker Compose. Los pasos son los mismos en Windows y Linux; las diferencias puntuales se indican en cada paso.

### 0. Prerrequisitos

| Requisito | Windows | Linux |
|---|---|---|
| Docker | [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/) (con WSL2 habilitado) | [Docker Engine + Compose plugin](https://docs.docker.com/engine/install/) |
| Git | [git-scm.com](https://git-scm.com/download/win) | `sudo apt-get install git` (Debian/Ubuntu) o equivalente |
| Terminal | PowerShell | bash/zsh |

En Linux, agrega tu usuario al grupo `docker` para no necesitar `sudo` en cada comando:

```bash
sudo usermod -aG docker $USER && newgrp docker
```

Verifica que Docker esté funcionando:

```bash
docker --version
docker compose version
```

---

### 1. Clonar el repositorio

**Linux / macOS (bash):**
```bash
git clone <repo-url>
cd RollCall
```

**Windows (PowerShell):**
```powershell
git clone <repo-url>
cd RollCall
```

---

### 2. Configurar el Docker Compose (base de datos + backend + frontend)

El archivo `docker-compose.yml` real **no se versiona** (contiene credenciales). Copia la plantilla y edítala:

**Linux / macOS:**
```bash
cp docker-compose.example.yml docker-compose.yml
```

**Windows (PowerShell):**
```powershell
Copy-Item docker-compose.example.yml docker-compose.yml
```

Abre `docker-compose.yml` y reemplaza:

- `<CAMBIAR_USUARIO>` → un usuario de PostgreSQL (ej. `rollcall_user`)
- `<CAMBIAR_CONTRASEÑA_SEGURA>` → una contraseña segura (ej. generada con `openssl rand -hex 16`)

> Estas mismas credenciales deben coincidir con `POSTGRES_USER` / `POSTGRES_PASSWORD` del `.env` del backend (paso 3).

---

### 3. Configurar las variables de entorno del backend

**Linux / macOS:**
```bash
cp backend/.env.example backend/.env
```

**Windows (PowerShell):**
```powershell
Copy-Item backend/.env.example backend/.env
```

Edita `backend/.env`:

| Variable | Descripción | Ejemplo |
|---|---|---|
| `ENVIRONMENT` | `development` o `production` | `production` |
| `SECRET_KEY` | Clave JWT (mín. 32 chars aleatorios) | `openssl rand -hex 32` |
| `ALLOWED_ORIGINS` | Orígenes permitidos por CORS (incluye la URL del frontend) | `["http://localhost:3020"]` |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Igual que en `docker-compose.yml` | `rollcall_user` / `...` / `rollcall_dev` |
| `POSTGRES_HOST` | `db` cuando corre con Docker Compose (nombre del servicio) | `db` |
| `POSTGRES_PORT` | Puerto interno de Postgres | `5432` |
| `API_USER` / `API_PASSWORD` | Credenciales del usuario admin que usará `camera_client.py` | — |
| `FACE_DISTANCE_THRESHOLD` | Umbral de similitud facial (0–1) | `0.40` |

> Generar `SECRET_KEY` — Linux/macOS: `openssl rand -hex 32`. Windows (PowerShell): `[Convert]::ToHexString((1..32 | ForEach-Object { Get-Random -Maximum 256 }))`.

---

### 4. Configurar las variables de entorno del frontend

**Linux / macOS:**
```bash
cp frontend/.env.example frontend/.env
```

**Windows (PowerShell):**
```powershell
Copy-Item frontend/.env.example frontend/.env
```

Edita `frontend/.env`:

| Variable | Descripción | Ejemplo |
|---|---|---|
| `NEXT_PUBLIC_APP_URL` | URL pública del frontend | `http://localhost:3020` |
| `NEXT_PUBLIC_API_URL` | URL pública de la API (alcanzable desde el navegador del usuario) | `http://localhost:8000` |
| `NEXT_PUBLIC_DEFAULT_LOCALE` | Idioma por defecto (`en` / `es`) | `es` |

> `NEXT_PUBLIC_API_URL` se incrusta en el bundle del navegador en tiempo de **build**. Si la cambias, reconstruye la imagen del frontend (`docker compose build frontend`).

---

### 5. Levantar el stack completo

Desde la raíz del repositorio:

```bash
docker compose up -d --build
```

Esto construye y arranca tres contenedores:

- `rollcall_db` — PostgreSQL 18 + pgvector (puerto `5433` en el host → `5432` interno)
- `rollcall_backend` — API FastAPI (puerto `8000`)
- `rollcall_frontend` — interfaz Next.js (puerto `3020`)

Verifica el estado:

```bash
docker compose ps
docker compose logs -f
```

---

### 6. Aplicar las migraciones de base de datos

Con los contenedores corriendo, ejecuta las migraciones de Alembic **dentro** del contenedor del backend:

```bash
docker compose exec backend alembic upgrade head
```

---

### 7. Crear el usuario administrador

Registra el primer usuario (administrador) a través de la API. Puedes usar Swagger UI o `curl`:

**Linux / macOS:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@rollcall.com","password":"CambiaEstaContraseña123","full_name":"Admin"}'
```

**Windows (PowerShell):**
```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/auth/register" `
  -ContentType "application/json" `
  -Body '{"email":"admin@rollcall.com","password":"CambiaEstaContraseña123","full_name":"Admin"}'
```

Usa estas mismas credenciales en `API_USER` / `API_PASSWORD` (`backend/.env`) si vas a correr `camera_client.py`.

---

### 8. Acceder al sistema

| Servicio | URL |
|---|---|
| Frontend (interfaz web) | `http://localhost:3020` |
| API (Swagger UI) | `http://localhost:8000/docs` (solo si `ENVIRONMENT != production`) |
| API (ReDoc) | `http://localhost:8000/redoc` |
| PostgreSQL (cliente externo) | `localhost:5433` |

---

### 9. Cliente de cámara (opcional, fuera de Docker)

`camera_client.py` accede a la cámara del equipo, por lo que normalmente **no corre en Docker** — corre directamente en el sistema operativo del nodo donde está conectada la cámara. Ver la sección "Cliente de cámara" en [`backend/README.md`](backend/README.md) para la instalación del entorno Python local (`venv` + `pip install -e ".[dev]"`).

```bash
cd backend
python camera_client.py attend     # modo asistencia (check-in / check-out)
python camera_client.py enroll <employee_id>   # registrar rostro de un empleado
```

> Configura `BASE_URL` en `backend/.env` apuntando a la URL pública de la API (ej. `http://localhost:8000/api/v1` si la cámara corre en la misma máquina que Docker).

---

### Comandos útiles de Docker Compose

```bash
# Ver logs de un servicio específico
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db

# Reiniciar un servicio tras cambiar su .env
docker compose restart backend

# Reconstruir un servicio tras cambiar código o dependencias
docker compose up -d --build backend
docker compose up -d --build frontend

# Detener todo (mantiene los datos)
docker compose stop

# Detener y eliminar contenedores (mantiene los volúmenes/datos)
docker compose down

# Detener y eliminar TODO, incluyendo datos de la base de datos
docker compose down -v
```

---

## Desarrollo local sin Docker (opcional)

Para desarrollo activo del backend o frontend, normalmente solo la base de datos corre en Docker y el backend/frontend corren directamente en el sistema con recarga automática:

```bash
# 1. Base de datos (Docker)
cp docker-compose.example.yml docker-compose.yml
# Editar credenciales
docker compose up -d db

# 2. Backend (ver backend/README.md para el entorno virtual)
cd backend
cp .env.example .env
# POSTGRES_HOST=localhost (no "db", porque no corre dentro de la red de Docker)
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload

# 3. Frontend (en otra terminal, ver frontend/README.md)
cd frontend
cp .env.example .env
pnpm install
pnpm dev
```

| Servicio | URL en desarrollo |
|---|---|
| Frontend | `http://localhost:3020` |
| Backend / Swagger | `http://localhost:8000/docs` |

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
- [Frontend — instalación y despliegue](frontend/README.md)
- Swagger UI: `http://localhost:8000/docs` (solo en entornos no-producción)

## Licencia

MIT
