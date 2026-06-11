# ── Stage 1: dependencies ────────────────────────────────────────────────────
FROM node:22-alpine AS deps

WORKDIR /app

RUN corepack enable

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile


# ── Stage 2: builder ─────────────────────────────────────────────────────────
FROM node:22-alpine AS builder

WORKDIR /app

RUN corepack enable

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build-time environment (overridden at runtime via env_file/.env)
ENV NEXT_TELEMETRY_DISABLED=1

RUN pnpm build


# ── Stage 3: runtime ──────────────────────────────────────────────────────────
FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Usuario no-root por seguridad
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# Salida "standalone" de Next.js — incluye solo lo necesario para correr el server
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3020
ENV PORT=3020
ENV HOSTNAME=0.0.0.0

CMD ["node", "server.js"]
