#!/bin/bash
# ========================================
# Deploy Script para Floor Plan Dashboard
# ========================================
# Ejecutar en el VPS después de clonar/copiar el código

set -e

echo "=========================================="
echo "FLOOR PLAN DASHBOARD - Deployment Script"
echo "=========================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    echo "ERROR: No se encuentra docker-compose.yml"
    echo "Ejecuta este script desde el directorio del proyecto"
    exit 1
fi

# Verificar que existe el archivo .env
if [ ! -f ".env" ]; then
    echo "ADVERTENCIA: No existe archivo .env"
    echo "Copiando .env.example a .env..."
    cp .env.example .env
    echo "IMPORTANTE: Edita .env con tus credenciales antes de continuar"
    echo "Comando: nano .env"
    exit 1
fi

# Verificar que la red postgresql_default existe
if ! docker network ls | grep -q "postgresql_default"; then
    echo "ERROR: La red postgresql_default no existe"
    echo "Asegúrate de que PostgreSQL está corriendo"
    exit 1
fi

echo ""
echo "1. Construyendo imagen Docker..."
docker-compose build

echo ""
echo "2. Iniciando servicio de inicialización de BD..."
docker-compose up postgres_init

echo ""
echo "3. Iniciando Dashboard..."
docker-compose up -d dashboard

echo ""
echo "4. Verificando estado..."
sleep 3
docker-compose ps

echo ""
echo "=========================================="
echo "✓ DEPLOYMENT COMPLETADO"
echo "=========================================="
echo ""
echo "Dashboard disponible en: http://automatik.website:5000"
echo ""
echo "Comandos útiles:"
echo "  - Ver logs:     docker-compose logs -f dashboard"
echo "  - Reiniciar:    docker-compose restart dashboard"
echo "  - Parar:        docker-compose down"
echo "  - Estado:       docker-compose ps"
echo ""
