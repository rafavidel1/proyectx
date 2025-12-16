#!/bin/bash
# ============================================================
# Script de Migración al Stack Unificado
# ============================================================
# Este script migra tu configuración actual a un stack unificado
# 
# ANTES DE EJECUTAR:
# 1. Asegúrate de que los contenedores actuales están parados
# 2. Haz backup de tus datos
# ============================================================

set -e

echo "=============================================="
echo "MIGRACIÓN AL STACK UNIFICADO"
echo "=============================================="

# Directorio base
STACK_DIR="/home/ubuntu/Desarrollo/stack"

# Crear estructura
echo "1. Creando estructura de directorios..."
mkdir -p $STACK_DIR
cd $STACK_DIR

# Parar contenedores actuales
echo "2. Parando contenedores actuales..."
docker stop floor_plan_dashboard n8n postgres_db 2>/dev/null || true

# Copiar datos de PostgreSQL
echo "3. Migrando datos de PostgreSQL..."
if [ -d "/home/ubuntu/Desarrollo/postgresql/data" ]; then
    cp -r /home/ubuntu/Desarrollo/postgresql/data $STACK_DIR/postgres_data
    echo "   ✓ Datos PostgreSQL copiados"
else
    echo "   ! No se encontraron datos PostgreSQL existentes"
fi

# Copiar datos de n8n
echo "4. Migrando datos de n8n..."
if [ -d "/home/ubuntu/Desarrollo/demo/n8n_data" ]; then
    cp -r /home/ubuntu/Desarrollo/demo/n8n_data $STACK_DIR/n8n_data
    echo "   ✓ Datos n8n copiados"
else
    echo "   ! No se encontraron datos n8n existentes"
fi

# Clonar/copiar dashboard
echo "5. Configurando dashboard..."
if [ -d "/home/ubuntu/Desarrollo/dashboard/proyectx" ]; then
    cp -r /home/ubuntu/Desarrollo/dashboard/proyectx $STACK_DIR/dashboard
    echo "   ✓ Dashboard copiado"
else
    echo "   ! Dashboard no encontrado, clónalo manualmente"
fi

# Crear .env
echo "6. Creando archivo .env..."
cat > $STACK_DIR/.env << 'EOF'
# PostgreSQL
DB_USER=paco
DB_PASSWORD=paco
DB_NAME=database

# Flask Dashboard
FLASK_SECRET_KEY=cambia-esto-por-una-clave-secreta-larga
HORA_CORTE_TURNO=17:00:00
HORA_INICIO_COMIDA=12:00:00
HORA_FIN_COMIDA=16:00:00
HORA_INICIO_CENA=20:00:00
HORA_FIN_CENA=23:00:00

# n8n
N8N_WEBHOOK_URL=http://automatik.website:5678/
EOF
echo "   ✓ .env creado"

# Crear docker-compose.yml
echo "7. Creando docker-compose.yml..."
cat > $STACK_DIR/docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16
    container_name: postgres_db
    restart: always
    environment:
      POSTGRES_USER: ${DB_USER:-paco}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-paco}
      POSTGRES_DB: ${DB_NAME:-database}
    ports:
      - "5432:5432"
    volumes:
      - ./postgres_data:/var/lib/postgresql/data
    networks:
      - app_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-paco}"]
      interval: 10s
      timeout: 5s
      retries: 5

  n8n:
    image: n8nio/n8n
    container_name: n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=0.0.0.0
      - GENERIC_TIMEZONE=Europe/Madrid
    volumes:
      - ./n8n_data:/home/node/.n8n
    networks:
      - app_network
    depends_on:
      postgres:
        condition: service_healthy

  dashboard:
    build: ./dashboard
    container_name: floor_plan_dashboard
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - FLASK_SECRET_KEY=${FLASK_SECRET_KEY:-dev-secret-key}
      - FLASK_DEBUG=false
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=${DB_NAME:-database}
      - DB_USER=${DB_USER:-paco}
      - DB_PASSWORD=${DB_PASSWORD:-paco}
      - HORA_CORTE_TURNO=${HORA_CORTE_TURNO:-17:00:00}
      - HORA_INICIO_COMIDA=${HORA_INICIO_COMIDA:-12:00:00}
      - HORA_FIN_COMIDA=${HORA_FIN_COMIDA:-16:00:00}
      - HORA_INICIO_CENA=${HORA_INICIO_CENA:-20:00:00}
      - HORA_FIN_CENA=${HORA_FIN_CENA:-23:00:00}
    networks:
      - app_network
    depends_on:
      postgres:
        condition: service_healthy

networks:
  app_network:
    driver: bridge
EOF
echo "   ✓ docker-compose.yml creado"

# Eliminar contenedores viejos
echo "8. Limpiando contenedores antiguos..."
docker rm floor_plan_dashboard n8n postgres_db 2>/dev/null || true

echo ""
echo "=============================================="
echo "✓ MIGRACIÓN COMPLETADA"
echo "=============================================="
echo ""
echo "Estructura creada en: $STACK_DIR"
echo ""
echo "Para iniciar el stack:"
echo "  cd $STACK_DIR"
echo "  docker-compose up -d --build"
echo ""
echo "Servicios disponibles:"
echo "  - Dashboard: http://automatik.website:5000"
echo "  - n8n:       http://automatik.website:5678"
echo "  - PostgreSQL: localhost:5432"
echo ""
