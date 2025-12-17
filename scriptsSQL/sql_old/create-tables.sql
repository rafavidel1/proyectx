-- Tabla de configuración de mesas (estática)
CREATE TABLE mesas (
    id SERIAL PRIMARY KEY,
    id_mesa VARCHAR(10) UNIQUE NOT NULL,  -- 'T1', 'T2', 'T3', etc.
    capacidad INTEGER NOT NULL,            -- 2, 4, 6, 8 personas
    activa BOOLEAN DEFAULT true,
    tipo VARCHAR(20) DEFAULT 'normal' -- Tipos: 'normal', 'premium', 'grande'
);

-- Tabla de horarios disponibles (configuración)
CREATE TABLE horarios_disponibles (
    id SERIAL PRIMARY KEY,
    dia_semana INTEGER NOT NULL,          -- 1=Lunes,..., 7=Domingo
    hora TIME NOT NULL,                    -- '13:00', '13:30', etc.
    activo BOOLEAN DEFAULT true,
    UNIQUE(dia_semana, hora)
);

-- Tabla de reservas (dinámica)
CREATE TABLE reservas (
    id SERIAL PRIMARY KEY,
    id_reserva VARCHAR(20) UNIQUE NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    id_mesa VARCHAR(10) REFERENCES mesas(id_mesa),
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    invitados INTEGER NOT NULL,
    estado VARCHAR(20) DEFAULT 'Reservado',  -- 'Reservado', 'Confirmado', 'Cancelado'
    notas TEXT,
    id_llamada VARCHAR(50),                  -- ID de VAPI
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Función que actualiza updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger que ejecuta la función en cada UPDATE
CREATE TRIGGER update_reservas_updated_at
    BEFORE UPDATE ON reservas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Tabla de bloqueos temporales (para la IA durante la llamada)
CREATE TABLE bloqueos_temporales (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    id_mesa VARCHAR(10) REFERENCES mesas(id_mesa),
    id_llamada VARCHAR(50) NOT NULL,       -- ID de VAPI call
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(fecha, hora, id_mesa)
);
--Duda:  no deberia de particionar la tabla reservas por fecha? debido a que en general todo se accede en funcion de esta.

CREATE TABLE informacion_llamadas (
    id SERIAL PRIMARY KEY,
    id_reserva VARCHAR(20) REFERENCES reservas(id_reserva),
    telefono VARCHAR(20),
    fecha_llamada TIMESTAMP,
    duracion_llamada INTEGER,  -- segundos
    motivo_finalizacion VARCHAR(50),
    peticiones_adicionales TEXT,
    coste_llamada NUMERIC(10, 4),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices para optimizar consultas
CREATE INDEX idx_reservas_fecha_hora ON reservas(fecha, hora);
CREATE INDEX idx_reservas_estado ON reservas(estado);
CREATE INDEX idx_bloqueos_temporales_llamada ON bloqueos_temporales(id_llamada);
CREATE INDEX idx_bloqueos_temporales_fecha ON bloqueos_temporales(fecha);