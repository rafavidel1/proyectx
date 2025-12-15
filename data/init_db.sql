-- ==============================================
-- Floor Plan Manager - Inicialización de Base de Datos
-- Ejecutar este script para crear las tablas
-- ==============================================

-- Eliminar tablas si existen (para desarrollo)
DROP TABLE IF EXISTS reservas CASCADE;
DROP TABLE IF EXISTS mesas CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;

-- ==============================================
-- TABLA: usuarios
-- ==============================================
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'viewer',
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para búsquedas por username
CREATE INDEX idx_usuarios_username ON usuarios(username);

-- ==============================================
-- TABLA: mesas
-- ==============================================
CREATE TABLE mesas (
    id SERIAL PRIMARY KEY,
    id_mesa VARCHAR(10) UNIQUE NOT NULL,
    capacidad INT NOT NULL DEFAULT 4,
    tipo VARCHAR(20) NOT NULL DEFAULT 'interior',
    activa BOOLEAN DEFAULT true,
    pos_x FLOAT DEFAULT 100,
    pos_y FLOAT DEFAULT 100,
    rotacion INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_mesas_id_mesa ON mesas(id_mesa);
CREATE INDEX idx_mesas_tipo ON mesas(tipo);
CREATE INDEX idx_mesas_activa ON mesas(activa);

-- ==============================================
-- TABLA: reservas
-- ==============================================
CREATE TABLE reservas (
    id SERIAL PRIMARY KEY,
    id_reserva VARCHAR(20) UNIQUE NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    id_mesa VARCHAR(10) NOT NULL REFERENCES mesas(id_mesa) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    invitados INT NOT NULL DEFAULT 2,
    estado VARCHAR(20) NOT NULL DEFAULT 'Reservado',
    notas TEXT,
    id_llamada VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para búsquedas frecuentes
CREATE INDEX idx_reservas_fecha ON reservas(fecha);
CREATE INDEX idx_reservas_id_mesa ON reservas(id_mesa);
CREATE INDEX idx_reservas_estado ON reservas(estado);
CREATE INDEX idx_reservas_fecha_hora ON reservas(fecha, hora);
CREATE INDEX idx_reservas_id_llamada ON reservas(id_llamada);

-- ==============================================
-- Función para actualizar updated_at automáticamente
-- ==============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para auto-update
CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mesas_updated_at BEFORE UPDATE ON mesas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reservas_updated_at BEFORE UPDATE ON reservas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==============================================
-- Mensaje de confirmación
-- ==============================================
SELECT 'Esquema creado correctamente' AS mensaje;
