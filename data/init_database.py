"""
Script para inicializar la base de datos.
Ejecuta los scripts SQL de creación y seed.
"""
import os
import sys

# Añadir directorio al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import psycopg2

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'database'),
    'user': os.getenv('DB_USER', 'paco'),
    'password': os.getenv('DB_PASSWORD', 'paco')
}

def read_sql_file(filename):
    """Lee un archivo SQL."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def execute_sql(sql, description="SQL"):
    """Ejecuta un script SQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print(f"[DB] Ejecutando {description}...")
        cursor.execute(sql)
        conn.commit()
        
        cursor.close()
        conn.close()
        print(f"[DB] {description} ejecutado correctamente")
        return True
    except Exception as e:
        print(f"[DB] Error en {description}: {e}")
        return False

def test_connection():
    """Prueba la conexión a la base de datos."""
    try:
        print(f"[DB] Conectando a {DB_CONFIG['host']}:{DB_CONFIG['port']}...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"[DB] Conexión exitosa!")
        print(f"[DB] PostgreSQL: {version[0][:50]}...")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB] Error de conexión: {e}")
        return False

def init_database():
    """Inicializa la base de datos con las tablas y datos."""
    print("\n" + "="*50)
    print("INICIALIZACIÓN DE BASE DE DATOS")
    print("="*50 + "\n")
    
    # Test conexión
    if not test_connection():
        print("\n[ERROR] No se puede conectar a la base de datos")
        return False
    
    # Ejecutar esquema
    print("\n[1/2] Creando esquema...")
    init_sql = read_sql_file('init_db.sql')
    if not execute_sql(init_sql, "init_db.sql"):
        return False
    
    # Ejecutar datos
    print("\n[2/2] Insertando datos de ejemplo...")
    seed_sql = read_sql_file('seed_data.sql')
    if not execute_sql(seed_sql, "seed_data.sql"):
        return False
    
    print("\n" + "="*50)
    print("BASE DE DATOS INICIALIZADA CORRECTAMENTE")
    print("="*50 + "\n")
    
    return True

def show_stats():
    """Muestra estadísticas de la base de datos."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("\n[ESTADÍSTICAS]")
        
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        print(f"  Usuarios: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM mesas")
        print(f"  Mesas: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM reservas")
        print(f"  Reservas: {cursor.fetchone()[0]}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_connection()
    elif len(sys.argv) > 1 and sys.argv[1] == '--stats':
        show_stats()
    else:
        if init_database():
            show_stats()
