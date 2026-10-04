# Multi-stage Dockerfile: Node.js (Tailwind + React) + Python FastAPI
# Stage 1: Build the Node.js frontend
FROM node:22-slim AS frontend-builder
WORKDIR /build
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Python FastAPI backend
FROM python:3.12.6-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8000
ENV LLM_BASE_URL=http://localhost:1234/v1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application files (main.py, data/, models/)
COPY backend/ .

# Copy compiled frontend dist from Stage 1 into ./frontend/dist
COPY --from=frontend-builder /build/dist ./frontend/dist

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]