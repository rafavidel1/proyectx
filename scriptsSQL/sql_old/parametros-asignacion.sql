-- Tabla de configuración de políticas (opcional, para cambiar sin tocar código)
CREATE TABLE politicas_asignacion (
    id SERIAL PRIMARY KEY,
    tipo_mesa VARCHAR(20),
    diferencia_maxima INTEGER,      -- +2 para normales
    ocupacion_minima_pct DECIMAL,   -- 0.75 para grandes
    ocupacion_minima_fallback DECIMAL -- 0.60 si no hay otras opciones
);

INSERT INTO public.politicas_asignacion VALUES 
(1, 'normal', 2, 1.0, 1.0),
(2, 'grande', 0, 0.75, 0.60);