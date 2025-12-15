let currentZone = 'interior'; // Variable global necesaria

// Inicialización al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    console.log('Iniciando aplicación (main.js)...');
    loadTables();
});

// Función para cambiar de zona (conectada a los botones del header)
function switchZone(zone) {
    currentZone = zone;
    
    // Actualizar botones visualmente
    const btnInterior = document.getElementById('btn-interior');
    const btnTerraza = document.getElementById('btn-terraza');
    
    if (zone === 'interior') {
        btnInterior.className = "px-4 py-2 rounded-lg text-sm font-medium transition-colors bg-slate-800 text-white";
        btnTerraza.className = "px-4 py-2 rounded-lg text-sm font-medium transition-colors bg-slate-200 text-slate-600 hover:bg-slate-300";
    } else {
        btnInterior.className = "px-4 py-2 rounded-lg text-sm font-medium transition-colors bg-slate-200 text-slate-600 hover:bg-slate-300";
        btnTerraza.className = "px-4 py-2 rounded-lg text-sm font-medium transition-colors bg-slate-800 text-white";
    }
    
    loadTables();
}

// Cargar datos del servidor
async function loadTables() {
    try {
        const endpoint = '/api/tables';
        console.log('[loadTables] Solicitando mesas a:', endpoint);

        const response = await fetch(endpoint);
        console.log('[loadTables] Status respuesta:', response.status);

        if (!response.ok) {
            const text = await response.text().catch(() => '');
            console.error('[loadTables] Respuesta no OK. Body:', text);
            throw new Error(`Error al cargar mesas. Status: ${response.status}`);
        }

        const raw = await response.json();
        console.log('[loadTables] JSON recibido bruto:', raw);

        // Adaptar: puede venir como array directo o como { tables: [...] }
        let tables = [];
        if (Array.isArray(raw)) {
            tables = raw;
        } else if (raw && Array.isArray(raw.tables)) {
            tables = raw.tables;
        } else {
            console.error('[loadTables] Formato inesperado. Esperado: [] o { tables: [] }');
            return;
        }

        console.log('[loadTables] Mesas normalizadas:', tables);
        renderTables(tables);
    } catch (error) {
        console.error('[loadTables] Error cargando mesas:', error);
    }
}

// Función auxiliar para generar HTML de sillas
function getChairsHTML(capacity) {
    let chairs = '';
    if (capacity >= 1) chairs += '<div class="chair chair-top"></div>';
    if (capacity >= 2) chairs += '<div class="chair chair-bottom"></div>';
    if (capacity >= 3) chairs += '<div class="chair chair-left"></div>';
    if (capacity >= 4) chairs += '<div class="chair chair-right"></div>';
    
    if (capacity >= 6) {
        chairs = ''; 
        chairs += '<div class="chair chair-top-left"></div>';
        chairs += '<div class="chair chair-top-right"></div>';
        chairs += '<div class="chair chair-bottom-left"></div>';
        chairs += '<div class="chair chair-bottom-right"></div>';
        chairs += '<div class="chair chair-left"></div>';
        chairs += '<div class="chair chair-right"></div>';
    }
    return chairs;
}

