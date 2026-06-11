<div align="center">

<img src="https://img.shields.io/badge/RollCall-Frontend-0A84FF?style=for-the-badge&labelColor=0A1628&color=0A84FF" alt="Open RollCall Frontend"/>

[![Next.js](https://img.shields.io/badge/Next.js-16-0A84FF?style=flat-square&logo=next.js&logoColor=white&labelColor=0A1628)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19-0A84FF?style=flat-square&logo=react&logoColor=white&labelColor=0A1628)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-0A84FF?style=flat-square&logo=typescript&logoColor=white&labelColor=0A1628)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-3-0A84FF?style=flat-square&logo=tailwindcss&logoColor=white&labelColor=0A1628)](https://tailwindcss.com/)
[![next-intl](https://img.shields.io/badge/next--intl-i18n-0A84FF?style=flat-square&labelColor=0A1628)](https://next-intl.dev/)

</div>

---

## Stack

| Componente | Tecnología | Notas |
|---|---|---|
| Framework | Next.js 16 (App Router) | React Server Components + rutas `[locale]` |
| UI | React 19 + Tailwind CSS | Diseño propio (design system "RollCall") |
| Tipado | TypeScript 5 | Estricto |
| i18n | next-intl | Español / Inglés (`messages/es.json`, `messages/en.json`) |
| Iconos | Phosphor Icons | `@phosphor-icons/react` |
| Linter | ESLint 9 (flat config) | `eslint-config-next` |
| Gestor de paquetes | pnpm | Workspace declarado en `pnpm-workspace.yaml` |

---

## Prerrequisitos

- **Node.js 22 LTS** (o superior)
- **pnpm** (`corepack enable` lo habilita automáticamente con Node 22)
- **Backend de RollCall** corriendo y accesible (ver [`../backend/README.md`](../backend/README.md))
- **Docker Desktop** (o Docker Engine en Linux) — solo si vas a desplegar con contenedores

### Instalar pnpm

```bash
corepack enable
corepack prepare pnpm@11.5.0 --activate
```

---

## Configuración

### Variables de entorno

Copia `.env.example` a `.env` dentro de `frontend/`:

```bash
cp .env.example .env
```

| Variable | Descripción | Ejemplo |
|---|---|---|
| `NEXT_PUBLIC_APP_URL` | URL pública en la que corre el frontend | `http://localhost:3020` |
| `NEXT_PUBLIC_API_URL` | URL base de la API del backend | `http://localhost:8000` |
| `NEXT_PUBLIC_DEFAULT_LOCALE` | Idioma por defecto (`en` o `es`) | `en` |

> Todas las variables empiezan con `NEXT_PUBLIC_` porque se usan en el cliente (browser). Si en el futuro se agregan variables solo de servidor, no deben llevar este prefijo.

> Si despliegas frontend y backend en hosts/dominios distintos, recuerda agregar la URL del frontend a `ALLOWED_ORIGINS` en el `.env` del backend (CORS).

---

## Desarrollo local (sin Docker)

Todos los comandos se ejecutan **dentro de la carpeta `frontend/`**.

```bash
cd frontend

# 1. Instalar dependencias
pnpm install

# 2. Configurar variables de entorno
cp .env.example .env

# 3. Levantar el servidor de desarrollo (puerto 3020)
pnpm dev
```

La aplicación queda disponible en `http://localhost:3020`.

> El backend debe estar corriendo (por defecto en `http://localhost:8000`) para que el login y las peticiones a la API funcionen. Ver [`../backend/README.md`](../backend/README.md).

### Comandos disponibles

```bash
# Servidor de desarrollo con recarga automática
pnpm dev

# Build de producción
pnpm build

# Servidor de producción (requiere "pnpm build" previo)
pnpm start

# Linter (obligatorio sin warnings/errores antes de cada commit)
pnpm lint

# Type-checking
pnpm run type-check
```

---

## Despliegue con Docker

El frontend se construye como una imagen multi-stage basada en `node:22-alpine`, usando la salida `standalone` de Next.js (`next.config.ts`).

### Build y ejecución individual

```bash
cd frontend

# Construir la imagen
docker build -t rollcall-frontend .

# Ejecutar el contenedor
docker run -d \
  --name rollcall_frontend \
  --env-file .env \
  -p 3020:3020 \
  rollcall-frontend
```

La aplicación queda disponible en `http://localhost:3020`.

### Como parte del stack completo

El `docker-compose.example.yml` de la raíz del repositorio define el servicio `frontend` junto con `backend` y `db`. Ver [`../README.md`](../README.md) para el procedimiento completo (Windows y Linux).

```bash
# Desde la raíz del repositorio
docker compose up -d --build frontend
```

---

## Estructura del proyecto

```
frontend/
├── messages/                 # Traducciones i18n (en.json, es.json)
├── public/                    # Assets estáticos
├── src/
│   ├── app/
│   │   └── [locale]/          # Rutas del App Router (i18n por segmento)
│   │       ├── (auth)/         # Login / registro
│   │       └── (dashboard)/    # Páginas autenticadas (personas, departamentos, posiciones, programas académicos, asistencia, ...)
│   ├── components/
│   │   ├── layout/             # Sidebar, header, shells de página
│   │   └── ui/                 # Componentes base (Button, Input, etc.)
│   ├── features/               # Un módulo por dominio (persons, departments,
│   │   │                          positions, academic-programs, attendance-checkin,
│   │   │                          face-enrollment, ...)
│   │   └── <feature>/
│   │       ├── components/     # UI del feature (≤ 200 líneas por componente)
│   │       ├── hooks/           # Hooks de datos (use<Feature>)
│   │       ├── services/        # Llamadas HTTP al backend
│   │       └── types.ts         # Tipos / DTOs (mirror de los schemas Pydantic)
│   └── lib/
│       ├── api/                 # Cliente HTTP, endpoints centralizados, ApiError
│       └── i18n/                 # Configuración de next-intl
├── eslint.config.mjs
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── Dockerfile
└── .env.example
```

---

## Convenciones del proyecto

- **Capa de datos modular por feature**: cada módulo bajo `src/features/<feature>/` tiene su propio `types.ts`, `services/*.service.ts` (llamadas a `ENDPOINTS` definidos en `src/lib/api/endpoints.ts`) y `hooks/use<Feature>.ts` (estado + fetch).
- **Componentes ≤ 200 líneas**: si un componente crece, se extraen sub-componentes (`*SheetShell.tsx`, `*DetailsHeader.tsx`, `*FormFields.tsx`, etc.).
- **i18n obligatorio**: todo texto visible va en `messages/en.json` y `messages/es.json` bajo el namespace del feature, accedido con `useTranslations('<Namespace>')`.
- **ESLint estricto**: `pnpm lint` debe terminar sin errores ni warnings antes de cualquier commit/PR.

---

## Notas de despliegue

- En producción, define `NEXT_PUBLIC_API_URL` apuntando al dominio público del backend (con HTTPS).
- El build de producción (`pnpm build` / imagen Docker) requiere que `NEXT_PUBLIC_*` esté disponible **en tiempo de build**, ya que Next.js las incrusta en el bundle del cliente. Si cambian, hay que reconstruir la imagen.
- El puerto por defecto es `3020` (configurado en `package.json` y en el `Dockerfile`).
