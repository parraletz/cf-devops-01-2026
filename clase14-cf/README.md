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
- cAdvisor para métricas de contenedores y cgroups
- Node Exporter para métricas del host
- Pruebas de carga con Locust

## ⚠️ Nota sobre el dashboard de Infra (cAdvisor)

El dashboard "CF — Infraestructura (Docker + Host)" cuenta **cgroups**, no únicamente contenedores Docker reales. cAdvisor reporta todos los cgroups del sistema, incluyendo:

- Contenedores Docker (cf-fastapi, etc.)
- Pods de Kubernetes/Minikube (generan múltiples cgroups)
- Servicios del sistema (system.slice)
- Sesiones de usuario (user.slice)

Actualmente muestra **~70 cgroups** porque minikube está ejecutando Kubernetes con muchos Pods, cada uno reportado como un cgroup distinto. El único contenedor Docker real corriendo es `cf-fastapi` (más minikube, grafana, prometheus, node-exporter, locust = 6 contenedores en total).

Verifying: `docker ps -a` mostrará **7 contenedores reales**, pero cAdvisor mostrará **~70 cgroups**.

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
