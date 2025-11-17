/**
 * Animation Controller
 *
 * Manages agent animation and position updates over time
 */

import { getBuildingData, getResultsData, setRoomState, renderBuilding } from './building.js';

// Animation state
let animationState = {
    isPlaying: false,
    currentTime: 0,
    speed: 0.5,  // Default to 0.5x speed for better visibility
    makespan: 0,
    agents: [],
    animationFrameId: null,
    lastFrameTime: 0
};

// Agent colors
const AGENT_COLORS = [
    '#E74C3C', // Red
    '#3498DB', // Blue
    '#2ECC71', // Green
    '#F39C12', // Orange
    '#9B59B6', // Purple
    '#1ABC9C', // Turquoise
    '#E67E22', // Carrot
    '#34495E'  // Dark gray
];

/**
 * Initialize animation system
 */
export function initAnimation(resultsData) {
    if (!resultsData || !resultsData.routes) {
        console.error('Invalid results data');
        return;
    }

    // Initialize agent data
    animationState.agents = resultsData.routes.map((route, index) => ({
        id: route.agentId,
        color: AGENT_COLORS[index % AGENT_COLORS.length],
        x: 0,
        y: 0,
        currentAction: null,
        currentActionIndex: 0,
        route: route,
        completed: false
    }));

    // Set makespan
    animationState.makespan = resultsData.makespan || 0;
    animationState.currentTime = 0;

    // Position agents at starting locations
    updateAgentPositions(0);

    console.log('Animation initialized:', animationState);
}

/**
 * Start animation
 */
export function startAnimation() {
    if (animationState.isPlaying) {
        return;
    }

    animationState.isPlaying = true;
    animationState.lastFrameTime = performance.now();
    animate();
}

/**
 * Pause animation
 */
export function pauseAnimation() {
    animationState.isPlaying = false;
    if (animationState.animationFrameId) {
        cancelAnimationFrame(animationState.animationFrameId);
        animationState.animationFrameId = null;
    }
}

/**
 * Restart animation
 */
export function restartAnimation() {
    animationState.currentTime = 0;
    animationState.isPlaying = false;
    updateAgentPositions(0);
    renderFrame();
}

/**
 * Set animation speed
 */
export function setSpeed(speed) {
    animationState.speed = Math.max(0.1, Math.min(3.0, speed));
}

/**
 * Scrub to specific time
 */
export function scrubTo(time) {
    animationState.currentTime = Math.max(0, Math.min(animationState.makespan, time));
    updateAgentPositions(animationState.currentTime);
    renderFrame();
}

/**
 * Main animation loop
 */
function animate() {
    if (!animationState.isPlaying) {
        return;
    }

    const currentFrameTime = performance.now();
    const deltaTime = (currentFrameTime - animationState.lastFrameTime) / 1000; // Convert to seconds
    animationState.lastFrameTime = currentFrameTime;

    // Update current time based on speed
    animationState.currentTime += deltaTime * animationState.speed * 60; // Scale by speed

    // Check if animation is complete
    if (animationState.currentTime >= animationState.makespan) {
        animationState.currentTime = animationState.makespan;
        pauseAnimation();
    }

    // Update agent positions
    updateAgentPositions(animationState.currentTime);

    // Render frame
    renderFrame();

    // Continue animation loop
    if (animationState.isPlaying) {
        animationState.animationFrameId = requestAnimationFrame(animate);
    }
}

/**
 * Update agent positions based on current time
 */
