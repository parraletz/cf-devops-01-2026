# cf-devops-01-2026

Material de prácticas del **Bootcamp DevOps — Código Facilito**.  
Manifests de Kubernetes listos para aplicar en un cluster local (Minikube) o en la nube.

---

## Contenido del repositorio

```
cf-devops-01-2026/
└── clase-kubernetes/          # Clases 11 & 12 — Kubernetes 1.31
    ├── 00-namespace.yaml
    ├── 01-deployment.yaml
    ├── 02-service-clusterip.yaml
    ├── 03-service-loadbalancer.yaml
    ├── 04-configmap.yaml
    ├── 05-deployment-con-config.yaml
    ├── 06-secrets.yaml
    ├── 07-depl-secret.yaml
    ├── kustomization.yaml
    └── nginx.env
```

---

## Clase Kubernetes — Recursos cubiertos

| Archivo | Recurso | Descripción |
|---------|---------|-------------|
| `00-namespace.yaml` | Namespace | Espacio aislado `cf-demo` para todos los recursos |
| `01-deployment.yaml` | Deployment | nginx 1.29-alpine, 2 réplicas, RollingUpdate, health checks |
| `02-service-clusterip.yaml` | Service (ClusterIP) | Exposición interna dentro del cluster |
| `03-service-loadbalancer.yaml` | Service (LoadBalancer) | Exposición externa; usa `minikube tunnel` en local |
| `04-configmap.yaml` | ConfigMap | HTML personalizado + variables de entorno no sensibles |
| `05-deployment-con-config.yaml` | Deployment + ConfigMap | Monta el ConfigMap como volumen y como env vars |
| `06-secrets.yaml` | Secret (Opaque) | Variables sensibles de configuración de nginx |
| `07-depl-secret.yaml` | Deployment + Secret | Consume el Secret a través de `envFrom` |
| `kustomization.yaml` | Kustomize | Aplica todos los recursos de una sola vez |

---

## Requisitos

- [kubectl](https://kubernetes.io/docs/tasks/tools/) >= 1.28
- [Minikube](https://minikube.sigs.k8s.io/docs/) (o cualquier cluster Kubernetes 1.28+)

---

## Inicio rapido

### 1. Levantar Minikube

```bash
minikube start
```

### 2. Aplicar todos los recursos con Kustomize

```bash
kubectl apply -k clase-kubernetes/
```

### 3. Verificar el estado

```bash
kubectl get all -n cf-demo
```

---

## Aplicar recursos individuales

```bash
# Namespace (primero siempre)
kubectl apply -f clase-kubernetes/00-namespace.yaml

# Deployment base
kubectl apply -f clase-kubernetes/01-deployment.yaml -n cf-demo

# Services
kubectl apply -f clase-kubernetes/02-service-clusterip.yaml  -n cf-demo
kubectl apply -f clase-kubernetes/03-service-loadbalancer.yaml -n cf-demo

# ConfigMap y Deployment que lo consume
kubectl apply -f clase-kubernetes/04-configmap.yaml            -n cf-demo
kubectl apply -f clase-kubernetes/05-deployment-con-config.yaml -n cf-demo

# Secrets
kubectl apply -f clase-kubernetes/06-secrets.yaml
kubectl apply -f clase-kubernetes/07-depl-secret.yaml
```

---

## Acceder al servicio nginx

### Via LoadBalancer (Minikube tunnel)

```bash
# Terminal 1
minikube tunnel

# Terminal 2 — obtener la IP externa
kubectl get svc nginx-lb -n cf-demo

curl http://<EXTERNAL-IP>
```

### Via port-forward

```bash
kubectl port-forward svc/nginx-lb 8080:80 -n cf-demo
curl http://localhost:8080
```

### Probar ClusterIP desde dentro del cluster

```bash
kubectl run test --image=curlimages/curl -it --rm \
  -- curl http://nginx-clusterip.cf-demo
```

---

## Comandos utiles

```bash
# Ver pods y su estado
kubectl get pods -n cf-demo -l app=nginx

# Ver logs
kubectl logs -l app=nginx -n cf-demo

# Escalar el Deployment
kubectl scale deployment nginx --replicas=4 -n cf-demo

# Ver el HTML montado desde el ConfigMap
kubectl exec -it <pod-name> -n cf-demo \
  -- cat /usr/share/nginx/html/index.html

# Eliminar todos los recursos del namespace
kubectl delete namespace cf-demo

# Eliminar con Kustomize
kubectl delete -k clase-kubernetes/
```

---

## Conceptos clave

| Concepto | Descripcion |
|----------|-------------|
| **Namespace** | Aislamiento lógico de recursos dentro del cluster |
| **Deployment** | Controlador que garantiza N réplicas en ejecución (self-healing) |
| **ReplicaSet** | Gestionado por el Deployment; mantiene el número de Pods deseado |
| **RollingUpdate** | Actualiza Pods de uno en uno sin downtime |
| **ClusterIP** | Service solo accesible dentro del cluster |
| **LoadBalancer** | Service con IP externa; en cloud provisiona un LB real |
| **ConfigMap** | Configuración no sensible desacoplada de la imagen |
| **Secret** | Configuración sensible almacenada codificada en base64 |
| **Kustomize** | Gestión de manifests sin templates (built-in en kubectl) |

---

## Curso

**Bootcamp DevOps — Código Facilito**  
Kubernetes 1.31 · Clases 11 y 12
