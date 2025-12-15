"""
Gestor de caché - Almacena temporalmente cambios antes de persistir.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
CACHE_FILE = os.path.join(CACHE_DIR, 'tables_cache.json')

# Asegurar que existe la carpeta cache
os.makedirs(CACHE_DIR, exist_ok=True)

class CacheManager:
    
    @staticmethod
    def save_to_cache(data: Dict[str, Any]) -> bool:
        """Guarda datos en caché con timestamp."""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[CacheManager] Error guardando en caché: {e}")
            return False
    
    @staticmethod
    def load_from_cache() -> Dict[str, Any]:
        """Carga datos desde caché."""
        try:
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    return cache_data.get('data', {})
            return {}
        except Exception as e:
            print(f"[CacheManager] Error cargando desde caché: {e}")
            return {}
    
    @staticmethod
    def clear_cache() -> bool:
        """Limpia el caché."""
        try:
            if os.path.exists(CACHE_FILE):
                os.remove(CACHE_FILE)
            return True
        except Exception as e:
            print(f"[CacheManager] Error limpiando caché: {e}")
            return False
