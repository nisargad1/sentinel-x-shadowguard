# ==============================================================================
# Multi-Stage Dockerfile for SENTINEL-X ShadowGuard Full-Stack Gateway
# ==============================================================================

# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Python Production Gateway Runtime
FROM python:3.11-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HOST=0.0.0.0

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python backend dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/app ./backend/app
COPY backend/run.py ./backend/run.py
COPY mcp_server ./mcp_server

# Copy built frontend assets into destination served by FastAPI
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Non-root unprivileged container user for zero-trust security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

WORKDIR /app/backend
CMD ["python", "run.py"]
