/**
 * Playback Controls
 *
 * Handles UI controls for animation playback
 */

import { initBuilding, loadResults, renderBuilding } from './building.js';
import {
    initAnimation,
    startAnimation,
    pauseAnimation,
    restartAnimation,
    setSpeed,
    scrubTo,
    getAnimationState
} from './animation.js';
import { updateMetrics, updateTimeDisplay } from './metrics.js';

// Current scenario
let currentScenario = 'basic';

/**
 * Initialize the application
 */
export async function init() {
    try {
        // Show loading
        showLoading(true);

        // Initialize building
        await initBuilding();

        // Load initial scenario
        await loadScenario(currentScenario);

        // Setup event listeners
        setupEventListeners();

        // Hide loading
        showLoading(false);

        console.log('Application initialized successfully');
    } catch (error) {
        console.error('Initialization error:', error);
        showLoading(false);
        alert('Failed to initialize application. Please check console for details.');
    }
}

/**
 * Load a scenario
 */
async function loadScenario(scenarioName) {
    try {
        showLoading(true);

        // Pause any existing animation
        pauseAnimation();

        // Load results
        const resultsData = await loadResults(scenarioName);

        // Initialize animation with results
        initAnimation(resultsData);

        // Update metrics display
        updateMetrics(resultsData);

        // Update scenario description
        updateScenarioDescription(scenarioName, resultsData);

        // Update timeline slider max value
        const timelineSlider = document.getElementById('timeline-slider');
        if (timelineSlider && resultsData) {
            timelineSlider.max = resultsData.makespan || 100;
            timelineSlider.value = 0;
        }

        // Render initial state
        renderBuilding();

        // Update time display
        updateTimeDisplay(0, resultsData.makespan || 0);

        // Reset button states
        updateButtonStates(false);

        showLoading(false);
        currentScenario = scenarioName;
    } catch (error) {
        console.error('Error loading scenario:', error);
        showLoading(false);
        throw error;
    }
}

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Scenario selector
    const scenarioSelect = document.getElementById('scenario');
    if (scenarioSelect) {
        scenarioSelect.addEventListener('change', (e) => {
            loadScenario(e.target.value);
        });
    }

    // Play button
    const playBtn = document.getElementById('btn-play');
    if (playBtn) {
        playBtn.addEventListener('click', () => {
            startAnimation();
            updateButtonStates(true);
            startTimeUpdateLoop();
        });
    }

    // Pause button
    const pauseBtn = document.getElementById('btn-pause');
    if (pauseBtn) {
        pauseBtn.addEventListener('click', () => {
            pauseAnimation();
            updateButtonStates(false);
        });
    }

    // Restart button
    const restartBtn = document.getElementById('btn-restart');
    if (restartBtn) {
        restartBtn.addEventListener('click', () => {
            restartAnimation();
            updateButtonStates(false);

            // Update displays
            const state = getAnimationState();
            updateTimeDisplay(0, state.makespan);

            const timelineSlider = document.getElementById('timeline-slider');
            if (timelineSlider) {
                timelineSlider.value = 0;
            }
        });
    }

    // Speed slider
    const speedSlider = document.getElementById('speed-slider');
    if (speedSlider) {
        speedSlider.addEventListener('input', (e) => {
            const speed = parseFloat(e.target.value);
            setSpeed(speed);

            const speedDisplay = document.getElementById('speed-display');
            if (speedDisplay) {
                speedDisplay.textContent = `${speed.toFixed(1)}x`;
            }
        });
    }

    // Timeline slider
    const timelineSlider = document.getElementById('timeline-slider');
    if (timelineSlider) {
        timelineSlider.addEventListener('input', (e) => {
            const time = parseFloat(e.target.value);
            scrubTo(time);

            const state = getAnimationState();
            updateTimeDisplay(time, state.makespan);
        });
    }

    // Canvas hover for tooltips
    const canvas = document.getElementById('canvas');
    if (canvas) {
        canvas.addEventListener('mousemove', handleCanvasHover);
        canvas.addEventListener('mouseleave', hideHoverInfo);
    }
}

