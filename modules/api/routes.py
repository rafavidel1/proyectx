"""
API Routes - Definición de endpoints HTTP.
"""
from flask import Blueprint, jsonify, request, session
from modules.api.api_functions import (
    # Auth
    login, get_user,
    # Tables
    get_tables, create_table, update_table, update_table_position, delete_table,
    # Reservations
    reserve_table, occupy_table, mark_as_occupied, free_table,
    # Availability
    check_availability, create_temporary_block, remove_temporary_block
)

api_bp = Blueprint('api', __name__, url_prefix='/api')

# ==============================================
# AUTENTICACIÓN
# ==============================================

@api_bp.post('/login')
def api_login():
    """POST /api/login - Iniciar sesión"""
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Usuario y contraseña requeridos'}), 400
    
    result = login(username, password)
    
    if result.get('success'):
        session['user_id'] = result['user']['id']
        session['user_role'] = result['user']['role']  # FIXED: was 'rol'
    
    status = 200 if result.get('success') else 401
    return jsonify(result), status

@api_bp.post('/logout')
def api_logout():
    """POST /api/logout - Cerrar sesión"""
    session.clear()
    return jsonify({'success': True, 'message': 'Sesión cerrada'})

@api_bp.get('/session')
def api_session():
    """GET /api/session - Verificar sesión activa"""
    user_id = session.get('user_id')
    if user_id:
        result = get_user(user_id)
        if result.get('success'):
            return jsonify(result)
    return jsonify({'success': False, 'message': 'No hay sesión activa'}), 401

# ==============================================
# MESAS
# ==============================================

@api_bp.get('/tables')
def api_get_tables():
    """GET /api/tables - Obtener mesas con estado por fecha y turno"""
    fecha = request.args.get('fecha')   # Optional: YYYY-MM-DD
    turno = request.args.get('turno')   # Optional: 'mediodia' o 'noche'
    tables = get_tables(fecha, turno)
    return jsonify(tables)

@api_bp.post('/tables')
def api_create_table():
    """POST /api/tables - Crear nueva mesa"""
    data = request.get_json(silent=True) or {}
    capacidad = int(data.get('capacity', 4))
    zona = data.get('zone', 'interior')
    
    result = create_table(capacidad, zona)
    status = 200 if result.get('success') else 400
    return jsonify(result), status

@api_bp.put('/tables/<table_id>')
def api_update_table(table_id):
    """PUT /api/tables/:id - Actualizar mesa"""
    data = request.get_json(silent=True) or {}
    result = update_table(table_id, data)
    status = 200 if result.get('success') else 400
    return jsonify(result), status

@api_bp.delete('/tables/<table_id>')
def api_delete_table(table_id):
    """DELETE /api/tables/:id - Eliminar mesa"""
    result = delete_table(table_id)
    status = 200 if result.get('success') else 400
    return jsonify(result), status

@api_bp.post('/tables/<table_id>/position')
def api_update_position(table_id):
    """POST /api/tables/:id/position - Actualizar posición"""
    data = request.get_json(silent=True) or {}
    x = data.get('x')
    y = data.get('y')
    
    if x is None or y is None:
        return jsonify({'success': False, 'message': 'x e y requeridos'}), 400
    
    result = update_table_position(table_id, float(x), float(y))
    status = 200 if result.get('success') else 400
    return jsonify(result), status

# ==============================================
# RESERVAS
# ==============================================

@api_bp.post('/tables/<table_id>/reserve')
def api_reserve_table(table_id):
    """POST /api/tables/:id/reserve - Crear reserva completa"""
    data = request.get_json(silent=True) or {}
    
    customer_name = data.get('customer_name', '').strip()
    time = data.get('time', '').strip()
    people = int(data.get('people', 2))
    fecha = data.get('fecha')
    telefono = data.get('telefono', '').strip()
    notas = data.get('notas', '').strip()
    
    if not customer_name or not time:
        return jsonify({'success': False, 'message': 'Nombre y hora requeridos'}), 400
    
    result = reserve_table(table_id, customer_name, time, people, fecha, telefono, notas)
    status = 200 if result.get('success') else 400
    return jsonify(result), status

