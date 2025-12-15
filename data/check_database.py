"""
Script para verificar los datos en la base de datos.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'database'),
    'user': os.getenv('DB_USER', 'paco'),
    'password': os.getenv('DB_PASSWORD', 'paco')
}

def check_database():
    """Verifica el contenido de la base de datos."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("\n" + "="*50)
        print("VERIFICACIÓN DE BASE DE DATOS")
        print("="*50)
        
        # Usuarios
        print("\n[USUARIOS]")
        cursor.execute("SELECT id, username, password, nombre, rol FROM usuarios")
        usuarios = cursor.fetchall()
        for u in usuarios:
            print(f"  {u['id']}: {u['username']} / {u['password']} ({u['rol']})")
        
        # Mesas
        print("\n[MESAS]")
        cursor.execute("SELECT id_mesa, capacidad, tipo, pos_x, pos_y, activa FROM mesas ORDER BY id_mesa")
        mesas = cursor.fetchall()
        for m in mesas:
            status = "activa" if m['activa'] else "inactiva"
            print(f"  {m['id_mesa']}: {m['capacidad']} pers, {m['tipo']}, pos({m['pos_x']},{m['pos_y']}) [{status}]")
        
        # Reservas de hoy
        print("\n[RESERVAS HOY]")
        cursor.execute("""
            SELECT id_reserva, id_mesa, nombre, hora, invitados, estado 
            FROM reservas 
            WHERE fecha = CURRENT_DATE
            ORDER BY hora
        """)
        reservas = cursor.fetchall()
        if reservas:
            for r in reservas:
                print(f"  {r['id_mesa']} | {r['hora']} | {r['nombre']} ({r['invitados']} pers) - {r['estado']}")
        else:
            print("  (Sin reservas para hoy)")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*50 + "\n")
        
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == '__main__':
    check_database()