/**
 * Handle canvas hover to show tooltips
 */
function handleCanvasHover(e) {
    const canvas = e.target;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Check if hovering over an agent
    const state = getAnimationState();
    let found = false;

    for (const agent of state.agents) {
        const dx = x - agent.x;
        const dy = y - agent.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance <= 12) { // Agent radius
            const currentAction = agent.currentAction;
            const actionType = currentAction ? currentAction.type : 'Waiting';
            const location = currentAction ? currentAction.location : 'N/A';
            const elapsed = Math.floor(state.currentTime);

            showHoverInfo(`<strong>${agent.id}</strong><br>Action: ${actionType}<br>Location: ${location}<br>Time: ${elapsed}s`);
            found = true;
            break;
        }
    }

    if (!found) {
        // Check if hovering over a room (using imported building data check)
        import('./building.js').then(module => {
            const buildingData = module.getBuildingData();
            if (buildingData && buildingData.rooms) {
                for (const room of buildingData.rooms) {
                    if (x >= room.x && x <= room.x + room.width &&
                        y >= room.y && y <= room.y + room.height) {
                        const roomState = module.getRoomState(room.id);
                        showHoverInfo(`<strong>${room.label || room.id}</strong><br>Status: ${roomState.toUpperCase()}<br>ID: ${room.id}`);
                        found = true;
                        break;
                    }
                }
            }

            if (!found) {
                hideHoverInfo();
            }
        });
    }
}

/**
 * Show hover info
 */
function showHoverInfo(html) {
    const hoverInfo = document.getElementById('hover-info');
    const hoverContent = document.getElementById('hover-info-content');

    if (hoverInfo && hoverContent) {
        hoverContent.innerHTML = html;
        hoverInfo.style.display = 'block';
    }
}

/**
 * Hide hover info
 */
function hideHoverInfo() {
    const hoverInfo = document.getElementById('hover-info');
    if (hoverInfo) {
        hoverInfo.style.display = 'none';
    }
}

/**
 * Update button states based on playback status
 */
function updateButtonStates(isPlaying) {
    const playBtn = document.getElementById('btn-play');
    const pauseBtn = document.getElementById('btn-pause');

    if (playBtn) {
        playBtn.disabled = isPlaying;
    }

    if (pauseBtn) {
        pauseBtn.disabled = !isPlaying;
    }
}

/**
 * Update scenario description
 */
function updateScenarioDescription(scenarioName, resultsData) {
    const descElement = document.getElementById('scenario-description');
    if (!descElement) {
        return;
    }

    const descriptions = {
        basic: '2 agents, 6 rooms, simple patrol',
        redundancy: '3 agents, 6 rooms, redundant coverage',
        return: '2 agents, 4 rooms, return to exits',
        multi: '5 agents, 10 rooms, large facility'
    };

    const desc = descriptions[scenarioName] || '';
    descElement.textContent = desc;
}

/**
 * Start time update loop (for live time display during animation)
 */
let timeUpdateInterval = null;

function startTimeUpdateLoop() {
    // Clear any existing interval
    if (timeUpdateInterval) {
        clearInterval(timeUpdateInterval);
    }

    // Update time display every 100ms during animation
    timeUpdateInterval = setInterval(() => {
        const state = getAnimationState();
        if (!state.isPlaying) {
            clearInterval(timeUpdateInterval);
            timeUpdateInterval = null;
            return;
        }

        updateTimeDisplay(state.currentTime, state.makespan);

        // Update timeline slider
        const timelineSlider = document.getElementById('timeline-slider');
        if (timelineSlider) {
            timelineSlider.value = state.currentTime;
        }
    }, 100);
}

/**
 * Show/hide loading indicator
 */
function showLoading(show) {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = show ? 'block' : 'none';
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
