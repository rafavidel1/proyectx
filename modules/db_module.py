"""
Módulo de Base de Datos PostgreSQL
Maneja toda la conectividad y lógica de negocio con la base de datos.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, List, Optional
from datetime import datetime, date, time
from contextlib import contextmanager

# Cargar variables de entorno desde .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv no instalado, usar variables del sistema

# ==============================================
# CONFIGURACIÓN
# ==============================================

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'database'),
    'user': os.getenv('DB_USER', 'paco'),
    'password': os.getenv('DB_PASSWORD', 'paco')
}

# Horarios de turnos
HORA_CORTE_TURNO = os.getenv('HORA_CORTE_TURNO', '17:00:00')
HORA_INICIO_COMIDA = os.getenv('HORA_INICIO_COMIDA', '12:00:00')
HORA_FIN_COMIDA = os.getenv('HORA_FIN_COMIDA', '16:00:00')
HORA_INICIO_CENA = os.getenv('HORA_INICIO_CENA', '20:00:00')
HORA_FIN_CENA = os.getenv('HORA_FIN_CENA', '23:00:00')

# ==============================================
# CONEXIÓN
# ==============================================

@contextmanager
def get_db_connection():
    """Context manager para conexiones a la base de datos."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        yield conn
    except psycopg2.Error as e:
        print(f"[DB] Error de conexión: {e}")
        raise
    finally:
        if conn:
            conn.close()

@contextmanager
def get_db_cursor(commit=True):
    """Context manager para obtener un cursor con auto-commit."""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            if commit:
                conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            print(f"[DB] Error en query: {e}")
            raise

def test_connection() -> bool:
    """Prueba la conexión a la base de datos."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"[DB] Error de conexión: {e}")
        return False

# ==============================================
# AUTENTICACIÓN - USUARIOS
# ==============================================

def iniciar_sesion(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Verifica credenciales y devuelve datos del usuario o None.
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT id, username, nombre, rol 
                FROM usuarios 
                WHERE username = %s AND password = %s AND activo = true
            """, (username, password))
            
            user = cursor.fetchone()
            if user:
                # Normalizar 'rol' a 'role' para el frontend
                return {
                    'id': user['id'],
                    'username': user['username'],
                    'name': user['nombre'],
                    'role': user['rol']  # Frontend espera 'role'
                }
            return None
    except Exception as e:
        print(f"[DB] Error en login: {e}")
        return None

