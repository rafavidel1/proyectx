/**
 * Módulo de Modales - Gestión completa de popups con cierre correcto.
 */
const ModalManager = {
    
    modal: null,
    modalContent: null,
    
    init() {
        this.modal = document.getElementById('modal');
        this.modalContent = document.getElementById('modal-content');
        
        if (!this.modal || !this.modalContent) {
            console.error('[ModalManager] Elementos del modal no encontrados');
            return;
        }
        
        // Cerrar al hacer clic en el backdrop (fondo oscuro)
        this.modal.addEventListener('click', (e) => {
            // Solo cerrar si el clic es en el backdrop, no en el contenido
            if (e.target === this.modal) {
                this.closeModal();
            }
        });
        
        // Prevenir que clicks dentro del contenido cierren el modal
        const modalInner = this.modal.querySelector('.bg-white');
        if (modalInner) {
            modalInner.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }
    },
    
    openModal(tableData) {
        if (!this.modal || !this.modalContent) return;
        
        this.modal.classList.remove('hidden');
        this.modal.classList.add('flex');
        
        if (tableData.status === 'free') {
            this._renderBookingForm(tableData);
        } else {
            this._renderReservationInfo(tableData);
        }
    },
    
    closeModal() {
        if (!this.modal) return;
        
        this.modal.classList.add('hidden');
        this.modal.classList.remove('flex');
        this.modalContent.innerHTML = '';
    },
    
    _renderBookingForm(table) {
        this.modalContent.innerHTML = `
            <h3 class="text-lg font-semibold text-green-700 mb-3">
                <i class="fa-solid fa-calendar-plus mr-2"></i>Nueva Reserva: ${table.name}
            </h3>
            <form id="booking-form" class="space-y-3">
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">
                        <i class="fa-solid fa-user mr-1"></i>Nombre del Cliente
                    </label>
                    <input type="text" name="customer_name" required 
                           class="w-full rounded-lg border-slate-300 shadow-sm p-2 border focus:border-green-500 focus:ring-1 focus:ring-green-500">
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-sm font-medium text-slate-700 mb-1">
                            <i class="fa-solid fa-clock mr-1"></i>Hora
                        </label>
                        <input type="time" name="time" required 
                               class="w-full rounded-lg border-slate-300 shadow-sm p-2 border focus:border-green-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-slate-700 mb-1">
                            <i class="fa-solid fa-users mr-1"></i>Personas
                        </label>
                        <input type="number" name="people" value="${table.capacity}" 
                               min="1" max="${table.capacity}" required
                               class="w-full rounded-lg border-slate-300 shadow-sm p-2 border focus:border-green-500">
                    </div>
                </div>
                <button type="submit" 
                        class="w-full bg-green-600 text-white py-2.5 rounded-lg hover:bg-green-700 transition font-medium">
                    <i class="fa-solid fa-check mr-2"></i>Confirmar Reserva
                </button>
            </form>
        `;
        
        document.getElementById('booking-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this._handleBookingSubmit(e, table.id);
        });
    },
    
    _renderReservationInfo(table) {
        const info = table.reservation_info || {};
        
        this.modalContent.innerHTML = `
            <h3 class="text-lg font-semibold text-red-700 mb-3">
                <i class="fa-solid fa-user-lock mr-2"></i>Mesa Reservada: ${table.name}
            </h3>
            <div class="bg-slate-50 p-4 rounded-lg mb-4 border border-slate-200 space-y-2">
                <p class="flex items-center">
                    <i class="fa-solid fa-user w-6 text-slate-600"></i>
                    <strong class="mr-2">Cliente:</strong> ${info.customer_name || 'N/A'}
                </p>
                <p class="flex items-center">
                    <i class="fa-solid fa-clock w-6 text-slate-600"></i>
                    <strong class="mr-2">Hora:</strong> ${info.time || 'N/A'}
                </p>
                <p class="flex items-center">
                    <i class="fa-solid fa-users w-6 text-slate-600"></i>
                    <strong class="mr-2">Personas:</strong> ${info.people || 'N/A'}
                </p>
            </div>
            <button onclick="ModalManager.cancelReservation('${table.id}')" 
                    class="w-full bg-red-500 text-white py-2.5 rounded-lg hover:bg-red-600 transition font-medium">
                <i class="fa-solid fa-trash mr-2"></i>Cancelar Reserva
            </button>
        `;
    },
    
    async _handleBookingSubmit(event, tableId) {
        const formData = new FormData(event.target);
        
        const data = {
            customer_name: formData.get('customer_name'),
            time: formData.get('time'),
            people: parseInt(formData.get('people'))
        };
        
        try {
            const result = await API.createReservation(tableId, data);
            
            if (result.success) {
                this.closeModal();
                window.App.loadAndRender(); // Recargar mesas
            } else {
                alert(result.message || 'Error al crear la reserva');
            }
        } catch (error) {
            alert('Error de conexión');
        }
    },
    
    async cancelReservation(tableId) {
        if (!confirm('¿Seguro que deseas cancelar esta reserva?')) return;
        
        try {
            const result = await API.cancelReservation(tableId);
            
            if (result.success) {
                this.closeModal();
                window.App.loadAndRender(); // Recargar mesas
            } else {
                alert(result.message || 'Error al cancelar');
            }
        } catch (error) {
            alert('Error de conexión');
        }
    }
};
