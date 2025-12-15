/**
 * Módulo de API - Centraliza todas las peticiones al backend.
 */
const API = {
    
    async getTables() {
        try {
            const response = await fetch('/api/tables');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            console.log('[API] Respuesta bruta del servidor:', data);
            
            // Normalizar respuesta: puede venir como array directo o como { tables: [...] }
            if (Array.isArray(data)) {
                return data;
            } else if (data && Array.isArray(data.tables)) {
                return data.tables;
            } else {
                console.error('[API] Formato inesperado. Esperado: [] o { tables: [] }');
                return [];
            }
        } catch (error) {
            console.error('[API] Error al cargar mesas:', error);
            return []; // Devolver array vacío en caso de error
        }
    },
    
    async createReservation(tableId, data) {
        try {
            const response = await fetch('/api/update_booking', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    table_id: tableId,
                    action: 'book',
                    ...data
                })
            });
            return await response.json();
        } catch (error) {
            console.error('[API] Error al crear reserva:', error);
            throw error;
        }
    },
    
    async cancelReservation(tableId) {
        try {
            const response = await fetch('/api/update_booking', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    table_id: tableId,
                    action: 'cancel'
                })
            });
            return await response.json();
        } catch (error) {
            console.error('[API] Error al cancelar reserva:', error);
            throw error;
        }
    },
    
    async updatePosition(tableId, x, y) {
        try {
            const response = await fetch('/api/update_position', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ table_id: tableId, x, y })
            });
            return await response.json();
        } catch (error) {
            console.error('[API] Error al actualizar posición:', error);
            throw error;
        }
    }
};
