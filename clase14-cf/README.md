# Clase 14 — Observabilidad

Stack completo de observabilidad para aplicaciones FastAPI: **Prometheus**, **Grafana**, **cAdvisor** y **Node Exporter**.

## 📦 Estructura

```
clase14-cf/
├── app/                 # Aplicación FastAPI instrumentada con Prometheus
│   ├── main.py         # Servidor con métricas custom
│   ├── Dockerfile      # Build de la imagen
│   └── requirements.txt
├── prometheus/         # Configuración de Prometheus
│   └── prometheus.yml
├── grafana/           # Configuración de Grafana
│   ├── provisioning/  # Datasources y dashboards
│   └── dashboards/    # JSONs de dashboards (FastAPI + Infra)
├── locust/            # Pruebas de carga
├── docker-compose.yml # Stack completo
└── README.md
```

## 🚀 Inicio rápido

```bash
# Levantar todo el stack
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f

# Detener y limpiar
docker compose down -v
```

## 🔗 endpoints

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| FastAPI App | http://localhost:8000 | - |
| FastAPI Docs | http://localhost:8000/docs | - |
| /metrics | http://localhost:8000/metrics | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin / admin |
| cAdvisor | http://localhost:8080 | - |
| Node Exporter | http://localhost:9100 | - |

## 📊 Características

- FastAPI instrumentado con prometheus_client
- Métricas HTTP: conteo, duración, requests activos
- Métricas de negocio: items total, errores
- Dashboards de Grafana preconfigurados
- cAdvisor para métricas de contenedores
- Node Exporter para métricas del host
- Pruebas de carga con Locust

## 🎯 Endpoints de ejemplo

- GET / — Info del servicio
- GET /items — Lista items (~10ms)
- GET /items/{id} — Item por ID (~50-150ms)
- POST /items — Crear item (~100-300ms)
- GET /slow — Endpoint lento (400ms-1.2s)
- GET /error — Error simulado (~30% fallo)
- GET /metrics — Exportación Prometheus

## 📝 Temas cubiertos

- Instrumentación de aplicaciones con Prometheus
- Configuración de scrape targets
- Uso de Histograms para latencias
- Dashboards en Grafana
- Monitoring de contenedores Docker
- Métricas del sistema operativo
