/**
 * Aplicación Principal - Orquesta todos los módulos.
 */
const App = {

    tables: [],
    editMode: false,

    async init() {
        console.log('[App] Inicializando Floor Plan Manager...');

        // Inicializar módulos
        MapRenderer.init();
        Interactions.init();
        ModalManager.init();

        // Configurar controles
        this._setupZoneSwitcher();
        this._setupEditToggle();
        this._setupDatePicker();

        // Cargar datos iniciales
        await this.loadAndRender();

        console.log('[App] Aplicación lista');
    },

    _setupDatePicker() {
        const datePicker = document.getElementById('date-picker');
        if (!datePicker) return;

        // Establecer fecha actual por defecto
        const today = new Date().toISOString().split('T')[0];
        datePicker.value = today;

        datePicker.addEventListener('change', () => {
            console.log('[App] Fecha seleccionada:', datePicker.value);
            this.loadAndRender();
        });
    },

    getSelectedDate() {
        const datePicker = document.getElementById('date-picker');
        return datePicker ? datePicker.value : null;
    },

    async loadAndRender() {
        try {
            this.tables = await API.getTables();
            console.log('[App] Mesas cargadas:', this.tables);
            console.log('[App] ¿Es array?', Array.isArray(this.tables));
            this.render();
        } catch (error) {
            console.error('[App] Error al cargar datos:', error);
        }
    },

    render() {
        console.log('[App] Renderizando con', this.tables.length, 'mesas');
        MapRenderer.renderTables(this.tables);

        // Validar que tables es array antes de filtrar
        if (!Array.isArray(this.tables)) {
            console.error('[App] Error: this.tables no es un array');
            return;
        }

        const toggle = document.getElementById('edit-toggle');
        const editEnabled = !!(toggle && toggle.checked);
        Interactions.toggleEditMode(editEnabled);
        // Adjuntar eventos a cada mesa renderizada
        this.tables
            .filter(t => t.zone === MapRenderer.currentZone)
            .forEach(table => {
                const el = document.getElementById(`table-${table.id}`);
                if (el) Interactions.attachToTable(el, table);
            });
    },

    _setupZoneSwitcher() {
        const btnInterior = document.getElementById('btn-interior');
        const btnTerraza = document.getElementById('btn-terraza');

        const switchZone = (zone) => {
            MapRenderer.setZone(zone);
            this.render();

            // Actualizar estilos de botones
            if (zone === 'interior') {
                btnInterior.className = "px-4 py-2 rounded-lg text-sm font-medium transition-colors bg-slate-800 text-white";
                btnTerraza.className = "px-4 py-2 rounded-lg text-sm font-medium transition-colors bg-slate-200 text-slate-600 hover:bg-slate-300";
            } else {
                btnInterior.className = "px-4 py-2 rounded-lg text-sm font-medium transition-colors bg-slate-200 text-slate-600 hover:bg-slate-300";
                btnTerraza.className = "px-4 py-2 rounded-lg text-sm font-medium transition-colors bg-slate-800 text-white";
            }
        };

        btnInterior.addEventListener('click', () => switchZone('interior'));
        btnTerraza.addEventListener('click', () => switchZone('terraza'));
    },

    _setupEditToggle() {
        const toggle = document.getElementById('edit-toggle');
        if (!toggle) return;
        toggle.addEventListener('change', (e) => {
            Interactions.toggleEditMode(e.target.checked);
        });
    }
};

// Exponer globalmente para acceso desde modales
window.App = App;
window.ModalManager = ModalManager;

// Iniciar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
