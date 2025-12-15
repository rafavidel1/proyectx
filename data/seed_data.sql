-- ==============================================
-- Floor Plan Manager - Datos de Ejemplo
-- Ejecutar después de init_db.sql
-- ==============================================

-- ==============================================
-- USUARIOS
-- ==============================================
INSERT INTO usuarios (username, password, nombre, rol) VALUES
    ('admin', 'admin123', 'Administrador', 'admin'),
    ('editor', 'editor123', 'Editor Principal', 'editor'),
    ('viewer', 'viewer123', 'Usuario Visor', 'viewer')
ON CONFLICT (username) DO NOTHING;

-- ==============================================
-- MESAS (T1 a T10)
-- ==============================================
INSERT INTO mesas (id_mesa, capacidad, tipo, zona, pos_x, pos_y) VALUES
    ('T1', 2, 'normal', 'interior', 80, 80),
    ('T2', 2, 'normal', 'interior', 220, 80),
    ('T3', 4, 'normal', 'interior', 360, 80),
    ('T4', 4, 'normal', 'interior', 500, 80),
    ('T5', 4, 'normal', 'interior', 80, 220),
    ('T6', 6, 'normal', 'interior', 220, 220),
    ('T7', 6, 'normal', 'interior', 360, 220),
    ('T8', 4, 'normal', 'terraza', 80, 80),
    ('T9', 4, 'normal', 'terraza', 220, 80),
    ('T10', 6, 'normal', 'terraza', 360, 80)
ON CONFLICT (id_mesa) DO NOTHING;

-- ==============================================
-- RESERVAS - HOY (14/12/2025) - CENA
-- ==============================================

-- Función para generar ID de reserva único
-- Formato: RESTA + 3 dígitos aleatorios

INSERT INTO reservas (id_reserva, fecha, hora, id_mesa, nombre, telefono, invitados, estado, notas) VALUES
    ('RESTA101', '2025-12-14', '20:00:00', 'T1', 'Juan García', '612345678', 2, 'Reservado', 'Aniversario'),
    ('RESTA102', '2025-12-14', '20:00:00', 'T3', 'María López', '623456789', 4, 'Reservado', 'Cumpleaños'),
    ('RESTA103', '2025-12-14', '20:30:00', 'T5', 'Pedro Martínez', '634567890', 3, 'Reservado', NULL),
    ('RESTA104', '2025-12-14', '20:30:00', 'T6', 'Ana Fernández', '645678901', 5, 'Reservado', 'Celebración familiar'),
    ('RESTA105', '2025-12-14', '21:00:00', 'T2', 'Carlos Ruiz', '656789012', 2, 'Reservado', NULL),
    ('RESTA106', '2025-12-14', '21:00:00', 'T4', 'Laura Sánchez', '667890123', 4, 'Reservado', 'Prefiere mesa tranquila'),
    ('RESTA107', '2025-12-14', '21:30:00', 'T7', 'Miguel Torres', '678901234', 6, 'Reservado', 'Grupo de amigos'),
    ('RESTA108', '2025-12-14', '21:30:00', 'T8', 'Elena Díaz', '689012345', 4, 'Reservado', 'Terraza si hace buen tiempo'),
    ('RESTA109', '2025-12-14', '22:00:00', 'T9', 'Roberto Moreno', '690123456', 4, 'Reservado', NULL),
    ('RESTA110', '2025-12-14', '22:00:00', 'T10', 'Isabel Navarro', '601234567', 6, 'Reservado', 'Despedida de soltero')
ON CONFLICT (id_reserva) DO NOTHING;

-- ==============================================
-- RESERVAS - MAÑANA (15/12/2025) - COMIDA
-- ==============================================
INSERT INTO reservas (id_reserva, fecha, hora, id_mesa, nombre, telefono, invitados, estado, notas) VALUES
    ('RESTA201', '2025-12-15', '13:00:00', 'T1', 'Antonio Vega', '612111222', 2, 'Reservado', 'Comida de negocios'),
    ('RESTA202', '2025-12-15', '13:00:00', 'T3', 'Carmen Blanco', '623222333', 4, 'Reservado', NULL),
    ('RESTA203', '2025-12-15', '13:30:00', 'T5', 'Francisco Rojo', '634333444', 4, 'Reservado', 'Menú del día'),
    ('RESTA204', '2025-12-15', '13:30:00', 'T6', 'Patricia Verde', '645444555', 5, 'Reservado', 'Alergia gluten'),
    ('RESTA205', '2025-12-15', '14:00:00', 'T2', 'Sergio Azul', '656555666', 2, 'Reservado', NULL),
    ('RESTA206', '2025-12-15', '14:00:00', 'T4', 'Natalia Gris', '667666777', 3, 'Reservado', 'Veganos'),
    ('RESTA207', '2025-12-15', '14:30:00', 'T7', 'Alberto Negro', '678777888', 6, 'Reservado', 'Comida empresa'),
    ('RESTA208', '2025-12-15', '14:30:00', 'T8', 'Cristina Rosa', '689888999', 4, 'Reservado', 'Terraza'),
    ('RESTA209', '2025-12-15', '15:00:00', 'T9', 'Daniel Marrón', '690999000', 4, 'Reservado', NULL),
    ('RESTA210', '2025-12-15', '15:00:00', 'T10', 'Lucía Dorado', '601000111', 6, 'Reservado', 'Celebración')
ON CONFLICT (id_reserva) DO NOTHING;

-- ==============================================
-- Verificación
-- ==============================================
SELECT 'Datos insertados correctamente' AS mensaje;
SELECT 'Usuarios: ' || COUNT(*) FROM usuarios;
SELECT 'Mesas: ' || COUNT(*) FROM mesas;
SELECT 'Reservas: ' || COUNT(*) FROM reservas;