def obtener_usuario_por_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un usuario por su ID."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT id, username, nombre, rol 
                FROM usuarios 
                WHERE id = %s AND activo = true
            """, (user_id,))
            
            user = cursor.fetchone()
            if user:
                return {
                    'id': user['id'],
                    'username': user['username'],
                    'name': user['nombre'],
                    'role': user['rol']
                }
            return None
    except Exception as e:
        print(f"[DB] Error: {e}")
        return None

# ==============================================
# MESAS - CRUD
# ==============================================

def obtener_todas_las_mesas() -> List[Dict[str, Any]]:
    """Obtiene todas las mesas activas."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT id, id_mesa, capacidad, tipo, activa, pos_x, pos_y, rotacion
                FROM mesas 
                WHERE activa = true
                ORDER BY id_mesa
            """)
            
            mesas = cursor.fetchall()
            # Transformar al formato esperado por el frontend
            return [{
                'id': m['id_mesa'],  # Usar id_mesa como id para el frontend
                'name': f"Mesa {m['id_mesa'][1:]}",  # T1 -> Mesa 1
                'capacity': m['capacidad'],
                'zone': m['tipo'],
                'x': m['pos_x'],
                'y': m['pos_y'],
                'rotation': m['rotacion'],
                'status': 'free',  # Se actualizará con las reservas
                'reservation_info': None
            } for m in mesas]
    except Exception as e:
        print(f"[DB] Error obteniendo mesas: {e}")
        return []

def obtener_mesas_con_estado(fecha: str = None, turno: str = None) -> List[Dict[str, Any]]:
    """
    Obtiene mesas con su estado de reserva para una fecha y turno dados.
    
    Args:
        fecha: Fecha en formato YYYY-MM-DD (default: hoy)
        turno: 'mediodia' o 'noche' (default: según hora actual)
    
    Returns:
        Lista de mesas con su estado
    """
    if fecha is None:
        fecha = date.today().isoformat()
    
    # Determinar turno si no se especifica
    if turno is None:
        hora_actual = datetime.now().time()
        corte = datetime.strptime(HORA_CORTE_TURNO, '%H:%M:%S').time()
        turno = 'mediodia' if hora_actual < corte else 'noche'
    
    # Definir rango horario según turno
    if turno == 'mediodia':
        hora_inicio = '00:00:00'
        hora_fin = HORA_CORTE_TURNO
    else:  # noche
        hora_inicio = HORA_CORTE_TURNO
        hora_fin = '23:59:59'
    
    try:
        with get_db_cursor() as cursor:
            # Obtener mesas
            cursor.execute("""
                SELECT id, id_mesa, capacidad, tipo, zona, pos_x, pos_y, rotacion
                FROM mesas 
                WHERE activa = true
                ORDER BY id_mesa
            """)
            mesas = cursor.fetchall()
            
            # Obtener reservas del día Y turno
            cursor.execute("""
                SELECT id_mesa, nombre, hora, invitados, estado
                FROM reservas 
                WHERE fecha = %s 
                  AND estado IN ('Reservado', 'Ocupado')
                  AND hora >= %s::time 
                  AND hora < %s::time
            """, (fecha, hora_inicio, hora_fin))
            reservas = {r['id_mesa']: r for r in cursor.fetchall()}
            
            result = []
            for m in mesas:
                mesa_data = {
                    'id': m['id_mesa'],
                    'name': f"Mesa {m['id_mesa'][1:]}",
                    'capacity': m['capacidad'],
                    'type': m['tipo'],
                    'zone': m['zona'],
                    'x': m['pos_x'],
                    'y': m['pos_y'],
                    'rotation': m['rotacion'],
                    'status': 'free',
                    'reservation_info': None
                }
                
                # Verificar si tiene reserva en este turno
                if m['id_mesa'] in reservas:
                    res = reservas[m['id_mesa']]
                    mesa_data['status'] = 'occupied' if res['estado'] == 'Ocupado' else 'reserved'
                    mesa_data['reservation_info'] = {
                        'customer_name': res['nombre'],
                        'time': str(res['hora'])[:5],  # HH:MM
                        'people': res['invitados']
                    }
                
                result.append(mesa_data)
            
            return result
    except Exception as e:
        print(f"[DB] Error: {e}")
        return []

def crear_mesa(capacidad: int, tipo: str = 'interior') -> Dict[str, Any]:
    """
    Crea una nueva mesa con ID auto-generado.
    El nombre se genera automáticamente (T11, T12, etc.)
    """
    try:
        with get_db_cursor() as cursor:
            # Obtener el siguiente número de mesa
            cursor.execute("""
                SELECT COALESCE(MAX(CAST(SUBSTRING(id_mesa FROM 2) AS INTEGER)), 0) + 1 as next_num
                FROM mesas
            """)
            next_num = cursor.fetchone()['next_num']
            id_mesa = f"T{next_num}"
            
            # Calcular posición inicial
            pos_x = 80 + ((next_num - 1) % 4) * 150
            pos_y = 80 + ((next_num - 1) // 4) * 140
            
            cursor.execute("""
                INSERT INTO mesas (id_mesa, capacidad, tipo, zona, pos_x, pos_y)
                VALUES (%s, %s, 'normal', %s, %s, %s)
                RETURNING id, id_mesa, capacidad, tipo, zona, pos_x, pos_y, rotacion
            """, (id_mesa, capacidad, tipo, pos_x, pos_y))
            
            mesa = cursor.fetchone()
            
            return {
                'success': True,
                'message': 'Mesa creada',
                'table': {
                    'id': mesa['id_mesa'],
                    'name': f"Mesa {next_num}",
                    'capacity': mesa['capacidad'],
                    'type': mesa['tipo'],
                    'zone': mesa['zona'],
                    'x': mesa['pos_x'],
                    'y': mesa['pos_y'],
                    'rotation': mesa['rotacion'],
                    'status': 'free',
                    'reservation_info': None
                }
            }
    except Exception as e:
        print(f"[DB] Error creando mesa: {e}")
        return {'success': False, 'message': str(e)}

def actualizar_mesa(id_mesa: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Actualiza una mesa existente."""
    try:
        with get_db_cursor() as cursor:
            updates = []
            values = []
            
            if 'capacity' in data:
                updates.append("capacidad = %s")
                values.append(data['capacity'])
            if 'zone' in data:
                updates.append("tipo = %s")
                values.append(data['zone'])
            if 'rotation' in data:
                updates.append("rotacion = %s")
                values.append(data['rotation'])
                
            if not updates:
                return {'success': False, 'message': 'No hay datos para actualizar'}
            
            values.append(id_mesa)
            cursor.execute(f"""
                UPDATE mesas SET {', '.join(updates)}
                WHERE id_mesa = %s
                RETURNING id_mesa, capacidad, tipo
            """, values)
            
            if cursor.rowcount == 0:
                return {'success': False, 'message': 'Mesa no encontrada'}
            
            return {'success': True, 'message': 'Mesa actualizada'}
    except Exception as e:
        print(f"[DB] Error: {e}")
        return {'success': False, 'message': str(e)}

