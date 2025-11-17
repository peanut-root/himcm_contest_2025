// Performance metrics calculator

import { Route } from '../../models/route.js';
import { PerformanceMetrics } from '../../models/mission.js';

export function calculateMetrics(
  routes: Route[],
  redundantRoomsCount: number
): PerformanceMetrics {
  // Calculate makespan (max completion time)
  const makespan = Math.max(...routes.map((r) => r.totalTime), 0);

  // Individual times
  const individualTimes = routes.map((route) => ({
    agentId: route.agentId,
    completionTime: route.totalTime,
  }));

  // Total path length
  const totalPathLength = routes.reduce((sum, route) => sum + route.pathLength, 0);

  // Redundancy coverage
  const redundantRoomInspections = new Map<string, Set<string>>();
  for (const route of routes) {
    for (const roomId of route.roomsInspected) {
      if (!redundantRoomInspections.has(roomId)) {
        redundantRoomInspections.set(roomId, new Set());
      }
      redundantRoomInspections.get(roomId)!.add(route.agentId);
    }
  }

  let redundantCompleted = 0;
  for (const [, agents] of redundantRoomInspections) {
    if (agents.size >= 2) {
      redundantCompleted++;
    }
  }

  const redundancyCoverage = {
    required: redundantRoomsCount,
    completed: redundantCompleted,
    rate: redundantRoomsCount > 0 ? redundantCompleted / redundantRoomsCount : 1.0,
  };

  // Clearance efficiency
  const totalClearances = routes.reduce((sum, route) => sum + route.clearanceOperations, 0);
  const totalEdgeTraversals = routes.reduce((sum, route) => {
    return sum + route.actions.filter((a) => a.type === 'MOVE').length;
  }, 0);

  const clearanceEfficiency = {
    edgesCleared: totalClearances,
    totalEdgeTraversals,
    rate: totalEdgeTraversals > 0 ? totalClearances / totalEdgeTraversals : 0,
  };

  // Load balance
  const times = routes.map((r) => r.totalTime);
  const mean = times.reduce((sum, t) => sum + t, 0) / times.length;
  const variance = times.reduce((sum, t) => sum + (t - mean) ** 2, 0) / times.length;
  const stdDev = Math.sqrt(variance);
  const maxDeviation = Math.max(...times) - Math.min(...times);

  const loadBalance = {
    mean,
    stdDev,
    maxDeviation,
  };

  return {
    makespan,
    individualTimes,
    totalPathLength,
    redundancyCoverage,
    clearanceEfficiency,
    loadBalance,
  };
}
