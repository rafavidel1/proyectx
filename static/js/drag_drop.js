let activeTable = null;
let initialX, initialY;
let currentX, currentY;
let xOffset = 0;
let yOffset = 0;
let draggedElement = null;
let offsetX = 0;
let offsetY = 0;

function initDrag(element) {
    element.addEventListener("mousedown", dragStart);
    element.addEventListener("touchstart", dragStart, { passive: false });
}

function dragStart(e) {
    // Don't drag if clicking specific buttons inside (if any)
    if (e.target.closest('.no-drag')) return;

    activeTable = e.currentTarget;
    
    // Get current position from style or dataset
    xOffset = parseInt(activeTable.style.left || 0);
    yOffset = parseInt(activeTable.style.top || 0);

    if (e.type === "touchstart") {
        initialX = e.touches[0].clientX - xOffset;
        initialY = e.touches[0].clientY - yOffset;
    } else {
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;
    }

    // Add global listeners
    document.addEventListener("mouseup", dragEnd);
    document.addEventListener("mousemove", drag);
    document.addEventListener("touchend", dragEnd);
    document.addEventListener("touchmove", drag, { passive: false });
}

function drag(e) {
    if (activeTable) {
        e.preventDefault();
    
        if (e.type === "touchmove") {
            currentX = e.touches[0].clientX - initialX;
            currentY = e.touches[0].clientY - initialY;
        } else {
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
        }

        xOffset = currentX;
        yOffset = currentY;

        setTranslate(currentX, currentY, activeTable);
    }
}

function setTranslate(xPos, yPos, el) {
    el.style.left = xPos + "px";
    el.style.top = yPos + "px";
}

function dragEnd(e) {
    if (!activeTable) return;

    initialX = currentX;
    initialY = currentY;

    // Save to backend
    const id = activeTable.dataset.id;
    savePosition(id, xOffset, yOffset);

    activeTable = null;

    document.removeEventListener("mouseup", dragEnd);
    document.removeEventListener("mousemove", drag);
    document.removeEventListener("touchend", dragEnd);
    document.removeEventListener("touchmove", drag);
}

async function savePosition(id, x, y) {
    try {
        await fetch('/api/tables/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, x, y })
        });
        console.log(`Saved ${id} at ${x}, ${y}`);
    } catch (error) {
        console.error('Error saving position:', error);
    }
}

function handleDragStart(event) {
    draggedElement = event.target;
    
    // Calculamos el offset del mouse respecto al elemento
    const rect = draggedElement.getBoundingClientRect();
    offsetX = event.clientX - rect.left;
    offsetY = event.clientY - rect.top;
    
    // Estilo visual durante el drag
    draggedElement.style.opacity = '0.5';
    draggedElement.style.cursor = 'grabbing';
    
    console.log('[drag_drop] Iniciando arrastre de:', draggedElement.id);
}

function handleDragEnd(event) {
    if (!draggedElement) return;
    
    // Restaurar estilo
    draggedElement.style.opacity = '1';
    draggedElement.style.cursor = 'move';
    
    // Calcular nueva posición relativa al contenedor
    const container = document.getElementById('floor-plan');
    if (!container) return;
    
    const containerRect = container.getBoundingClientRect();
    
    // Posición del mouse menos el offset
    let newX = event.clientX - containerRect.left - offsetX;
    let newY = event.clientY - containerRect.top - offsetY;
    
    // Limitar a los bordes del contenedor
    newX = Math.max(0, Math.min(newX, containerRect.width - 100));
    newY = Math.max(0, Math.min(newY, containerRect.height - 100));
    
    // Aplicar nueva posición
    draggedElement.style.left = `${newX}px`;
    draggedElement.style.top = `${newY}px`;
    
    // Actualizar data attributes
    draggedElement.dataset.x = newX;
    draggedElement.dataset.y = newY;
    
    console.log('[drag_drop] Nueva posición:', { x: newX, y: newY });
    
    draggedElement = null;
}

// Permitir el drop en el contenedor
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('floor-plan');
    if (container) {
        container.addEventListener('dragover', (e) => {
            e.preventDefault(); // Necesario para permitir drop
        });
    }
});
