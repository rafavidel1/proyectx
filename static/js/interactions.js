/**
 * Módulo de Interacciones - Drag & Drop (mouse + touch) y eventos de clic.
 */
const Interactions = {

    draggedElement: null,
    offsetX: 0,
    offsetY: 0,
    isDragging: false,
    editMode: false, // Modo edición desactivado por defecto

    init() {
        const container = document.getElementById('floor-plan');
        if (container) {
            container.addEventListener('dragover', (e) => e.preventDefault());

            // Touch events para móvil
            container.addEventListener('touchmove', (e) => this._handleTouchMove(e), { passive: false });
            container.addEventListener('touchend', (e) => this._handleTouchEnd(e));
        }
    },

    setEditMode(enabled) {
        this.editMode = enabled;
        console.log('[Interactions] Modo edición:', enabled ? 'ON' : 'OFF');
    },

    toggleEditMode(enabled) {
        this.setEditMode(enabled);
    },

    attachToTable(element, tableData) {
        // Solo permitir drag si el modo edición está activo
        element.draggable = this.editMode;
        element.style.cursor = this.editMode ? 'move' : 'pointer';

        // Mouse events
        if (this.editMode) {
            element.addEventListener('dragstart', (e) => this._handleDragStart(e));
            element.addEventListener('dragend', (e) => this._handleDragEnd(e, tableData));
        }

        // Touch events para móvil
        element.addEventListener('touchstart', (e) => this._handleTouchStart(e, element, tableData));

        // Click detection
        let clickStartTime = 0;

        element.addEventListener('mousedown', () => {
            this.isDragging = false;
            clickStartTime = Date.now();
        });

        element.addEventListener('mousemove', () => {
            if (Date.now() - clickStartTime > 100) {
                this.isDragging = true;
            }
        });

        element.addEventListener('mouseup', () => {
            if (!this.isDragging && Date.now() - clickStartTime < 200) {
                window.ModalManager.openModal(tableData);
            }
        });
    },

    // --- MOUSE EVENTS ---

    _handleDragStart(event) {
        if (!this.editMode) {
            event.preventDefault();
            return;
        }

        this.draggedElement = event.target;

        const rect = this.draggedElement.getBoundingClientRect();
        this.offsetX = event.clientX - rect.left;
        this.offsetY = event.clientY - rect.top;

        this.draggedElement.style.opacity = '0.5';
    },

    async _handleDragEnd(event, tableData) {
        if (!this.draggedElement || !this.editMode) return;

        this.draggedElement.style.opacity = '1';

        const container = document.getElementById('floor-plan');
        const containerRect = container.getBoundingClientRect();

        let newX = event.clientX - containerRect.left - this.offsetX;
        let newY = event.clientY - containerRect.top - this.offsetY;

        newX = Math.max(0, Math.min(newX, containerRect.width - 100));
        newY = Math.max(0, Math.min(newY, containerRect.height - 100));

        this.draggedElement.style.left = `${newX}px`;
        this.draggedElement.style.top = `${newY}px`;

        try {
            const result = await API.updatePosition(tableData.id, newX, newY);
            if (result.success) {
                console.log(`[Interactions] Mesa ${tableData.id} movida a (${newX}, ${newY})`);
            }
        } catch (error) {
            console.error('[Interactions] Error al guardar posición');
        }

        this.draggedElement = null;
    },

    // --- TOUCH EVENTS (MÓVIL) ---

    _handleTouchStart(event, element, tableData) {
        if (!this.editMode) {
            // En modo normal, abrir modal al tap
            const clickTime = Date.now();
            setTimeout(() => {
                if (!this.isDragging) {
                    window.ModalManager.openModal(tableData);
                }
            }, 150);
            return;
        }

        // Modo edición: preparar para arrastrar
        this.draggedElement = element;
        this.isDragging = false;

        const touch = event.touches[0];
        const rect = element.getBoundingClientRect();

        this.offsetX = touch.clientX - rect.left;
        this.offsetY = touch.clientY - rect.top;

        element.style.opacity = '0.7';
    },

    _handleTouchMove(event) {
        if (!this.draggedElement || !this.editMode) return;

        event.preventDefault(); // Evitar scroll
        this.isDragging = true;

        const touch = event.touches[0];
        const container = document.getElementById('floor-plan');
        const containerRect = container.getBoundingClientRect();

        let newX = touch.clientX - containerRect.left - this.offsetX;
        let newY = touch.clientY - containerRect.top - this.offsetY;

        newX = Math.max(0, Math.min(newX, containerRect.width - 100));
        newY = Math.max(0, Math.min(newY, containerRect.height - 100));

        this.draggedElement.style.left = `${newX}px`;
        this.draggedElement.style.top = `${newY}px`;
    },

    async _handleTouchEnd(event) {
        if (!this.draggedElement || !this.editMode) return;

        this.draggedElement.style.opacity = '1';

        if (this.isDragging) {
            // Guardar nueva posición
            const tableId = this.draggedElement.dataset.id;
            const newX = parseFloat(this.draggedElement.style.left);
            const newY = parseFloat(this.draggedElement.style.top);

            try {
                await API.updatePosition(tableId, newX, newY);
                console.log(`[Interactions] Mesa movida (touch) a (${newX}, ${newY})`);
            } catch (error) {
                console.error('[Interactions] Error al guardar posición (touch)');
            }
        }

        this.draggedElement = null;
        this.isDragging = false;
    }
};
