"""
CLASE 14 — Observabilidad · Código Facilito DevOps Bootcamp
Script de Locust para pruebas de carga sobre la API FastAPI.

Genera tráfico realista para visualizar métricas en Grafana:
  - Distintas latencias por endpoint (permite ver histogramas)
  - Error rate en /error (permite ver tasa de errores)
  - Múltiples usuarios concurrentes (permite ver Gauge de activos)
  - Creación de items (permite ver el Gauge del inventario)

Ejecutar:
  # Con UI web (recomendado para ver en tiempo real)
  locust -f locustfile.py --host http://localhost:8000

  # Headless (sin UI) — útil para CI/CD
  locust -f locustfile.py --host http://localhost:8000 \
         --users 20 --spawn-rate 2 --run-time 5m --headless

  # Con la UI web acceder a http://localhost:8089
"""

import random
from locust import HttpUser, task, between, events


# ── Datos de prueba ───────────────────────────────────────────

CATEGORIES = ["orchestration", "monitoring", "visualization", "framework", "container", "ci-cd", "security"]

SAMPLE_ITEMS = [
    {"name": "ArgoCD",       "category": "ci-cd",          "price": 0.0},
    {"name": "Vault",        "category": "security",        "price": 0.0},
    {"name": "Jaeger",       "category": "observabilidad",  "price": 0.0},
    {"name": "Helm",         "category": "orchestration",   "price": 0.0},
    {"name": "Istio",        "category": "networking",      "price": 0.0},
    {"name": "Loki",         "category": "monitoring",      "price": 0.0},
    {"name": "Tempo",        "category": "observabilidad",  "price": 0.0},
    {"name": "Cilium",       "category": "networking",      "price": 0.0},
    {"name": "Keda",         "category": "autoscaling",     "price": 0.0},
    {"name": "Cert-Manager", "category": "security",        "price": 0.0},
]


# ── Usuario de carga normal ───────────────────────────────────

class APIUser(HttpUser):
    """
    Usuario base que simula tráfico típico de una API REST.
    Espera entre 0.5s y 2s entre requests — simula un usuario activo.
    """
    wait_time = between(0.5, 2.0)
    # Los pesos de los @task determinan la frecuencia relativa:
    #   task(10) → 10 veces más probable que task(1)

    @task(10)
    def get_root(self):
        """Endpoint más rápido — genera muchos datos en los buckets bajos del histograma."""
        self.client.get("/", name="GET /")

    @task(8)
    def list_items(self):
        """Lista todos los items — latencia baja (~10ms)."""
        self.client.get("/items", name="GET /items")

    @task(5)
    def list_items_by_category(self):
        """Filtra items por categoría — mismo endpoint, label diferente en Prometheus."""
        category = random.choice(CATEGORIES)
        self.client.get(f"/items?category={category}", name="GET /items?category=*")

    @task(6)
    def get_item(self):
        """Obtiene un item por ID — latencia media (~30-120ms)."""
        item_id = random.randint(1, 10)
        with self.client.get(
            f"/items/{item_id}",
            name="GET /items/{id}",
            catch_response=True,
        ) as response:
            # 404 es esperado para IDs altos — no contar como error de Locust
            if response.status_code == 404:
                response.success()

    @task(2)
    def create_item(self):
        """Crea un item nuevo — latencia alta (~80-250ms). Modifica el Gauge de inventario."""
        item = random.choice(SAMPLE_ITEMS).copy()
        item["name"] = f"{item['name']}-{random.randint(100, 999)}"
        self.client.post(
            "/items",
            json=item,
            name="POST /items",
        )

    @task(3)
    def health_check(self):
        """Health check — usado por Docker/Kubernetes."""
        self.client.get("/health", name="GET /health")

    @task(2)
    def hit_error_endpoint(self):
        """
        30% de probabilidad de HTTP 500 — genera error rate visible en Grafana.
        PromQL para verlo:
          rate(http_requests_total{status_code="500"}[5m])
          / rate(http_requests_total[5m])
        """
        with self.client.get(
            "/error",
            name="GET /error",
            catch_response=True,
        ) as response:
            if response.status_code == 500:
                # Es un error esperado (simulado) — registrar como fallo para las stats de Locust
                response.failure("Simulated 500 error")


# ── Usuario que genera latencias altas ────────────────────────

class SlowUser(HttpUser):
    """
    Usuario que golpea /slow deliberadamente.
    Útil para ver los buckets altos del histograma (>0.5s, >1.0s)
    y los percentiles p95/p99 en Grafana.

    Menor peso que APIUser para no saturar el histograma.
    """
    wait_time = between(1.0, 3.0)
    # Peso relativo frente a APIUser (menos usuarios de este tipo)
    weight = 1

    @task
    def slow_request(self):
        """Genera latencias entre 400ms y 1.2s — activa los buckets >0.5s."""
        self.client.get("/slow", name="GET /slow")


# ── Eventos de Locust (hooks opcionales) ─────────────────────

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("=" * 60)
    print("  Clase 14 — Código Facilito DevOps Bootcamp")
    print("  Iniciando prueba de carga contra FastAPI + Prometheus")
    print("  Grafana: http://localhost:3000  (admin/admin)")
    print("  Prometheus: http://localhost:9090")
    print("  API Docs: http://localhost:8000/docs")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n✓ Prueba de carga finalizada.")
    print("  Revisa los dashboards en Grafana para ver las métricas generadas.")
