# 🔄 Guía de Actualización de Componentes

Esta guía explica cómo actualizar cada servicio del stack con el **mínimo downtime** posible.

---

## 📦 Estructura del Stack

| Servicio   | Puerto | Datos Persistentes   |
| ---------- | ------ | -------------------- |
| PostgreSQL | 5432   | `./postgres_data/` |
| n8n        | 5678   | `./n8n_data/`      |
| Dashboard  | 5000   | (sin estado local)   |

---

## 1️⃣ Actualizar n8n

**Downtime estimado:** 5-10 segundos

### Paso 1: Descargar nueva imagen (sin parar)

```bash
docker pull n8nio/n8n:latest
# O una versión específica:
# docker pull n8nio/n8n:2.0.2
```

### Paso 2: Probar en paralelo (sin afectar servicio)

```bash
docker run -d \
  --name n8n_new \
  -v /home/ubuntu/Desarrollo/demo/n8n_data:/home/node/.n8n \
  n8nio/n8n:latest

# Verificar que arranca bien
docker logs -f n8n_new
# Buscar: "n8n ready" y "Editor is now accessible"
# Ctrl+C para salir de los logs
```

### Paso 3: Swap rápido (único momento de downtime)

```bash
docker stop n8n
docker rm n8n

docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v /home/ubuntu/Desarrollo/demo/n8n_data:/home/node/.n8n \
  n8nio/n8n:latest

docker stop n8n_new
docker rm n8n_new
```

### Paso 4: Verificar

```bash
docker ps
# Acceder a http://automatik.website:5678
```

---

## 2️⃣ Actualizar PostgreSQL

**⚠️ CUIDADO: Base de datos crítica**

**Downtime estimado:** 1-5 minutos (dependiendo de migración)

### Paso 1: Hacer backup ANTES

```bash
docker exec postgres_db pg_dumpall -U paco > backup_$(date +%Y%m%d_%H%M).sql
```

### Paso 2: Verificar versión actual

```bash
docker exec postgres_db postgres --version
```

### Paso 3: Descargar nueva imagen

```bash
docker pull postgres:16
# O para upgrade mayor (ej: 16 -> 17):
# docker pull postgres:17
```

### Paso 4: Actualización (solo parches menores)

```bash
# Para actualizaciones menores (16.x -> 16.y):
docker stop postgres_db
docker rm postgres_db

docker run -d \
  --name postgres_db \
  -p 5432:5432 \
  -e POSTGRES_USER=paco \
  -e POSTGRES_PASSWORD=paco \
  -e POSTGRES_DB=database \
  -v /home/ubuntu/Desarrollo/postgresql/data:/var/lib/postgresql/data \
  postgres:16
```

### ⚠️ Para upgrades mayores (ej: 15 → 16)

Requiere `pg_upgrade`. Proceso más complejo:

```bash
# 1. Backup completo
# 2. Nuevo contenedor con nueva versión
# 3. Restaurar desde backup
# 4. Verificar
```

---

## 3️⃣ Actualizar Dashboard (Código)

**Downtime estimado:** 10-30 segundos

### Opción A: Con Git (recomendado)

```bash
cd /home/ubuntu/Desarrollo/dashboard/proyectx

# Descargar cambios
git pull origin main

# Rebuild y restart
docker-compose up -d --build
```

### Opción B: Rebuild manual

```bash
cd /home/ubuntu/Desarrollo/dashboard/proyectx

# Para el servicio
docker stop floor_plan_dashboard

# Rebuild con nueva imagen
docker-compose build --no-cache dashboard

# Reiniciar
docker-compose up -d dashboard
```

### Opción C: Sin docker-compose

```bash
cd /home/ubuntu/Desarrollo/dashboard/proyectx

# Rebuild imagen
docker build -t proyectx_dashboard .

# Swap rápido
docker stop floor_plan_dashboard
docker rm floor_plan_dashboard

docker run -d \
  --name floor_plan_dashboard \
  -p 5000:5000 \
  --env-file .env \
  --network postgresql_default \
  proyectx_dashboard
```

---

## 🔧 Comandos Útiles

### Ver logs de cualquier servicio

```bash
docker logs -f floor_plan_dashboard
docker logs -f n8n
docker logs -f postgres_db
```

### Reiniciar un servicio sin rebuild

```bash
docker restart floor_plan_dashboard
docker restart n8n
docker restart postgres_db
```

### Ver uso de recursos

```bash
docker stats
```

### Limpiar imágenes viejas

```bash
docker image prune -a
```

---

## ⚡ Resumen Rápido

| Servicio             | Comando Rápido                                                                                                                                                                  |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **n8n**        | `docker pull n8nio/n8n && docker stop n8n && docker rm n8n && docker run -d --name n8n -p 5678:5678 -v /home/ubuntu/Desarrollo/demo/n8n_data:/home/node/.n8n n8nio/n8n:latest` |
| **Dashboard**  | `cd /path/to/proyectx && git pull && docker-compose up -d --build`                                                                                                             |
| **PostgreSQL** | Backup primero, luego `docker pull postgres:16 && docker-compose up -d postgres`                                                                                               |

---

## 📋 Checklist Pre-Actualización

- [ ] ¿Hice backup de PostgreSQL?
- [ ] ¿Probé la nueva imagen en paralelo?
- [ ] ¿Es horario de bajo tráfico?
- [ ] ¿Tengo acceso SSH al VPS?
- [ ] ¿Puedo hacer rollback si falla?
