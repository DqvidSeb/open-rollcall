<div align="center">

<img src="https://img.shields.io/badge/RollCall-Backend-0A84FF?style=for-the-badge&labelColor=0A1628&color=0A84FF" alt="Open RollCall Backend"/>

[![Python](https://img.shields.io/badge/Python-3.11+-0A84FF?style=flat-square&logo=python&logoColor=white&labelColor=0A1628)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-0A84FF?style=flat-square&logo=fastapi&logoColor=white&labelColor=0A1628)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-0A84FF?style=flat-square&logo=sqlalchemy&logoColor=white&labelColor=0A1628)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18%20+%20pgvector-0A84FF?style=flat-square&logo=postgresql&logoColor=white&labelColor=0A1628)](https://www.postgresql.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-ArcFace-0A84FF?style=flat-square&logo=tensorflow&logoColor=white&labelColor=0A1628)](https://www.tensorflow.org/)

</div>

---

## Stack

| Componente | Tecnología | Notas |
|---|---|---|
| Framework web | FastAPI | Async, OpenAPI auto-generado |
| Servidor ASGI | Uvicorn | Con `--reload` en desarrollo |
| ORM | SQLAlchemy 2 (async) | Sesiones asíncronas con asyncpg |
| Driver PostgreSQL | asyncpg | Protocolo binario, alta performance |
| Migraciones | Alembic | Auto-generadas desde modelos ORM |
| Base de datos | PostgreSQL 18 + pgvector | Búsqueda vectorial por distancia coseno |
| Reconocimiento facial | DeepFace + ArcFace | Embeddings de 512 dimensiones |
| Motor de IA | TensorFlow + tf-keras | Inferencia en CPU |
| Detector facial | OpenCV YuNet | Detección y landmarks en el cliente |
| Configuración | pydantic-settings | Variables de entorno tipadas |
| Auth | JWT (python-jose) + bcrypt | Tokens de acceso y refresco |

---

## Prerrequisitos

- **Docker Desktop** (o Docker Engine en Linux) — para la base de datos
- **Python 3.11 o superior**
- **Git**

### Instalar Docker

| SO | Instrucciones |
|---|---|
| Windows | [docs.docker.com/desktop/install/windows](https://docs.docker.com/desktop/install/windows-install/) |
| macOS | [docs.docker.com/desktop/install/mac](https://docs.docker.com/desktop/install/mac-install/) |
| Ubuntu/Debian | `sudo apt-get install docker.io docker-compose-plugin` |
| Fedora/RHEL | `sudo dnf install docker docker-compose-plugin` |

En Linux, agrega tu usuario al grupo docker para no necesitar `sudo`:
```bash
sudo usermod -aG docker $USER && newgrp docker
```

---

## Configuración

### 1. Variables de entorno

Copia `.env.example` a `.env` dentro de `backend/` y rellena los valores:

```bash
cp .env.example .env
```

| Variable | Descripción | Ejemplo |
|---|---|---|
| `SECRET_KEY` | Clave JWT (mín. 32 chars) | `openssl rand -hex 32` |
| `POSTGRES_USER` | Usuario de PostgreSQL | `rollcall_user` |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL | `s3cr3t` |
| `POSTGRES_HOST` | Host de la BD | `localhost` |
| `POSTGRES_PORT` | Puerto de la BD | `5432` |
| `POSTGRES_DB` | Nombre de la base de datos | `rollcall_dev` |
| `API_USER` | Usuario admin para el cliente de cámara | `admin@rollcall.com` |
| `API_PASSWORD` | Contraseña de ese usuario | — |
| `FACE_DISTANCE_THRESHOLD` | Umbral de distancia coseno (0–1) | `0.55` |
| `FACE_DETECTOR_BACKEND` | Backend de detección | `skip` (cliente pre-detecta) |

> `FACE_DETECTOR_BACKEND=skip` indica que el cliente de cámara envía la cara ya recortada y alineada. No cambiarlo a menos que se use la API sin `camera_client.py`.

### 2. Credenciales de Docker Compose

El archivo `docker-compose.yml` en la raíz del repositorio define el servicio de base de datos. Las credenciales que pongas allí deben coincidir exactamente con las de tu `.env`. Cámbialas antes de cualquier despliegue que no sea local.

---

## Base de datos

La BD corre como contenedor Docker. Usa la imagen oficial `pgvector/pgvector:pg18`, que incluye PostgreSQL 18 con la extensión pgvector preinstalada.

**Desde la raíz del repositorio:**

```bash
# Levantar la base de datos
docker compose up -d db

# Ver logs
docker compose logs -f db

# Detener
docker compose stop db

# Eliminar contenedor y volumen (borra todos los datos)
docker compose down -v
```

> Necesita estar corriendo antes de ejecutar las migraciones o el servidor.

---

## Entorno Python

Todos los comandos siguientes se ejecutan **dentro de la carpeta `backend/`**.

```bash
cd backend
```

### Crear y activar el entorno virtual

**Windows (PowerShell o CMD):**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Instalar dependencias

```bash
pip install -e ".[dev]"
```

Esto instala el paquete en modo editable con todas las dependencias de desarrollo (ruff, pytest, mypy, httpx).

### Desactivar / eliminar el entorno

```bash
# Desactivar
deactivate

# Eliminar (desde backend/)
rm -rf .venv          # Linux / macOS
Remove-Item -Recurse .venv   # Windows PowerShell
```

---

## Migraciones

Con la base de datos corriendo y el `.env` configurado:

```bash
# Aplicar todas las migraciones (crear tablas)
alembic upgrade head

# Ver el estado actual
alembic current

# Generar una nueva migración tras cambiar modelos ORM
alembic revision --autogenerate -m "descripcion del cambio"

# Revertir un paso
alembic downgrade -1
```

---

## Ejecutar el servidor

```bash
# Desarrollo (recarga automática al guardar)
uvicorn app.main:app --reload

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

> En el primer arranque, el servidor carga el modelo ArcFace (~20 s). Los reinicios posteriores también cargan el modelo. Con `--workers > 1` en producción cada worker carga su propia instancia del modelo.

La API queda disponible en `http://localhost:8000`.  
Documentación interactiva: `http://localhost:8000/docs`

---

## Cliente de cámara

El archivo `camera_client.py` es el cliente que captura video, detecta rostros con YuNet y se comunica con la API. Requiere que el servidor esté corriendo y el `.env` configurado con `BASE_URL`, `API_USER` y `API_PASSWORD`.

Se ejecuta en una **consola separada**, también dentro de `backend/` con el entorno virtual activado.

```bash
# Modo asistencia — check-in / check-out por reconocimiento facial
python camera_client.py attend

# Modo enrollment — registrar rostros de un empleado
python camera_client.py enroll <employee_id>
```

Usa `ESC` para cerrar la ventana de cámara.

> El archivo `.onnx` del detector YuNet (`face_detection_yunet_2023mar.onnx`) se descarga automáticamente en el primer uso si no está presente.

---

## Consolas necesarias en desarrollo

El sistema requiere tres procesos corriendo simultáneamente, cada uno en su propia terminal:

```
Terminal 1 (raíz del repo)  →  docker compose up -d db
Terminal 2 (backend/)       →  uvicorn app.main:app --reload
Terminal 3 (backend/)       →  python camera_client.py attend
```

---

## Estructura del proyecto

```
backend/
├── app/
│   ├── api/v1/endpoints/   # Rutas HTTP (auth, employees, face, attendance)
│   ├── core/               # Config, base de datos, seguridad, dependencias
│   ├── models/             # Modelos SQLAlchemy (Person, Employee, FaceEncoding, …)
│   ├── repositories/       # Acceso a datos por modelo
│   ├── schemas/            # Schemas Pydantic (request / response)
│   ├── services/           # Lógica de negocio (FaceService, AttendanceService, …)
│   └── main.py             # Entry point FastAPI
├── alembic/                # Migraciones de base de datos
│   └── versions/
├── tests/
├── camera_client.py        # Cliente de cámara (enrollment + asistencia)
├── pyproject.toml          # Dependencias y configuración del proyecto
├── alembic.ini
├── Dockerfile
└── .env.example
```

---

## Comandos de desarrollo

```bash
# Linter y formato
ruff check .
ruff format .

# Type checking
mypy app/

# Tests
pytest

# Tests con cobertura
pytest --cov=app tests/
```

---

## Notas de despliegue

- En producción, cambia `ENVIRONMENT=production` en el `.env`. Esto desactiva `/docs`, `/redoc` y `/openapi.json`.
- El modelo ArcFace se descarga automáticamente de DeepFace en el primer uso (`~/.deepface/`). En Docker, monta ese directorio como volumen para no descargarlo en cada arranque del contenedor.
- La inferencia es en CPU. Para tiempos de respuesta menores a 1 s, se recomienda GPU con los drivers CUDA apropiados.