def actualizar_posicion_mesa(id_mesa: str, x: float, y: float) -> Dict[str, Any]:
    """Actualiza la posición de una mesa."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                UPDATE mesas SET pos_x = %s, pos_y = %s
                WHERE id_mesa = %s
            """, (x, y, id_mesa))
            
            if cursor.rowcount == 0:
                return {'success': False, 'message': 'Mesa no encontrada'}
            
            return {'success': True, 'message': 'Posición actualizada'}
    except Exception as e:
        print(f"[DB] Error: {e}")
        return {'success': False, 'message': str(e)}

def eliminar_mesa(id_mesa: str) -> Dict[str, Any]:
    """Elimina (desactiva) una mesa."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                UPDATE mesas SET activa = false
                WHERE id_mesa = %s
            """, (id_mesa,))
            
            if cursor.rowcount == 0:
                return {'success': False, 'message': 'Mesa no encontrada'}
            
            return {'success': True, 'message': 'Mesa eliminada'}
    except Exception as e:
        print(f"[DB] Error: {e}")
        return {'success': False, 'message': str(e)}

# ==============================================
# RESERVAS
# ==============================================

def _generar_id_reserva() -> str:
    """Genera un ID único para la reserva."""
    import random
    return f"RESTA{random.randint(100, 999)}{random.randint(100, 999)}"

def crear_reserva(id_mesa: str, nombre: str, fecha: str, hora: str, 
                  invitados: int, telefono: str = '', notas: str = '') -> Dict[str, Any]:
    """
    Crea una nueva reserva, verificando primero que la mesa esté disponible
    para ese turno y fecha.
    """
    try:
        # Determinar turno según la hora
        turno = _determinar_turno(hora)
        if turno == 'mediodia':
            hora_inicio = '00:00:00'
            hora_fin = HORA_CORTE_TURNO
        else:
            hora_inicio = HORA_CORTE_TURNO
            hora_fin = '23:59:59'
        
        with get_db_cursor() as cursor:
            # Verificar si la mesa ya tiene reserva para ese turno y fecha
            cursor.execute("""
                SELECT id_reserva, nombre, hora 
                FROM reservas 
                WHERE id_mesa = %s 
                  AND fecha = %s 
                  AND hora >= %s::time 
                  AND hora < %s::time
                  AND estado IN ('Reservado', 'Ocupado')
            """, (id_mesa, fecha, hora_inicio, hora_fin))
            
            existing = cursor.fetchone()
            if existing:
                turno_nombre = 'Mediodía' if turno == 'mediodia' else 'Noche'
                return {
                    'success': False, 
                    'message': f"Mesa ya reservada para {turno_nombre} ({existing['hora'].strftime('%H:%M')}) por {existing['nombre']}"
                }
            
            # Crear la reserva
            id_reserva = _generar_id_reserva()
            
            cursor.execute("""
                INSERT INTO reservas (id_reserva, id_mesa, nombre, fecha, hora, invitados, telefono, notas, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Reservado')
                RETURNING id, id_reserva
            """, (id_reserva, id_mesa, nombre, fecha, hora, invitados, telefono, notas))
            
            return {
                'success': True,
                'message': 'Reserva creada',
                'id_reserva': id_reserva
            }
    except Exception as e:
        print(f"[DB] Error creando reserva: {e}")
        return {'success': False, 'message': str(e)}

