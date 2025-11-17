// Coverage verification - check all rooms inspected

import { Room } from '../../models/building.js';
import { Route } from '../../models/route.js';

export interface CoverageResult {
  allRoomsInspected: boolean;
  missingRooms: string[];
  redundancySatisfied: boolean;
  insufficientInspections: {
    roomId: string;
    inspectionCount: number;
  }[];
}

export function verifyCoverage(
  rooms: Room[],
  routes: Route[],
  redundantRooms: string[]
): CoverageResult {
  // Count inspections per room
  const inspectionCount = new Map<string, Set<string>>();

  for (const room of rooms) {
    inspectionCount.set(room.id, new Set());
  }

  // Count inspections from routes
  for (const route of routes) {
    for (const roomId of route.roomsInspected) {
      if (inspectionCount.has(roomId)) {
        inspectionCount.get(roomId)!.add(route.agentId);
      }
    }
  }

  // Check coverage
  const missingRooms: string[] = [];
  for (const room of rooms) {
    const count = inspectionCount.get(room.id)?.size || 0;
    if (count === 0) {
      missingRooms.push(room.id);
    }
  }

  // Check redundancy
  const insufficientInspections: { roomId: string; inspectionCount: number }[] = [];
  for (const roomId of redundantRooms) {
    const count = inspectionCount.get(roomId)?.size || 0;
    if (count < 2) {
      insufficientInspections.push({ roomId, inspectionCount: count });
    }
  }

  return {
    allRoomsInspected: missingRooms.length === 0,
    missingRooms,
    redundancySatisfied: insufficientInspections.length === 0,
    insufficientInspections,
  };
}

export function verifyReturnToExit(
  routes: Route[],
  exits: string[],
  returnRequired: boolean
): { allReturned: boolean; failedReturns: string[] } {
  if (!returnRequired) {
    return { allReturned: true, failedReturns: [] };
  }

  const failedReturns: string[] = [];

  for (const route of routes) {
    if (route.actions.length === 0) continue;

    const lastAction = route.actions[route.actions.length - 1];
    if (!exits.includes(lastAction.location)) {
      failedReturns.push(route.agentId);
    }
  }

  return {
    allReturned: failedReturns.length === 0,
    failedReturns,
  };
}
