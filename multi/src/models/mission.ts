// Mission model - Complete mission configuration and results

import { Building } from './building.js';
import { Agent } from './agent.js';
import { Route } from './route.js';

export interface MissionConfig {
  building: Building;
  agents: Agent[];
  redundantRooms: string[];
  returnToExit: boolean;
  timeParameters: {
    enterTime: number;
    exitTime: number;
  };
}

export interface PerformanceMetrics {
  makespan: number;
  individualTimes: {
    agentId: string;
    completionTime: number;
  }[];
  totalPathLength: number;
  redundancyCoverage: {
    required: number;
    completed: number;
    rate: number;
  };
  clearanceEfficiency: {
    edgesCleared: number;
    totalEdgeTraversals: number;
    rate: number;
  };
  loadBalance: {
    mean: number;
    stdDev: number;
    maxDeviation: number;
  };
}

export interface ValidationResult {
  valid: boolean;
  coverage: {
    allRoomsInspected: boolean;
    missingRooms: string[];
  };
  redundancy: {
    redundancySatisfied: boolean;
    insufficientInspections: {
      roomId: string;
      inspectionCount: number;
    }[];
  };
  conflicts: {
    noRoomConflicts: boolean;
    conflictingActions: {
      agent1: string;
      agent2: string;
      roomId: string;
      time: number;
    }[];
  };
  returnToExit: {
    allReturned: boolean;
    failedReturns: string[];
  };
  errors: string[];
}

export interface TimelineData {
  agents: {
    agentId: string;
    activities: {
      startTime: number;
      endTime: number;
      label: string;
      type: string;
      color?: string;
    }[];
  }[];
  events: {
    time: number;
    description: string;
    agents?: string[];
  }[];
  duration: number;
}

export interface MissionResult {
  routes: Route[];
  makespan: number;
  metrics: PerformanceMetrics;
  validation: ValidationResult;
  timeline?: TimelineData;
}

export interface Mission {
  id: string;
  config: MissionConfig;
  result?: MissionResult;
  status: 'PENDING' | 'PLANNING' | 'COMPLETED' | 'FAILED';
  createdAt: Date;
  completedAt?: Date;
  error?: string;
}