export function updateAgentPositions(time) {
    const buildingData = getBuildingData();
    if (!buildingData) {
        return;
    }

    animationState.agents.forEach(agent => {
        // Find current action
        const action = findCurrentAction(agent.route.actions, time);

        if (!action) {
            // No action at this time, agent is done
            agent.completed = true;
            agent.currentAction = null;
            return;
        }

        agent.currentAction = action;

        // Update position based on action type
        if (action.type === 'MOVE') {
            // Linear interpolation between start and end positions
            const progress = (time - action.startTime) / action.duration;
            const clampedProgress = Math.max(0, Math.min(1, progress));

            const fromPos = getNodePosition(buildingData, action.from || action.location);
            const toPos = getNodePosition(buildingData, action.to || action.location);

            if (fromPos && toPos) {
                agent.x = fromPos.x + (toPos.x - fromPos.x) * clampedProgress;
                agent.y = fromPos.y + (toPos.y - fromPos.y) * clampedProgress;
            }
        } else if (action.type === 'INSPECT') {
            // Agent is inspecting a room
            const roomPos = getRoomCenter(buildingData, action.location);
            if (roomPos) {
                agent.x = roomPos.x;
                agent.y = roomPos.y;
            }

            // Update room state
            const actionEndTime = action.startTime + action.duration;
            if (time >= action.startTime && time < actionEndTime) {
                setRoomState(action.location, 'in-progress');
            } else if (time >= actionEndTime) {
                setRoomState(action.location, 'completed');
            }
        }
    });

    // Update room states for all inspected rooms
    updateRoomStates(time);
}

/**
 * Find current action at given time
 */
function findCurrentAction(actions, time) {
    for (const action of actions) {
        const endTime = action.startTime + action.duration;
        if (time >= action.startTime && time < endTime) {
            return action;
        }
    }
    return null;
}

/**
 * Update all room states based on current time
 */
function updateRoomStates(time) {
    const resultsData = getResultsData();
    if (!resultsData || !resultsData.routes) {
        return;
    }

    // Check all agent routes for inspection actions
    resultsData.routes.forEach(route => {
        route.actions.forEach(action => {
            if (action.type === 'INSPECT') {
                const actionEndTime = action.startTime + action.duration;

                if (time < action.startTime) {
                    // Not yet started (keep as pending)
                } else if (time >= action.startTime && time < actionEndTime) {
                    setRoomState(action.location, 'in-progress');
                } else if (time >= actionEndTime) {
                    setRoomState(action.location, 'completed');
                }
            }
        });
    });
}

/**
 * Get node position from building data
 */
function getNodePosition(buildingData, nodeId) {
    if (!buildingData || !buildingData.nodes) {
        return null;
    }

    const node = buildingData.nodes.find(n => n.id === nodeId);
    if (node) {
        return { x: node.x, y: node.y };
    }

    // Check if it's the hallway
    if (nodeId === 'hallway' && buildingData.hallway) {
        const hallway = buildingData.hallway;
        return {
            x: hallway.x + hallway.width / 2,
            y: hallway.y + hallway.height / 2
        };
    }

    return null;
}

/**
 * Get room center position
 */
function getRoomCenter(buildingData, roomId) {
    if (!buildingData || !buildingData.rooms) {
        return null;
    }

    const room = buildingData.rooms.find(r => r.id === roomId);
    if (room) {
        return {
            x: room.x + room.width / 2,
            y: room.y + room.height / 2
        };
    }

    return null;
}

/**
 * Render current frame
 */
function renderFrame() {
    // Render building (rooms, hallway, exits)
    renderBuilding();

    // Draw agents
    drawAgents();
}

/**
 * Draw all agents
 */
export function drawAgents() {
    const canvas = document.getElementById('canvas');
    if (!canvas) {
        return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) {
        return;
    }

    animationState.agents.forEach(agent => {
        // Draw agent circle
        ctx.fillStyle = agent.color;
        ctx.beginPath();
        ctx.arc(agent.x, agent.y, 12, 0, Math.PI * 2);
        ctx.fill();

        // Border
        ctx.strokeStyle = '#FFF';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Label
        ctx.fillStyle = '#FFF';
        ctx.font = 'bold 10px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(agent.id, agent.x, agent.y);
    });
}

/**
 * Get current animation state (for controls/metrics)
 */
export function getAnimationState() {
    return animationState;
}
