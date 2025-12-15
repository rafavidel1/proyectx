"""
Servicio de gestión de reservas.
Maneja la lógica de negocio de reservas, cancelaciones y ocupación.
"""
from typing import Dict, Any
from modules.web.data_manager import load_tables, save_tables

class ReservationService:
    
    @staticmethod
    def create_reservation(table_id: str, customer_name: str, time: str, people: int) -> Dict[str, Any]:
        """Crea una nueva reserva en una mesa."""
        tables = load_tables()
        
        for table in tables:
            if str(table.get('id')) == str(table_id):
                
                # Validaciones de negocio
                if table.get('status') in ['reserved', 'occupied']:
                    return {
                        "success": False,
                        "message": "La mesa no está disponible"
                    }
                
                if people > table.get('capacity', 0):
                    return {
                        "success": False,
                        "message": f"Capacidad máxima: {table.get('capacity')} personas"
                    }
                
                # Crear reserva
                table['status'] = 'reserved'
                table['reservation_info'] = {
                    'customer_name': customer_name,
                    'time': time,
                    'people': people
                }
                
                save_tables(tables)
                return {
                    "success": True,
                    "message": "Reserva creada exitosamente",
                    "table": table
                }
        
        return {"success": False, "message": "Mesa no encontrada"}
    
    @staticmethod
    def occupy_without_reservation(table_id: str) -> Dict[str, Any]:
        """
        Marca una mesa como ocupada sin reserva previa (walk-in).
        No requiere datos del cliente.
        """
        tables = load_tables()
        
        for table in tables:
            if str(table.get('id')) == str(table_id):
                
                if table.get('status') in ['reserved', 'occupied']:
                    return {
                        "success": False,
                        "message": "La mesa no está disponible"
                    }
                
                # Ocupar sin datos de cliente
                table['status'] = 'occupied'
                table['reservation_info'] = {
                    'customer_name': 'Cliente sin reserva',
                    'time': 'Walk-in',
                    'people': None
                }
                
                save_tables(tables)
                return {
                    "success": True,
                    "message": "Mesa ocupada (walk-in)",
                    "table": table
                }
        
        return {"success": False, "message": "Mesa no encontrada"}
    
    @staticmethod
    def mark_as_occupied(table_id: str) -> Dict[str, Any]:
        """Marca una mesa reservada como ocupada (el cliente llegó)."""
        tables = load_tables()
        
        for table in tables:
            if str(table.get('id')) == str(table_id):
                
                if table.get('status') != 'reserved':
                    return {
                        "success": False,
                        "message": "La mesa no tiene reserva activa"
                    }
                
                table['status'] = 'occupied'
                
                save_tables(tables)
                return {
                    "success": True,
                    "message": "Mesa marcada como ocupada",
                    "table": table
                }
        
        return {"success": False, "message": "Mesa no encontrada"}
    
    @staticmethod
    def cancel_reservation(table_id: str) -> Dict[str, Any]:
        """Cancela una reserva o libera una mesa ocupada."""
        tables = load_tables()
        
        for table in tables:
            if str(table.get('id')) == str(table_id):
                
                if table.get('status') == 'free':
                    return {
                        "success": False,
                        "message": "La mesa ya está libre"
                    }
                
                table['status'] = 'free'
                table['reservation_info'] = None
                
                save_tables(tables)
                return {
                    "success": True,
                    "message": "Mesa liberada",
                    "table": table
                }
        
        return {"success": False, "message": "Mesa no encontrada"}
