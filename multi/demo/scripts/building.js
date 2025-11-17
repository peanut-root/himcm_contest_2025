/**
 * Building Layout Renderer
 *
 * Handles loading and rendering the building layout on HTML5 Canvas
 */

// State
let buildingData = null;
let resultsData = null;
let canvas = null;
let ctx = null;

// Room state colors
const ROOM_COLORS = {
    pending: '#FFD54F',      // Yellow
    'in-progress': '#29B6F6', // Blue
    completed: '#66BB6A'      // Green
};

// Room states tracking
const roomStates = new Map();

/**
 * Initialize the building renderer
 */
export async function initBuilding() {
    canvas = document.getElementById('canvas');
    if (!canvas) {
        throw new Error('Canvas element not found');
    }

    ctx = canvas.getContext('2d');
    if (!ctx) {
        throw new Error('Could not get 2D context');
    }

    // Load building layout
    await loadBuildingLayout();

    // Initialize all rooms as pending
    if (buildingData && buildingData.rooms) {
        buildingData.rooms.forEach(room => {
            roomStates.set(room.id, 'pending');
        });
    }

    // Initial render
    render();
}

/**
 * Load building layout from JSON
 */
export async function loadBuildingLayout() {
    try {
        const response = await fetch('data/building.json');
        if (!response.ok) {
            throw new Error(`Failed to load building: ${response.statusText}`);
        }
        buildingData = await response.json();
        console.log('Building loaded:', buildingData);
        return buildingData;
    } catch (error) {
        console.error('Error loading building:', error);
        showError('Failed to load building layout. Please ensure data/building.json exists.');
        throw error;
    }
}

/**
 * Load results from JSON
 */
export async function loadResults(scenarioName = 'basic') {
    try {
        const response = await fetch(`data/results-${scenarioName}.json`);
        if (!response.ok) {
            throw new Error(`Failed to load results: ${response.statusText}`);
        }
        resultsData = await response.json();
        console.log('Results loaded:', resultsData);

        // Reset room states
        if (buildingData && buildingData.rooms) {
            buildingData.rooms.forEach(room => {
                roomStates.set(room.id, 'pending');
            });
        }

        return resultsData;
    } catch (error) {
        console.error('Error loading results:', error);
        showError(`Failed to load scenario: ${scenarioName}`);
        throw error;
    }
}

/**
 * Update room state
 */
export function setRoomState(roomId, state) {
    if (roomStates.has(roomId)) {
        roomStates.set(roomId, state);
    }
}

/**
 * Get current room state
 */
export function getRoomState(roomId) {
    return roomStates.get(roomId) || 'pending';
}

/**
 * Main render function
 */
export function render() {
    if (!ctx || !buildingData) {
        return;
    }

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw background
    ctx.fillStyle = '#f5f5f5';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw building components
    drawHallway();
    drawRooms();
    drawExits();
}

/**
 * Draw hallway
 */
function drawHallway() {
    if (!buildingData || !buildingData.hallway) {
        return;
    }

    const hallway = buildingData.hallway;

    ctx.fillStyle = '#E0E0E0';
    ctx.fillRect(hallway.x, hallway.y, hallway.width, hallway.height);

    ctx.strokeStyle = '#999';
    ctx.lineWidth = 2;
    ctx.strokeRect(hallway.x, hallway.y, hallway.width, hallway.height);

    // Label
    ctx.fillStyle = '#666';
    ctx.font = 'bold 14px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('HALLWAY', hallway.x + hallway.width / 2, hallway.y + hallway.height / 2);
}

/**
 * Draw all rooms
 */
function drawRooms() {
    if (!buildingData || !buildingData.rooms) {
        return;
    }

    buildingData.rooms.forEach(room => {
        drawRoom(room);
    });
}

/**
 * Draw a single room
 */
function drawRoom(room) {
    const state = getRoomState(room.id);
    const color = ROOM_COLORS[state] || ROOM_COLORS.pending;

    // Room rectangle
    ctx.fillStyle = color;
    ctx.fillRect(room.x, room.y, room.width, room.height);

    // Border
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    ctx.strokeRect(room.x, room.y, room.width, room.height);

    // Label
    ctx.fillStyle = '#333';
    ctx.font = 'bold 16px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(room.label || room.id, room.x + room.width / 2, room.y + room.height / 2);

    // Room ID (smaller, below label)
    ctx.font = '12px sans-serif';
    ctx.fillStyle = '#666';
    ctx.fillText(`(${room.id})`, room.x + room.width / 2, room.y + room.height / 2 + 20);
}

/**
 * Draw exits
 */
function drawExits() {
    if (!buildingData || !buildingData.nodes) {
        return;
    }

    const exits = buildingData.nodes.filter(node => node.type === 'EXIT');

    exits.forEach(exit => {
        // Exit marker (triangle)
        ctx.fillStyle = '#E74C3C';
        ctx.beginPath();
        ctx.moveTo(exit.x, exit.y - 20);
        ctx.lineTo(exit.x - 15, exit.y + 10);
        ctx.lineTo(exit.x + 15, exit.y + 10);
        ctx.closePath();
        ctx.fill();

        // Border
        ctx.strokeStyle = '#C0392B';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Label
        ctx.fillStyle = '#333';
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.fillText(exit.label || 'EXIT', exit.x, exit.y + 15);
    });
}

/**
 * Show error message
 */
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #e74c3c;
        color: white;
        padding: 15px 20px;
        border-radius: 4px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        z-index: 1000;
    `;
    document.body.appendChild(errorDiv);

    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

/**
 * Get building data
 */
export function getBuildingData() {
    return buildingData;
}

/**
 * Get results data
 */
export function getResultsData() {
    return resultsData;
}

/**
 * Export render function for animation
 */
export { render as renderBuilding };
