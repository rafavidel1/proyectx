CREATE OR REPLACE FUNCTION check_availability(
    p_fecha DATE,
    p_hora TIME,
    p_invitados INTEGER,
    p_id_llamada VARCHAR DEFAULT NULL
)
RETURNS TABLE(
    disponible BOOLEAN,
    id_mesa VARCHAR,
    capacidad_mesa INTEGER,
    alternativas JSON
) AS $$
DECLARE
    mesa_disponible RECORD;
    hay_alternativas JSON;
    max_diferencia INTEGER;
BEGIN
    -- 1. Buscar mesa óptima con lógica de proximidad
    SELECT m.id_mesa, m.capacidad INTO mesa_disponible
    FROM mesas m
    WHERE m.activa = true
      -- Lógica de capacidad inteligente:
      AND (
          -- Mesas normales/pequeñas (<=6): permiten hasta +2 personas
          (m.tipo != 'grande' AND m.capacidad >= p_invitados AND m.capacidad <= p_invitados + 2)
          OR
          -- Mesas grandes (>=8): solo si el grupo es al menos 75% de su capacidad
          (m.tipo = 'grande' AND m.capacidad >= p_invitados AND p_invitados >= CEIL(m.capacidad * 0.75))
          OR
          -- Si solo quedan mesas grandes, permitir si el grupo es al menos 60%
          (m.tipo = 'grande' AND m.capacidad >= p_invitados AND p_invitados >= CEIL(m.capacidad * 0.60)
           AND NOT EXISTS (
               SELECT 1 FROM mesas m2 
               WHERE m2.activa = true 
                 AND m2.tipo != 'grande' 
                 AND m2.capacidad >= p_invitados
           ))
      )
      -- No existe reserva
      AND NOT EXISTS (
          SELECT 1 FROM reservas r
          WHERE r.id_mesa = m.id_mesa
            AND r.fecha = p_fecha
            AND r.hora = p_hora
            AND r.estado IN ('Reservado', 'Confirmado')
      )
      -- No existe bloqueo temporal de otra llamada
      AND NOT EXISTS (
          SELECT 1 FROM bloqueos_temporales bt
          WHERE bt.id_mesa = m.id_mesa
            AND bt.fecha = p_fecha
            AND bt.hora = p_hora
            AND (p_id_llamada IS NULL OR bt.id_llamada != p_id_llamada)
            AND bt.created_at > NOW() - INTERVAL '10 minutes'
      )
    ORDER BY 
        -- Prioridad 1: Mesa exacta
        CASE WHEN m.capacidad = p_invitados THEN 0 ELSE 1 END,
        -- Prioridad 2: Mesa más pequeña posible
        m.capacidad ASC,
        -- Prioridad 3: Preferir mesas normales sobre grandes
        CASE WHEN m.tipo = 'grande' THEN 1 ELSE 0 END
    LIMIT 1;

    -- 2. Si hay mesa disponible
    IF mesa_disponible IS NOT NULL THEN
        RETURN QUERY SELECT 
            true, 
            mesa_disponible.id_mesa, 
            mesa_disponible.capacidad,
            NULL::JSON;
        RETURN;
    END IF;

    -- 3. Si no hay disponibilidad, buscar alternativas en horas posteriores
    SELECT json_agg(json_build_object(
        'hora', alt.hora,
        'id_mesa', alt.id_mesa,
        'capacidad', alt.capacidad
    ) ORDER BY alt.hora ASC) INTO hay_alternativas
    FROM (
        SELECT DISTINCT h.hora, m.id_mesa, m.capacidad
        FROM horarios_disponibles h
        CROSS JOIN mesas m
        WHERE h.dia_semana = EXTRACT(DOW FROM p_fecha)
          AND h.hora > p_hora
          AND h.activo = true
          AND m.activa = true
          -- Aplicar misma lógica de capacidad
          AND (
              (m.tipo != 'grande' AND m.capacidad >= p_invitados AND m.capacidad <= p_invitados + 2)
              OR
              (m.tipo = 'grande' AND m.capacidad >= p_invitados AND p_invitados >= CEIL(m.capacidad * 0.75))
          )
          AND NOT EXISTS (
              SELECT 1 FROM reservas r
              WHERE r.id_mesa = m.id_mesa
                AND r.fecha = p_fecha
                AND r.hora = h.hora
                AND r.estado IN ('Reservado', 'Confirmado')
          )
          AND NOT EXISTS (
              SELECT 1 FROM bloqueos_temporales bt
              WHERE bt.id_mesa = m.id_mesa
                AND bt.fecha = p_fecha
                AND bt.hora = h.hora
                AND bt.created_at > NOW() - INTERVAL '10 minutes'
          )
        ORDER BY h.hora ASC, m.capacidad ASC
        LIMIT 5
    ) alt;

    RETURN QUERY SELECT false, NULL::VARCHAR, NULL::INTEGER, hay_alternativas;
END;
$$ LANGUAGE plpgsql;