/**
 * Metrics Display
 *
 * Handles displaying mission statistics and metrics
 */

/**
 * Update metrics panel with results data
 */
export function updateMetrics(resultsData) {
    if (!resultsData) {
        clearMetrics();
        return;
    }

    // Update makespan
    const makespanElement = document.getElementById('metric-makespan');
    if (makespanElement) {
        makespanElement.textContent = `${resultsData.makespan}s`;
    }

    // Update coverage
    const coverageElement = document.getElementById('metric-coverage');
    if (coverageElement && resultsData.metrics) {
        const coverage = resultsData.metrics.coverage || 0;
        coverageElement.textContent = `${coverage}%`;
    }

    // Update path length
    const pathLengthElement = document.getElementById('metric-path-length');
    if (pathLengthElement && resultsData.metrics) {
        const pathLength = resultsData.metrics.totalPathLength || 0;
        pathLengthElement.textContent = `${pathLength}m`;
    }

    // Update agent times
    updateAgentTimes(resultsData.routes);

    // Update agent paths
    updateAgentPaths(resultsData.routes);
}

/**
 * Update agent times display
 */
function updateAgentTimes(routes) {
    const agentTimesContainer = document.getElementById('agent-times');
    if (!agentTimesContainer || !routes) {
        return;
    }

    // Clear existing
    agentTimesContainer.innerHTML = '';

    // Add each agent's completion time
    routes.forEach(route => {
        const agentTimeDiv = document.createElement('div');
        agentTimeDiv.className = 'agent-time';

        const agentIdSpan = document.createElement('span');
        agentIdSpan.className = 'agent-id';
        agentIdSpan.textContent = route.agentId;

        const timeValueSpan = document.createElement('span');
        timeValueSpan.className = 'time-value';
        timeValueSpan.textContent = `${route.completionTime || 0}s`;

        agentTimeDiv.appendChild(agentIdSpan);
        agentTimeDiv.appendChild(timeValueSpan);
        agentTimesContainer.appendChild(agentTimeDiv);
    });
}

/**
 * Update agent paths display
 */
function updateAgentPaths(routes) {
    const agentPathsContainer = document.getElementById('agent-paths');
    if (!agentPathsContainer || !routes) {
        return;
    }

    // Clear existing
    agentPathsContainer.innerHTML = '';

    // Add each agent's path
    routes.forEach(route => {
        const agentPathDiv = document.createElement('div');
        agentPathDiv.className = 'agent-path';

        const headerDiv = document.createElement('div');
        headerDiv.className = 'agent-path-header';

        const agentIdSpan = document.createElement('span');
        agentIdSpan.className = 'agent-id';
        agentIdSpan.textContent = route.agentId;

        // Calculate path length (sum of all MOVE durations)
        let pathLength = 0;
        if (route.actions && route.actions.length > 0) {
            pathLength = route.actions
                .filter(action => action.type === 'MOVE')
                .reduce((sum, action) => sum + (action.duration || 0), 0);
        }

        const lengthSpan = document.createElement('span');
        lengthSpan.className = 'path-length';
        lengthSpan.textContent = `${pathLength} units`;

        headerDiv.appendChild(agentIdSpan);
        headerDiv.appendChild(lengthSpan);

        const pathValueSpan = document.createElement('span');
        pathValueSpan.className = 'path-value';

        // Format the path: startLocation → R1 → R2 → ... → endLocation
        const startLocation = route.startLocation || 'Unknown';
        const rooms = route.roomsInspected || [];

        // Get the end location from the last action
        let endLocation = startLocation;
        if (route.actions && route.actions.length > 0) {
            const lastAction = route.actions[route.actions.length - 1];
            endLocation = lastAction.to || lastAction.location || startLocation;
        }

        // Build path string
        const pathParts = [startLocation, ...rooms, endLocation];
        pathValueSpan.textContent = pathParts.join(' → ');

        agentPathDiv.appendChild(headerDiv);
        agentPathDiv.appendChild(pathValueSpan);
        agentPathsContainer.appendChild(agentPathDiv);
    });
}

/**
 * Clear all metrics
 */
function clearMetrics() {
    const makespanElement = document.getElementById('metric-makespan');
    if (makespanElement) {
        makespanElement.textContent = '--';
    }

    const coverageElement = document.getElementById('metric-coverage');
    if (coverageElement) {
        coverageElement.textContent = '--';
    }

    const pathLengthElement = document.getElementById('metric-path-length');
    if (pathLengthElement) {
        pathLengthElement.textContent = '--';
    }

    const agentTimesContainer = document.getElementById('agent-times');
    if (agentTimesContainer) {
        agentTimesContainer.innerHTML = '';
    }

    const agentPathsContainer = document.getElementById('agent-paths');
    if (agentPathsContainer) {
        agentPathsContainer.innerHTML = '';
    }
}

/**
 * Update time display in controls
 */
export function updateTimeDisplay(currentTime, makespan) {
    const timeDisplay = document.getElementById('time-display');
    if (timeDisplay) {
        const currentSec = Math.floor(currentTime);
        const makespanSec = Math.floor(makespan);
        timeDisplay.textContent = `${currentSec}s / ${makespanSec}s`;
    }
}