// Renderizado principal
function renderTables(tables) {
    const container = document.getElementById('floor-plan');
    if (!container) {
        console.error('[renderTables] No se encontró el contenedor #floor-plan');
        return;
    }
    
    console.log('[renderTables] Número de mesas totales recibidas:', tables.length);
    container.innerHTML = '';

    let renderedCount = 0;

    tables.forEach(table => {
        // Log mínimo de cada mesa para ver su estructura
        if (!table._loggedOnce) {
            console.log('[renderTables] Mesa recibida:', table);
            table._loggedOnce = true;
        }

        if (!table.zone || table.zone !== currentZone) return;

        const el = document.createElement('div');
        // Clases base
        el.className = `absolute border-2 rounded-lg shadow-md cursor-move transition-colors flex items-center justify-center select-none ${
            table.status === 'reserved' 
            ? 'bg-red-100 border-red-400 text-red-800' 
            : 'bg-green-100 border-green-400 text-green-800'
        }`;
        
        // Estilos dinámicos
        el.style.width = '100px';
        el.style.height = '100px';
        el.style.left = `${table.x}px`;
        el.style.top = `${table.y}px`;
        el.style.transform = `rotate(${table.rotation || 0}deg)`;
        
        // Atributos útiles para drag_drop.js
        el.id = `table-${table.id}`;
        el.draggable = true;
        el.dataset.id = table.id;
        el.dataset.x = table.x;
        el.dataset.y = table.y;
        el.dataset.zone = table.zone;

        // Contenido interno (contrarrestar rotación)
        const innerContentRotation = -(table.rotation || 0);
        const iconClass = table.status === 'reserved' ? 'fa-user-lock' : 'fa-chair';
        
        el.innerHTML = `
            ${getChairsHTML(table.capacity || 2)}
            <div style="transform: rotate(${innerContentRotation}deg);" class="text-center pointer-events-none">
                <i class="fa-solid ${iconClass} text-xl mb-1"></i>
                <div class="font-bold text-sm">${table.name}</div>
                <div class="text-xs opacity-75">${table.capacity || 2} pers.</div>
            </div>
        `;

        // --- Integración con drag_drop.js ---
        // Drag & Drop
        if (typeof handleDragStart === 'function') {
            el.addEventListener('dragstart', handleDragStart);
        }
        if (typeof handleDragEnd === 'function') {
            el.addEventListener('dragend', (ev) => {
                handleDragEnd(ev);
                // Si drag_drop.js actualiza left/top del elemento, reflejamos en el backend
                const rect = el.getBoundingClientRect();
                // Coordenadas relativas al contenedor
                const containerRect = container.getBoundingClientRect();
                const newX = rect.left - containerRect.left;
                const newY = rect.top - containerRect.top;
                updateTablePosition(table.id, newX, newY);
            });
        }

        // Click vs drag para abrir modal
        let isDragging = false;
        el.addEventListener('mousedown', () => isDragging = false);
        el.addEventListener('mousemove', () => isDragging = true);
        el.addEventListener('mouseup', () => {
            if (!isDragging) openBookingModal(table);
        });

        renderedCount++;
        container.appendChild(el);
    });

    console.log(`[renderTables] Mesas renderizadas para zona "${currentZone}":`, renderedCount);
}

// --- NUEVO: avisar al backend cuando cambia la posición de una mesa ---
async function updateTablePosition(tableId, x, y) {
    try {
        const payload = { table_id: tableId, x, y };
        console.log('[updateTablePosition] Enviando nueva posición:', payload);

        const response = await fetch('/api/update_position', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            console.warn('[updateTablePosition] Error al guardar posición. Status:', response.status);
        }
    } catch (err) {
        console.error('[updateTablePosition] Error de red:', err);
    }
}

async function sendUpdate(payload) {
    try {
        const response = await fetch('/api/update_booking', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const text = await response.text();
            console.error('[sendUpdate] Error en la respuesta del servidor:', text);
            throw new Error(`Error al actualizar reserva. Status: ${response.status}`);
        }

        const result = await response.json();
        console.log('[sendUpdate] Resultado de la actualización:', result);

        // Actualizar la interfaz o dar feedback al usuario si es necesario
        alert('Reserva actualizada con éxito');
    } catch (error) {
        console.error('[sendUpdate] Error al enviar actualización:', error);
        alert('Error al actualizar la reserva. Intente nuevamente más tarde.');
    }
}

// --- Lógica del Modal ---

function openBookingModal(table) {
    const modal = document.getElementById('modal');
    const content = document.getElementById('modal-content');
    modal.classList.remove('hidden');
    modal.classList.add('flex');

    if (!table || !table.id) {
        console.error('[openBookingModal] Mesa inválida:', table);
        return;
    }

    // Limpiar contenido previo
    content.innerHTML = '';

    // Títulos
    const title = document.createElement('h2');
    title.className = 'text-lg font-bold mb-4';
    title.innerText = `Mesa ${table.name} - Detalles`;
    content.appendChild(title);

    // Información básica
    const info = document.createElement('div');
    info.className = 'grid grid-cols-2 gap-4 mb-4';
    info.innerHTML = `
        <div><strong>ID:</strong> ${table.id}</div>
        <div><strong>Zona:</strong> ${table.zone}</div>
        <div><strong>Capacidad:</strong> ${table.capacity || 2} personas</div>
        <div><strong>Estado:</strong> ${table.status === 'reserved' ? 'Reservada' : 'Disponible'}</div>
    `;
    content.appendChild(info);

    // --- NUEVO: Mostrar y editar reserva ---
    if (table.status === 'reserved') {
        // Mostrar detalles de la reserva
        const reservationDetails = document.createElement('div');
        reservationDetails.className = 'mb-4';
        reservationDetails.innerHTML = `
            <div class="font-semibold">Detalles de la Reserva:</div>
            <div><strong>Cliente:</strong> ${table.reservation.customer_name || 'N/A'}</div>
            <div><strong>Teléfono:</strong> ${table.reservation.customer_phone || 'N/A'}</div>
            <div><strong>Fecha y Hora:</strong> ${new Date(table.reservation.datetime).toLocaleString() || 'N/A'}</div>
        `;
        content.appendChild(reservationDetails);

        // Botón para editar reserva
        const btnEdit = document.createElement('button');
        btnEdit.className = 'mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700 transition-colors';
        btnEdit.innerText = 'Editar Reserva';
        btnEdit.onclick = () => openEditReservationModal(table.reservation);
        content.appendChild(btnEdit);
    } else {
        // Mensaje de mesa disponible
        const availableMsg = document.createElement('div');
        availableMsg.className = 'text-center text-gray-500 py-4';
        availableMsg.innerText = 'Esta mesa está disponible para reserva';
        content.appendChild(availableMsg);
    }

    // Cerrar modal
    const closeButton = document.createElement('button');
    closeButton.className = 'absolute top-2 right-2 text-gray-500 hover:text-gray-700';
    closeButton.innerHTML = '&times;';
    closeButton.onclick = () => {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    };
    modal.appendChild(closeButton);
}

