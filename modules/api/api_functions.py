"""
API Functions - Funciones de lógica de negocio para los endpoints.
Delegan al módulo de base de datos.
"""
from typing import Dict, Any, List
from datetime import date
from modules.db_module import (
    # Auth
    iniciar_sesion,
    obtener_usuario_por_id,
    # Mesas
    obtener_mesas_con_estado,
    crear_mesa,
    actualizar_mesa,
    actualizar_posicion_mesa,
    eliminar_mesa,
    # Reservas
    crear_reserva,
    ocupar_mesa_sin_reserva,
    marcar_mesa_ocupada,
    liberar_mesa,
    # Disponibilidad
    obtener_disponibilidad,
    crear_bloqueo_temporal,
    eliminar_bloqueo_temporal
)

# ==============================================
# AUTENTICACIÓN
# ==============================================

def login(username: str, password: str) -> Dict[str, Any]:
    """Autentica un usuario."""
    user = iniciar_sesion(username, password)
    if user:
        return {
            'success': True,
            'message': 'Login exitoso',
            'user': user
        }
    return {
        'success': False,
        'message': 'Credenciales inválidas'
    }

def get_user(user_id: int) -> Dict[str, Any]:
    """Obtiene datos de un usuario por ID."""
    user = obtener_usuario_por_id(user_id)
    if user:
        return {'success': True, 'user': user}
    return {'success': False, 'message': 'Usuario no encontrado'}

# ==============================================
# MESAS
# ==============================================

def get_tables(fecha: str = None, turno: str = None) -> List[Dict[str, Any]]:
    """Obtiene todas las mesas con su estado para una fecha y turno."""
    if fecha is None:
        fecha = date.today().isoformat()
    return obtener_mesas_con_estado(fecha, turno)

def create_table(capacidad: int, zona: str) -> Dict[str, Any]:
    """Crea una nueva mesa."""
    return crear_mesa(capacidad, zona)

def update_table(id_mesa: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Actualiza una mesa."""
    return actualizar_mesa(id_mesa, data)

def update_table_position(id_mesa: str, x: float, y: float) -> Dict[str, Any]:
    """Actualiza la posición de una mesa."""
    return actualizar_posicion_mesa(id_mesa, x, y)

def delete_table(id_mesa: str) -> Dict[str, Any]:
    """Elimina una mesa."""
    return eliminar_mesa(id_mesa)

# ==============================================
# RESERVAS
# ==============================================

def reserve_table(id_mesa: str, customer_name: str, time: str, 
                  people: int, fecha: str = None, telefono: str = '',
                  notas: str = '') -> Dict[str, Any]:
    """Crea una reserva con todos los datos."""
    if fecha is None:
        fecha = date.today().isoformat()
    
    # Convertir hora a formato HH:MM:SS si viene como HH:MM
    if len(time) == 5:
        time = f"{time}:00"
    
    return crear_reserva(id_mesa, customer_name, fecha, time, people, telefono, notas)

def occupy_table(id_mesa: str, fecha: str = None, turno: str = None) -> Dict[str, Any]:
    """Ocupa una mesa sin reserva (walk-in)."""
    return ocupar_mesa_sin_reserva(id_mesa, fecha, turno)

def mark_as_occupied(id_mesa: str, fecha: str = None) -> Dict[str, Any]:
    """Marca una mesa reservada como ocupada."""
    if fecha is None:
        fecha = date.today().isoformat()
    return marcar_mesa_ocupada(id_mesa, fecha)

def free_table(id_mesa: str, fecha: str = None) -> Dict[str, Any]:
    """Libera una mesa."""
    return liberar_mesa(id_mesa, fecha)

# ==============================================
# DISPONIBILIDAD
# ==============================================

def check_availability(fecha: str, hora: str, invitados: int, 
                       id_llamada: str = None) -> List[Dict[str, Any]]:
    """Consulta disponibilidad de mesas."""
    return obtener_disponibilidad(fecha, hora, invitados, id_llamada)

def create_temporary_block(id_mesa: str, fecha: str, hora: str, 
                           id_llamada: str) -> Dict[str, Any]:
    """Crea un bloqueo temporal."""
    return crear_bloqueo_temporal(id_mesa, fecha, hora, id_llamada)

def remove_temporary_block(id_llamada: str) -> Dict[str, Any]:
    """Elimina un bloqueo temporal."""
    return eliminar_bloqueo_temporal(id_llamada)
