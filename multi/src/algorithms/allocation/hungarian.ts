// Hungarian algorithm for task assignment
// Simplified implementation for MVP - handles basic assignment problem

import { Room } from '../../models/building.js';
import { Agent } from '../../models/agent.js';
import { AllocationResult } from './greedy.js';

export function hungarianAllocate(
  agents: Agent[],
  rooms: Room[],
  redundantRooms: string[],
  costMatrix?: number[][]
): AllocationResult {
  // Create task list with redundancy
  const tasks: string[] = [];
  for (const room of rooms) {
    tasks.push(room.id);
    if (redundantRooms.includes(room.id)) {
      tasks.push(room.id);
    }
  }

  const n = agents.length;
  const m = tasks.length;

  // Use provided cost matrix or create uniform cost
  let matrix: number[][];
  if (costMatrix && costMatrix.length === n && costMatrix[0].length === m) {
    matrix = costMatrix.map((row) => [...row]);
  } else {
    // Default: uniform costs
    matrix = Array(n)
      .fill(0)
      .map(() => Array(m).fill(1));
  }

  // Pad matrix to make it square
  const size = Math.max(n, m);
  const paddedMatrix: number[][] = Array(size)
    .fill(0)
    .map((_, i) =>
      Array(size)
        .fill(0)
        .map((_, j) => {
          if (i < n && j < m) return matrix[i][j];
          return 1000; // High cost for dummy assignments
        })
    );

  // Run simplified Hungarian algorithm
  const assignment = hungarianMethod(paddedMatrix);

  // Extract assignments
  const assignments = new Map<string, string[]>();
  for (const agent of agents) {
    assignments.set(agent.id, []);
  }

  for (let i = 0; i < n; i++) {
    const taskIdx = assignment[i];
    if (taskIdx < m) {
      const agentTasks = assignments.get(agents[i].id)!;
      agentTasks.push(tasks[taskIdx]);
    }
  }

  return { assignments };
}

function hungarianMethod(matrix: number[][]): number[] {
  const n = matrix.length;
  const cost = matrix.map((row) => [...row]);

  // Step 1: Row reduction
  for (let i = 0; i < n; i++) {
    const minVal = Math.min(...cost[i]);
    for (let j = 0; j < n; j++) {
      cost[i][j] -= minVal;
    }
  }

  // Step 2: Column reduction
  for (let j = 0; j < n; j++) {
    let minVal = Infinity;
    for (let i = 0; i < n; i++) {
      minVal = Math.min(minVal, cost[i][j]);
    }
    for (let i = 0; i < n; i++) {
      cost[i][j] -= minVal;
    }
  }

  // Step 3: Find optimal assignment (simplified greedy matching)
  const rowAssigned = new Array(n).fill(false);
  const colAssigned = new Array(n).fill(false);
  const assignment = new Array(n).fill(-1);

  // Greedy zero assignment
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      if (cost[i][j] === 0 && !rowAssigned[i] && !colAssigned[j]) {
        assignment[i] = j;
        rowAssigned[i] = true;
        colAssigned[j] = true;
        break;
      }
    }
  }

  // Assign remaining unassigned rows
  for (let i = 0; i < n; i++) {
    if (!rowAssigned[i]) {
      for (let j = 0; j < n; j++) {
        if (!colAssigned[j]) {
          assignment[i] = j;
          colAssigned[j] = true;
          break;
        }
      }
    }
  }

  return assignment;
}