// --- NUEVO: Lógica del Modal de Edición de Reserva ---
function openEditReservationModal(reservation) {
    const modal = document.getElementById('modal');
    const content = document.getElementById('modal-content');
    modal.classList.remove('hidden');
    modal.classList.add('flex');

    // Limpiar contenido previo
    content.innerHTML = '';

    // Títulos
    const title = document.createElement('h2');
    title.className = 'text-lg font-bold mb-4';
    title.innerText = `Editar Reserva - Mesa ${reservation.table_name}`;
    content.appendChild(title);

    // Formulario de edición
    const form = document.createElement('form');
    form.className = 'grid grid-cols-1 gap-4';

    // Nombre del cliente
    const customerNameField = document.createElement('div');
    customerNameField.className = 'flex flex-col';
    customerNameField.innerHTML = `
        <label class="font-semibold" for="customer-name">Nombre del Cliente</label>
        <input class="p-2 border rounded-lg" type="text" id="customer-name" value="${reservation.customer_name}" required>
    `;
    form.appendChild(customerNameField);

    // Teléfono del cliente
    const customerPhoneField = document.createElement('div');
    customerPhoneField.className = 'flex flex-col';
    customerPhoneField.innerHTML = `
        <label class="font-semibold" for="customer-phone">Teléfono del Cliente</label>
        <input class="p-2 border rounded-lg" type="tel" id="customer-phone" value="${reservation.customer_phone}" required>
    `;
    form.appendChild(customerPhoneField);

    // Fecha y hora
    const datetimeField = document.createElement('div');
    datetimeField.className = 'flex flex-col';
    datetimeField.innerHTML = `
        <label class="font-semibold" for="reservation-datetime">Fecha y Hora</label>
        <input class="p-2 border rounded-lg" type="datetime-local" id="reservation-datetime" value="${new Date(reservation.datetime).toISOString().slice(0, 16)}" required>
    `;
    form.appendChild(datetimeField);

    // Botón de guardar cambios
    const btnSave = document.createElement('button');
    btnSave.className = 'mt-4 px-4 py-2 bg-green-600 text-white rounded-lg shadow-md hover:bg-green-700 transition-colors';
    btnSave.innerText = 'Guardar Cambios';
    btnSave.type = 'submit';
    form.appendChild(btnSave);

    // Manejo del envío del formulario
    form.onsubmit = async (e) => {
        e.preventDefault();

        const updatedReservation = {
            id: reservation.id,
            table_id: reservation.table_id,
            customer_name: document.getElementById('customer-name').value,
            customer_phone: document.getElementById('customer-phone').value,
            datetime: new Date(document.getElementById('reservation-datetime').value).toISOString(),
        };

        console.log('[openEditReservationModal] Reserva a actualizar:', updatedReservation);

        // Enviar actualización a servidor
        await sendUpdate(updatedReservation);

        // Cerrar modal después de un breve retraso
        setTimeout(() => {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }, 500);
    };

    content.appendChild(form);

    // Cerrar modal
    const closeButton = document.createElement('button');
    closeButton.className = 'absolute top-2 right-2 text-gray-500 hover:text-gray-700';
    closeButton.innerHTML = '&times;';
    closeButton.onclick = () => {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    };
    modal.appendChild(closeButton);
}
