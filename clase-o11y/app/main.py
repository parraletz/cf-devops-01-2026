"""
CLASE 14 — Observabilidad · Código Facilito DevOps Bootcamp
FastAPI instrumentado con prometheus_client.

Endpoints:
  GET  /              → Info del servicio
  GET  /health        → Health check
  GET  /items         → Lista items (rápido ~10ms)
  GET  /items/{id}    → Item por ID (medio ~50-150ms)
  POST /items         → Crear item (lento ~100-300ms)
  GET  /slow          → Endpoint lento (~500ms-1s) para ver histogramas
  GET  /error         → Falla aleatoria 30% para ver error rate
  GET  /metrics       → Endpoint de Prometheus (texto)
"""

import time
import random
import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
)

# ── Métricas de Prometheus ────────────────────────────────────────────────────

# Counter: solo incrementa. Ideal para conteos acumulados.
REQUEST_COUNT = Counter(
    name="http_requests_total",
    documentation="Total de requests HTTP recibidos",
    labelnames=["method", "endpoint", "status_code"],
)

# Histogram: mide distribuciones. Ideal para latencias.
# buckets define los rangos en segundos para los histogramas.
REQUEST_DURATION = Histogram(
    name="http_request_duration_seconds",
    documentation="Duración de requests HTTP en segundos",
    labelnames=["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

# Gauge: sube y baja. Ideal para valores instantáneos.
ACTIVE_REQUESTS = Gauge(
    name="http_requests_in_progress",
    documentation="Requests HTTP activos en este momento",
    labelnames=["method", "endpoint"],
)

# Gauge para el inventario total
ITEMS_TOTAL = Gauge(
    name="app_items_total",
    documentation="Total de items en el inventario",
)

# Counter para errores de aplicación
APP_ERRORS = Counter(
    name="app_errors_total",
    documentation="Total de errores de aplicación",
    labelnames=["endpoint", "error_type"],
)

# Info: metadata estática del servicio
APP_INFO = Info(
    name="app",
    documentation="Información del servicio",
)

# ── Base de datos simulada ────────────────────────────────────────────────────

items_db: dict[int, dict] = {
    1: {"id": 1, "name": "Kubernetes", "category": "orchestration", "price": 0.0},
    2: {"id": 2, "name": "Prometheus", "category": "monitoring", "price": 0.0},
    3: {"id": 3, "name": "Grafana", "category": "visualization", "price": 0.0},
    4: {"id": 4, "name": "FastAPI", "category": "framework", "price": 0.0},
    5: {"id": 5, "name": "Docker", "category": "container", "price": 0.0},
}
next_id = 6

# ── Modelos ───────────────────────────────────────────────────────────────────

class ItemCreate(BaseModel):
    name: str
    category: str = "general"
    price: float = 0.0

class Item(BaseModel):
    id: int
    name: str
    category: str
    price: float

# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializar métricas al arrancar
    APP_INFO.info({
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("APP_ENV", "dev"),
        "name": "cf-observability-demo",
    })
    ITEMS_TOTAL.set(len(items_db))
    yield
    # Cleanup al apagar (si fuera necesario)

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="CF Observabilidad Demo",
    description="FastAPI instrumentado con Prometheus — Clase 14 Código Facilito",
    version=os.getenv("APP_VERSION", "1.0.0"),
    lifespan=lifespan,
)

# ── Middleware: registra métricas en cada request ─────────────────────────────

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """
    Middleware que intercepta cada request para:
    1. Incrementar el contador de requests activos (Gauge)
    2. Medir la duración (Histogram)
    3. Registrar el conteo total con status code (Counter)
    """
    endpoint = request.url.path
    method = request.method

    # Ignorar el propio endpoint /metrics para no generar ruido
    if endpoint == "/metrics":
        return await call_next(request)

    ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).inc()
    start_time = time.time()

    try:
        response = await call_next(request)
        status_code = str(response.status_code)
    except Exception as exc:
        status_code = "500"
        APP_ERRORS.labels(endpoint=endpoint, error_type=type(exc).__name__).inc()
        raise
    finally:
        duration = time.time() - start_time
        ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).dec()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code,
        ).inc()

    return response

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/", tags=["general"])
async def root():
    """Endpoint raíz — respuesta instantánea."""
    return {
        "service": "cf-observabilidad-demo",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("APP_ENV", "dev"),
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "metrics": "/metrics",
    }


@app.get("/health", tags=["general"])
async def health():
    """Health check — usado por Docker y Kubernetes."""
    return {
        "status": "healthy",
        "items_count": len(items_db),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/items", response_model=list[Item], tags=["items"])
async def list_items(category: Optional[str] = None):
    """
    Lista todos los items. Latencia simulada: 5-20ms.
    Ideal para ver el bucket más bajo del histograma.
    """
    await asyncio.sleep(random.uniform(0.005, 0.02))

    if category:
        return [i for i in items_db.values() if i["category"] == category]
    return list(items_db.values())


@app.get("/items/{item_id}", response_model=Item, tags=["items"])
async def get_item(item_id: int):
    """
    Obtiene un item por ID. Latencia simulada: 30-120ms.
    Simula una consulta a base de datos con variabilidad realista.
    """
    await asyncio.sleep(random.uniform(0.03, 0.12))

    if item_id not in items_db:
        APP_ERRORS.labels(endpoint="/items/{item_id}", error_type="NotFound").inc()
        raise HTTPException(status_code=404, detail=f"Item {item_id} no encontrado")

    return items_db[item_id]


@app.post("/items", response_model=Item, status_code=201, tags=["items"])
async def create_item(item: ItemCreate):
    """
    Crea un nuevo item. Latencia simulada: 80-250ms.
    Simula escritura en base de datos.
    """
    global next_id
    await asyncio.sleep(random.uniform(0.08, 0.25))

    new_item = {"id": next_id, **item.model_dump()}
    items_db[next_id] = new_item
    next_id += 1

    # Actualizar el gauge del inventario
    ITEMS_TOTAL.set(len(items_db))

    return new_item


@app.get("/slow", tags=["demo"])
async def slow_endpoint():
    """
    Endpoint lento: 400ms - 1.2s.
    Útil para visualizar los buckets altos del histograma en Grafana
    y el percentil p95/p99 con histogram_quantile() en PromQL.
    """
    delay = random.uniform(0.4, 1.2)
    await asyncio.sleep(delay)
    return {
        "message": "Respuesta lenta",
        "delay_ms": round(delay * 1000, 2),
        "hint": "Revisa el histograma en Grafana — deberías ver este request en los buckets >0.5s",
    }


@app.get("/error", tags=["demo"])
async def error_endpoint():
    """
    Falla aleatoriamente ~30% de las veces con HTTP 500.
    Útil para generar error rate visible en Grafana.

    PromQL para verlo:
      rate(http_requests_total{status_code="500"}[5m])
      /
      rate(http_requests_total[5m])
    """
    await asyncio.sleep(random.uniform(0.01, 0.05))

    if random.random() < 0.30:
        APP_ERRORS.labels(endpoint="/error", error_type="SimulatedError").inc()
        raise HTTPException(
            status_code=500,
            detail="Error simulado para demostración de observabilidad",
        )

    return {"message": "¡Sin error esta vez!", "luck": "good"}


@app.get("/metrics", tags=["observability"])
async def metrics():
    """
    Endpoint scrapeado por Prometheus cada 15 segundos.
    Retorna todas las métricas en formato texto Prometheus.
    """
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST,
    )
