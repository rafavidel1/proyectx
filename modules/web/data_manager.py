import json
import os

# Ruta al archivo JSON de datos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'restaurant_data.json')

def load_tables():
    """
    Lee todas las mesas desde el JSON.
    Retorna una lista de diccionarios.
    """
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Manejar ambos formatos: array directo o {"tables": [...]}
            if isinstance(data, list):
                return data
            return data.get('tables', [])
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo: {DATA_PATH}")
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON inválido: {e}")
        return []

def save_tables(tables):
    """
    Guarda la lista completa de mesas en el JSON.
    tables: lista de diccionarios
    """
    try:
        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump({'tables': tables}, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo guardar el JSON: {e}")
        return False

def get_table_by_id(table_id):
    """
    Busca una mesa específica por ID.
    Retorna el diccionario de la mesa o None si no existe.
    """
    tables = load_tables()
    for table in tables:
        if str(table.get('id')) == str(table_id):
            return table
    return None
