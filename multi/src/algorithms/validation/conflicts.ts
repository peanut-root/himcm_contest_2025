// Temporal conflict detection - identify simultaneous room inspections

import { Route } from '../../models/route.js';

export interface ConflictResult {
  noRoomConflicts: boolean;
  conflictingActions: {
    agent1: string;
    agent2: string;
    roomId: string;
    time: number;
  }[];
}

/**
 * Detect temporal conflicts where multiple agents attempt to inspect
 * the same room simultaneously (overlapping INSPECT actions)
 */
export function detectRoomConflicts(routes: Route[]): ConflictResult {
  const conflictingActions: {
    agent1: string;
    agent2: string;
    roomId: string;
    time: number;
  }[] = [];

  // Extract all INSPECT actions with agent IDs
  const inspections: {
    agentId: string;
    roomId: string;
    startTime: number;
    endTime: number;
  }[] = [];

  for (const route of routes) {
    for (const action of route.actions) {
      if (action.type === 'INSPECT' && action.targetRoom) {
        inspections.push({
          agentId: route.agentId,
          roomId: action.targetRoom,
          startTime: action.startTime,
          endTime: action.endTime,
        });
      }
    }
  }

  // Check for overlapping inspections of the same room
  for (let i = 0; i < inspections.length; i++) {
    for (let j = i + 1; j < inspections.length; j++) {
      const insp1 = inspections[i];
      const insp2 = inspections[j];

      // Only check if same room
      if (insp1.roomId !== insp2.roomId) continue;

      // Check for time overlap
      const overlaps =
        (insp1.startTime < insp2.endTime && insp1.endTime > insp2.startTime) ||
        (insp2.startTime < insp1.endTime && insp2.endTime > insp1.startTime);

      if (overlaps) {
        conflictingActions.push({
          agent1: insp1.agentId,
          agent2: insp2.agentId,
          roomId: insp1.roomId,
          time: Math.max(insp1.startTime, insp2.startTime),
        });
      }
    }
  }

  return {
    noRoomConflicts: conflictingActions.length === 0,
    conflictingActions,
  };
}

/**
 * Get all corridor traversals (MOVE actions) organized by time
 * Useful for visualizing parallel corridor usage
 */
export function getCorridorTraversals(routes: Route[]) {
  const traversals: {
    agentId: string;
    location: string;
    startTime: number;
    endTime: number;
  }[] = [];

  for (const route of routes) {
    for (const action of route.actions) {
      if (action.type === 'MOVE') {
        traversals.push({
          agentId: route.agentId,
          location: action.location,
          startTime: action.startTime,
          endTime: action.endTime,
        });
      }
    }
  }

  return traversals.sort((a, b) => a.startTime - b.startTime);
}
