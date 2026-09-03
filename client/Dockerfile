# ── Stage 1: Install dependencies ────────────────────────────────────
FROM node:20-alpine AS deps

# Add libc6-compat for Next.js SWC compiler compatibility on Alpine
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy dependency files first (cache layer)
COPY package.json pnpm-lock.yaml ./

# Install pnpm and dependencies
RUN corepack enable && corepack prepare pnpm@latest --activate
RUN pnpm install --frozen-lockfile

# ── Stage 2: Build the application ──────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Set build-time env variables
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
# Disable Next.js telemetry during build
ENV NEXT_TELEMETRY_DISABLED=1

# Build the Next.js application (standalone output)
RUN corepack enable && corepack prepare pnpm@latest --activate
RUN pnpm run build

# ── Stage 3: Production runtime ─────────────────────────────────────
FROM node:20-alpine AS runner

WORKDIR /app

# Disable Next.js telemetry during runtime
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user for security
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 appuser

# Copy standalone build output with correct ownership
COPY --from=builder --chown=1001:1001 /app/.next/standalone ./
COPY --from=builder --chown=1001:1001 /app/.next/static ./.next/static
COPY --from=builder --chown=1001:1001 /app/public ./public

# Switch to non-root user
USER appuser

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

EXPOSE 3000

CMD ["node", "server.js"]