def ocupar_mesa_sin_reserva(id_mesa: str, fecha: str = None, turno: str = None) -> Dict[str, Any]:
    """
    Ocupa una mesa sin reserva previa (walk-in).
    Crea un registro completo en la tabla de reservas con datos identificables.
    
    Args:
        id_mesa: ID de la mesa
        fecha: Fecha de ocupación (YYYY-MM-DD). Si None, usa hoy.
        turno: 'mediodia' o 'noche'. Si None, determina por hora actual.
    """
    import random
    
    try:
        # Usar fecha proporcionada o hoy
        if fecha is None:
            fecha = date.today().isoformat()
        
        hora_actual = datetime.now().strftime('%H:%M:%S')
        
        # Usar turno proporcionado o determinar por hora
        if turno is None:
            turno = _determinar_turno(hora_actual)
        
        # La hora de la reserva será una hora típica del turno
        if turno == 'mediodia':
            hora_reserva = '13:00:00'
        else:
            hora_reserva = '20:00:00'
        
        # Generar ID: RESYYYYMMDD_XXXX (17 chars para VARCHAR(20))
        random_suffix = random.randint(1000, 9999)
        fecha_str = fecha.replace('-', '')
        id_reserva = f"RES{fecha_str}_{random_suffix}"
        
        with get_db_cursor() as cursor:
            # Obtener capacidad máxima de la mesa
            cursor.execute("SELECT capacidad FROM mesas WHERE id_mesa = %s", (id_mesa,))
            mesa = cursor.fetchone()
            if not mesa:
                return {'success': False, 'message': 'Mesa no encontrada'}
            
            capacidad = mesa['capacidad']
            
            # Verificar si la mesa ya está ocupada para este turno
            if turno == 'mediodia':
                hora_inicio, hora_fin = '00:00:00', HORA_CORTE_TURNO
            else:
                hora_inicio, hora_fin = HORA_CORTE_TURNO, '23:59:59'
            
            cursor.execute("""
                SELECT id_reserva FROM reservas 
                WHERE id_mesa = %s AND fecha = %s 
                  AND hora >= %s::time AND hora < %s::time
                  AND estado IN ('Reservado', 'Ocupado')
            """, (id_mesa, fecha, hora_inicio, hora_fin))
            
            if cursor.fetchone():
                return {'success': False, 'message': 'Mesa ya ocupada para este turno'}
            
            # Crear el registro de reserva manual
            cursor.execute("""
                INSERT INTO reservas (
                    id_reserva, fecha, hora, id_mesa, nombre, 
                    telefono, invitados, estado, notas, id_llamada
                ) VALUES (
                    %s, %s, %s, %s, 'RESERVA MANUAL',
                    '000000000', %s, 'Ocupado', 'Mesa ocupada sin reserva previa', NULL
                )
            """, (id_reserva, fecha, hora_reserva, id_mesa, capacidad))
            
            return {
                'success': True, 
                'message': 'Mesa ocupada',
                'id_reserva': id_reserva
            }
    except Exception as e:
        print(f"[DB] Error: {e}")
        return {'success': False, 'message': str(e)}

def marcar_mesa_ocupada(id_mesa: str, fecha: str) -> Dict[str, Any]:
    """Marca una reserva como ocupada (el cliente llegó)."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                UPDATE reservas SET estado = 'Ocupado'
                WHERE id_mesa = %s AND fecha = %s AND estado = 'Reservado'
            """, (id_mesa, fecha))
            
            if cursor.rowcount == 0:
                return {'success': False, 'message': 'Reserva no encontrada'}
            
            return {'success': True, 'message': 'Mesa marcada como ocupada'}
    except Exception as e:
        print(f"[DB] Error: {e}")
        return {'success': False, 'message': str(e)}

