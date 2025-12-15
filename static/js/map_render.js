/**
 * Módulo de Renderizado - Solo se encarga de pintar el mapa.
 */
const MapRenderer = {

    currentZone: 'interior',
    container: null,

    init() {
        this.container = document.getElementById('floor-plan');
        if (!this.container) {
            console.error('[MapRenderer] Contenedor #floor-plan no encontrado');
        }
    },

    renderTables(tables) {
        if (!this.container) return;

        // Validación defensiva
        if (!Array.isArray(tables)) {
            console.error('[MapRenderer] Error: tables no es un array', tables);
            return;
        }

        this.container.innerHTML = '';
        const filteredTables = tables.filter(t => t.zone === this.currentZone);

        console.log(`[MapRenderer] Renderizando ${filteredTables.length} mesas para zona "${this.currentZone}"`);

        filteredTables.forEach(table => {
            const element = this._createTableElement(table);
            this.container.appendChild(element);
        });
    },

    _createTableElement(table) {
        const el = document.createElement('div');

        // Colores según estado
        let statusClasses;
        switch (table.status) {
            case 'reserved':
                statusClasses = 'bg-red-100 border-red-400 text-red-800';
                break;
            case 'occupied':
                statusClasses = 'bg-amber-100 border-amber-400 text-amber-800';
                break;
            default: // 'free'
                statusClasses = 'bg-green-100 border-green-400 text-green-800';
        }

        el.className = `absolute border-2 rounded-lg shadow-md cursor-pointer transition-all 
                        flex items-center justify-center select-none ${statusClasses}
                        hover:shadow-lg hover:scale-105 hover:z-20`;

        el.style.cssText = `
            width: 100px;
            height: 100px;
            left: ${table.x}px;
            top: ${table.y}px;
            transform: rotate(${table.rotation || 0}deg);
        `;

        el.id = `table-${table.id}`;
        el.draggable = true;
        el.dataset.id = table.id;
        el.dataset.x = table.x;
        el.dataset.y = table.y;

        // Tooltip con información de reserva
        if (table.status === 'reserved' && table.reservation_info) {
            const info = table.reservation_info;
            el.title = `🧑 ${info.customer_name || 'Cliente'}\n⏰ ${info.time || 'N/A'}\n👥 ${info.people || '?'} personas`;
        } else if (table.status === 'free') {
            el.title = `${table.name} - Disponible\nCapacidad: ${table.capacity || 2} personas`;
        } else {
            el.title = `${table.name} - ${table.status}`;
        }

        const innerRotation = -(table.rotation || 0);
        const icon = table.status === 'reserved' ? 'fa-user-lock' :
            table.status === 'occupied' ? 'fa-utensils' : 'fa-chair';

        el.innerHTML = `
            ${this._generateChairsHTML(table.capacity || 2)}
            <div style="transform: rotate(${innerRotation}deg);" class="text-center pointer-events-none z-10">
                <i class="fa-solid ${icon} text-xl mb-1"></i>
                <div class="font-bold text-sm">${table.name}</div>
                <div class="text-xs opacity-75">${table.capacity || 2} pers.</div>
            </div>
        `;

        return el;
    },

    _generateChairsHTML(capacity) {
        let chairs = '';

        if (capacity < 6) {
            if (capacity >= 1) chairs += '<div class="chair chair-top"></div>';
            if (capacity >= 2) chairs += '<div class="chair chair-bottom"></div>';
            if (capacity >= 3) chairs += '<div class="chair chair-left"></div>';
            if (capacity >= 4) chairs += '<div class="chair chair-right"></div>';
        } else {
            chairs = `
                <div class="chair chair-top-left"></div>
                <div class="chair chair-top-right"></div>
                <div class="chair chair-bottom-left"></div>
                <div class="chair chair-bottom-right"></div>
                <div class="chair chair-left"></div>
                <div class="chair chair-right"></div>
            `;
        }

        return chairs;
    },

    setZone(zone) {
        this.currentZone = zone;
    }
};
