// Output formatter for mission result JSON generation

import { MissionResult } from '../models/mission.js';
import * as fs from 'fs';

export function formatMissionOutput(missionId: string, result: MissionResult): object {
  return {
    missionId,
    makespan: result.makespan,
    routes: result.routes.map((route) => ({
      agentId: route.agentId,
      actions: route.actions,
      roomsInspected: route.roomsInspected,
      totalTime: route.totalTime,
      pathLength: route.pathLength,
      clearanceOperations: route.clearanceOperations,
    })),
    metrics: result.metrics,
    validation: result.validation,
    ...(result.timeline && { timeline: result.timeline }),
  };
}

export function saveMissionOutput(missionId: string, result: MissionResult, filePath: string): void {
  const output = formatMissionOutput(missionId, result);
  fs.writeFileSync(filePath, JSON.stringify(output, null, 2), 'utf-8');
}

export function loadMissionOutput(filePath: string): object {
  const fileContent = fs.readFileSync(filePath, 'utf-8');
  return JSON.parse(fileContent);
}
