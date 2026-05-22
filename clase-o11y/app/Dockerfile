# ============================================================
# CLASE 14 — Observabilidad · Código Facilito DevOps Bootcamp
# Imagen mínima para FastAPI instrumentado con Prometheus
# ============================================================

FROM python:3.12-slim

# Metadatos
LABEL maintainer="Código Facilito DevOps Bootcamp"
LABEL description="FastAPI + Prometheus Client — Clase 14 Observabilidad"

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=dev \
    APP_VERSION=1.0.0

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias primero (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY main.py .

# Exponer el puerto de la app
EXPOSE 8000

# Health check interno del contenedor
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

# Arrancar con uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