def liberar_mesa(id_mesa: str, fecha: str = None) -> Dict[str, Any]:
    """Libera una mesa (cancela reserva o desocupa)."""
    if fecha is None:
        fecha = date.today().isoformat()
        
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                UPDATE reservas SET estado = 'Cancelado'
                WHERE id_mesa = %s AND fecha = %s AND estado IN ('Reservado', 'Ocupado')
            """, (id_mesa, fecha))
            
            return {'success': True, 'message': 'Mesa liberada'}
    except Exception as e:
        print(f"[DB] Error: {e}")
        return {'success': False, 'message': str(e)}

# ==============================================
# DISPONIBILIDAD POR TURNOS
# ==============================================

def _determinar_turno(hora: str) -> str:
    """Determina si una hora corresponde al turno de Comida o Cena."""
    hora_time = datetime.strptime(hora, '%H:%M:%S').time() if isinstance(hora, str) else hora
    corte = datetime.strptime(HORA_CORTE_TURNO, '%H:%M:%S').time()
    
    return 'comida' if hora_time < corte else 'cena'

def obtener_disponibilidad(fecha: str, hora: str, invitados: int, 
                            id_llamada: str = None) -> List[Dict[str, Any]]:
    """
    Obtiene las mesas disponibles para una fecha, hora y número de invitados.
    Usa la lógica de turnos (comida/cena) para determinar disponibilidad.
    
    Args:
        fecha: Fecha de la reserva (YYYY-MM-DD)
        hora: Hora de la reserva (HH:MM:SS)
        invitados: Número de invitados
        id_llamada: ID de llamada para bloqueos temporales (opcional)
    
    Returns:
        Lista de mesas disponibles
    """
    turno = _determinar_turno(hora)
    hora_corte = HORA_CORTE_TURNO
    
    try:
        with get_db_cursor() as cursor:
            # Query para obtener mesas disponibles
            # Una mesa está disponible si:
            # 1. Tiene capacidad suficiente
            # 2. No tiene reserva en el mismo turno
            # 3. O el bloqueo temporal es del mismo id_llamada
            
            if turno == 'comida':
                hora_inicio = HORA_INICIO_COMIDA
                hora_fin = hora_corte
            else:
                hora_inicio = hora_corte
                hora_fin = '23:59:59'
            
            cursor.execute("""
                SELECT m.id_mesa, m.capacidad, m.tipo, m.pos_x, m.pos_y
                FROM mesas m
                WHERE m.activa = true
                  AND m.capacidad >= %s
                  AND m.id_mesa NOT IN (
                      SELECT r.id_mesa 
                      FROM reservas r
                      WHERE r.fecha = %s
                        AND r.hora >= %s::time
                        AND r.hora < %s::time
                        AND r.estado IN ('Reservado', 'Ocupado', 'Bloqueado')
                        AND (r.id_llamada IS NULL OR r.id_llamada != %s)
                  )
                ORDER BY m.capacidad ASC, m.id_mesa
            """, (invitados, fecha, hora_inicio, hora_fin, id_llamada or ''))
            
            mesas = cursor.fetchall()
            
            return [{
                'id': m['id_mesa'],
                'name': f"Mesa {m['id_mesa'][1:]}",
                'capacity': m['capacidad'],
                'zone': m['tipo']
            } for m in mesas]
    except Exception as e:
        print(f"[DB] Error obteniendo disponibilidad: {e}")
        return []

def crear_bloqueo_temporal(id_mesa: str, fecha: str, hora: str, id_llamada: str) -> Dict[str, Any]:
    """
    Crea un bloqueo temporal en una mesa (para llamadas/n8n).
    El bloqueo debe liberarse manualmente o expira según lógica de negocio.
    """
    try:
        with get_db_cursor() as cursor:
            id_reserva = f"BLOCK{id_llamada[:6]}"
            
            cursor.execute("""
                INSERT INTO reservas (id_reserva, id_mesa, nombre, fecha, hora, invitados, estado, id_llamada)
                VALUES (%s, %s, 'Bloqueo Temporal', %s, %s, 0, 'Bloqueado', %s)
            """, (id_reserva, id_mesa, fecha, hora, id_llamada))
            
            return {'success': True, 'message': 'Mesa bloqueada'}
    except Exception as e:
        print(f"[DB] Error: {e}")
        return {'success': False, 'message': str(e)}

def eliminar_bloqueo_temporal(id_llamada: str) -> Dict[str, Any]:
    """Elimina un bloqueo temporal por id_llamada."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                DELETE FROM reservas 
                WHERE id_llamada = %s AND estado = 'Bloqueado'
            """, (id_llamada,))
            
            return {'success': True, 'message': 'Bloqueo eliminado'}
    except Exception as e:
        print(f"[DB] Error: {e}")
        return {'success': False, 'message': str(e)}
