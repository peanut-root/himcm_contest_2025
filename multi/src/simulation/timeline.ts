// Timeline builder - extract activities from routes and create visualization data

import { Route } from '../models/route.js';
import { TimelineData } from '../models/mission.js';
import { detectRoomConflicts } from '../algorithms/validation/conflicts.js';

/**
 * Build timeline visualization data from mission routes
 * Converts route actions into timeline activities with appropriate colors
 */
export function buildTimeline(routes: Route[]): TimelineData {
  const agents: TimelineData['agents'] = [];
  const events: TimelineData['events'] = [];
  let maxTime = 0;

  // Convert routes to timeline activities
  for (const route of routes) {
    const activities: TimelineData['agents'][0]['activities'] = [];

    for (const action of route.actions) {
      let label = '';
      let color = '';

      switch (action.type) {
        case 'MOVE':
          label = `Move to ${action.location}`;
          color = action.clearedEdge ? '#ff9800' : '#2196f3'; // Orange if cleared, blue otherwise
          break;
        case 'ENTER':
          label = `Enter ${action.targetRoom}`;
          color = '#4caf50'; // Green
          break;
        case 'INSPECT':
          label = `Inspect ${action.targetRoom}`;
          color = '#f44336'; // Red (critical activity)
          break;
        case 'EXIT_ROOM':
          label = `Exit ${action.targetRoom}`;
          color = '#4caf50'; // Green
          break;
        default:
          label = action.type;
          color = '#9e9e9e'; // Gray
      }

      activities.push({
        startTime: action.startTime,
        endTime: action.endTime,
        label,
        type: action.type,
        color,
      });

      maxTime = Math.max(maxTime, action.endTime);
    }

    agents.push({
      agentId: route.agentId,
      activities,
    });
  }

  // Detect conflicts and add as events
  const conflicts = detectRoomConflicts(routes);
  for (const conflict of conflicts.conflictingActions) {
    events.push({
      time: conflict.time,
      description: `⚠️ Conflict: ${conflict.agent1} and ${conflict.agent2} both in ${conflict.roomId}`,
      agents: [conflict.agent1, conflict.agent2],
    });
  }

  // Add start/end events
  events.push({
    time: 0,
    description: 'Mission Start',
  });

  events.push({
    time: maxTime,
    description: 'Mission Complete',
  });

  // Sort events by time
  events.sort((a, b) => a.time - b.time);

  return {
    agents,
    events,
    duration: maxTime,
  };
}

/**
 * Insert wait times when room conflicts are detected
 * Returns modified routes with WAIT actions inserted
 */
export function insertWaitTimes(routes: Route[]): Route[] {
  const conflicts = detectRoomConflicts(routes);

  if (conflicts.noRoomConflicts) {
    return routes; // No changes needed
  }

  // For now, just return original routes
  // Full implementation would reschedule conflicting inspections
  // This is a TODO for future enhancement
  return routes;
}