@api_bp.post('/tables/<table_id>/occupy')
def api_occupy_table(table_id):
    """POST /api/tables/:id/occupy - Ocupar mesa (walk-in)"""
    data = request.get_json(silent=True) or {}
    fecha = data.get('fecha')
    turno = data.get('turno')
    result = occupy_table(table_id, fecha, turno)
    status = 200 if result.get('success') else 400
    return jsonify(result), status

@api_bp.post('/tables/<table_id>/arrived')
def api_mark_arrived(table_id):
    """POST /api/tables/:id/arrived - Marcar llegada del cliente"""
    data = request.get_json(silent=True) or {}
    fecha = data.get('fecha')
    result = mark_as_occupied(table_id, fecha)
    status = 200 if result.get('success') else 400
    return jsonify(result), status

@api_bp.post('/tables/<table_id>/free')
def api_free_table(table_id):
    """POST /api/tables/:id/free - Liberar mesa"""
    data = request.get_json(silent=True) or {}
    fecha = data.get('fecha')
    result = free_table(table_id, fecha)
    status = 200 if result.get('success') else 400
    return jsonify(result), status

# ==============================================
# DISPONIBILIDAD
# ==============================================

@api_bp.get('/availability')
def api_check_availability():
    """GET /api/availability - Consultar mesas disponibles"""
    fecha = request.args.get('fecha')
    hora = request.args.get('hora')
    invitados = request.args.get('invitados', 2, type=int)
    id_llamada = request.args.get('id_llamada')
    
    if not fecha or not hora:
        return jsonify({'success': False, 'message': 'fecha y hora requeridos'}), 400
    
    mesas = check_availability(fecha, hora, invitados, id_llamada)
    return jsonify({'success': True, 'tables': mesas})

@api_bp.post('/block')
def api_create_block():
    """POST /api/block - Crear bloqueo temporal"""
    data = request.get_json(silent=True) or {}
    
    id_mesa = data.get('id_mesa')
    fecha = data.get('fecha')
    hora = data.get('hora')
    id_llamada = data.get('id_llamada')
    
    if not all([id_mesa, fecha, hora, id_llamada]):
        return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400
    
    result = create_temporary_block(id_mesa, fecha, hora, id_llamada)
    status = 200 if result.get('success') else 400
    return jsonify(result), status

@api_bp.delete('/block/<id_llamada>')
def api_remove_block(id_llamada):
    """DELETE /api/block/:id_llamada - Eliminar bloqueo"""
    result = remove_temporary_block(id_llamada)
    status = 200 if result.get('success') else 400
    return jsonify(result), status

# ==============================================
# LEGACY ENDPOINTS (Compatibilidad)
# ==============================================

@api_bp.post('/update_position')
def api_update_position_legacy():
    """POST /api/update_position (legacy)"""
    data = request.get_json(silent=True) or {}
    table_id = data.get('table_id')
    x = data.get('x')
    y = data.get('y')
    
    if not table_id or x is None or y is None:
        return jsonify({'success': False, 'message': 'Campos requeridos: table_id, x, y'}), 400
    
    result = update_table_position(table_id, float(x), float(y))
    status = 200 if result.get('success') else 400
    return jsonify(result), status

@api_bp.post('/update_booking')
def api_update_booking_legacy():
    """POST /api/update_booking (legacy)"""
    data = request.get_json(silent=True) or {}
    table_id = data.get('table_id')
    action = data.get('action')
    
    if not table_id or not action:
        return jsonify({'success': False, 'message': 'Campos requeridos: table_id, action'}), 400
    
    if action == 'book':
        result = reserve_table(
            id_mesa=table_id,
            customer_name=data.get('customer_name', ''),
            time=data.get('time', ''),
            people=int(data.get('people', 0))
        )
    elif action == 'cancel':
        result = free_table(table_id)
    elif action == 'occupy':
        result = occupy_table(table_id)
    else:
        result = {'success': False, 'message': 'Acción no válida'}
    
    status = 200 if result.get('success') else 400
    return jsonify(result), status
