"""
Servicio de gestión de mesas.
"""
from typing import List, Dict, Any, Optional
import uuid
from modules.web.data_manager import load_tables, save_tables
from modules.web.cache_manager import CacheManager

class TableService:
    
    @staticmethod
    def get_all_tables() -> List[Dict[str, Any]]:
        """Obtiene todas las mesas del sistema."""
        return load_tables()
    
    @staticmethod
    def get_table_by_id(table_id: str) -> Optional[Dict[str, Any]]:
        """Busca una mesa por ID."""
        tables = load_tables()
        for table in tables:
            if str(table.get('id')) == str(table_id):
                return table
        return None
    
    @staticmethod
    def create_table(name: str, zone: str, capacity: int, x: float, y: float) -> Dict[str, Any]:
        """Crea una nueva mesa."""
        try:
            tables = load_tables()
            
            # Generar ID único
            new_id = str(len(tables) + 1)
            while any(t.get('id') == new_id for t in tables):
                new_id = str(int(new_id) + 1)
            
            new_table = {
                "id": new_id,
                "name": name,
                "zone": zone,
                "x": round(float(x), 2),
                "y": round(float(y), 2),
                "capacity": int(capacity),
                "rotation": 0,
                "status": "free",
                "reservation_info": None
            }
            
            tables.append(new_table)
            save_tables(tables)
            CacheManager.save_to_cache({'tables': tables})
            
            return {
                "success": True,
                "message": "Mesa creada exitosamente",
                "table": new_table
            }
        except Exception as e:
            print(f"[TableService] Error creando mesa: {e}")
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def update_table(table_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza propiedades de una mesa (nombre, capacidad, etc.)."""
        try:
            tables = load_tables()
            
            for table in tables:
                if str(table.get('id')) == str(table_id):
                    # Actualizar campos permitidos
                    if 'name' in data:
                        table['name'] = data['name']
                    if 'capacity' in data:
                        table['capacity'] = int(data['capacity'])
                    if 'zone' in data:
                        table['zone'] = data['zone']
                    if 'rotation' in data:
                        table['rotation'] = int(data['rotation'])
                    
                    save_tables(tables)
                    CacheManager.save_to_cache({'tables': tables})
                    
                    return {
                        "success": True,
                        "message": "Mesa actualizada",
                        "table": table
                    }
            
            return {"success": False, "message": "Mesa no encontrada"}
        except Exception as e:
            print(f"[TableService] Error actualizando mesa: {e}")
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def delete_table(table_id: str) -> Dict[str, Any]:
        """Elimina una mesa del sistema."""
        try:
            tables = load_tables()
            original_count = len(tables)
            
            tables = [t for t in tables if str(t.get('id')) != str(table_id)]
            
            if len(tables) == original_count:
                return {"success": False, "message": "Mesa no encontrada"}
            
            save_tables(tables)
            CacheManager.save_to_cache({'tables': tables})
            
            return {
                "success": True,
                "message": "Mesa eliminada exitosamente"
            }
        except Exception as e:
            print(f"[TableService] Error eliminando mesa: {e}")
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def update_table_position(table_id: str, x: float, y: float) -> Dict[str, Any]:
        """Actualiza la posición de una mesa en el mapa."""
        try:
            tables = load_tables()
            
            for table in tables:
                if str(table.get('id')) == str(table_id):
                    table['x'] = round(float(x), 2)
                    table['y'] = round(float(y), 2)
                    
                    save_tables(tables)
                    CacheManager.save_to_cache({'tables': tables})
                    
                    return {
                        "success": True,
                        "message": "Posición actualizada",
                        "table": table
                    }
            
            return {"success": False, "message": "Mesa no encontrada"}
        except Exception as e:
            print(f"[TableService] Error: {e}")
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def get_tables_by_zone(zone: str) -> List[Dict[str, Any]]:
        """Filtra mesas por zona (interior/terraza)."""
        tables = load_tables()
        return [t for t in tables if t.get('zone') == zone]
