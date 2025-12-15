"""
Script de migración para añadir columna 'zona' a la tabla mesas
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

cur = conn.cursor()

print("Ejecutando migración...")

# Añadir columna zona si no existe
cur.execute("ALTER TABLE mesas ADD COLUMN IF NOT EXISTS zona VARCHAR(20) DEFAULT 'interior'")
print("✓ Columna 'zona' añadida")

# Copiar valores de tipo a zona (si tipo era interior/terraza)
cur.execute("UPDATE mesas SET zona = tipo WHERE tipo IN ('interior', 'terraza')")
print("✓ Valores copiados de 'tipo' a 'zona'")

# Poner tipo = 'normal' en todas las mesas
cur.execute("UPDATE mesas SET tipo = 'normal'")
print("✓ Columna 'tipo' actualizada a 'normal'")

conn.commit()
print("\n✅ Migración completada exitosamente")

cur.close()
conn.close()
