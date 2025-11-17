// ILP task allocation using javascript-lp-solver

import { Room } from '../../models/building.js';
import { Agent } from '../../models/agent.js';
import { AllocationResult } from './greedy.js';
import solver from 'javascript-lp-solver';

export async function ilpAllocate(
  agents: Agent[],
  rooms: Room[],
  redundantRooms: string[]
): Promise<AllocationResult> {
  // Variables: x[agent][room] = 1 if agent inspects room
  const variables: any = {};
  const constraints: any = {};

  // Create variables for each agent-room pair
  for (const agent of agents) {
    for (const room of rooms) {
      const varName = `x_${agent.id}_${room.id}`;
      variables[varName] = {
        agent: agent.id,
        room: room.id,
        cost: 1, // Simplified: uniform cost (can be replaced with estimated time)
      };
    }
  }

  // Constraint: Each room must be inspected at least once
  for (const room of rooms) {
    const constraintName = `coverage_${room.id}`;
    constraints[constraintName] = { min: 1 };

    for (const agent of agents) {
      const varName = `x_${agent.id}_${room.id}`;
      if (!constraints[constraintName][varName]) {
        constraints[constraintName][varName] = 0;
      }
      constraints[constraintName][varName] += 1;
    }
  }

  // Constraint: Redundant rooms must be inspected at least twice
  for (const roomId of redundantRooms) {
    const constraintName = `redundancy_${roomId}`;
    constraints[constraintName] = { min: 2 };

    for (const agent of agents) {
      const varName = `x_${agent.id}_${roomId}`;
      if (!constraints[constraintName][varName]) {
        constraints[constraintName][varName] = 0;
      }
      constraints[constraintName][varName] += 1;
    }
  }

  // Constraint: Balance workload (soft constraint - limit max tasks per agent)
  const avgLoad = Math.ceil((rooms.length + redundantRooms.length) / agents.length);
  for (const agent of agents) {
    const constraintName = `workload_${agent.id}`;
    constraints[constraintName] = { max: avgLoad + 2 }; // Allow some flexibility

    for (const room of rooms) {
      const varName = `x_${agent.id}_${room.id}`;
      if (!constraints[constraintName][varName]) {
        constraints[constraintName][varName] = 0;
      }
      constraints[constraintName][varName] += 1;
    }
  }

  // Solve ILP
  const model = {
    optimize: 'cost',
    opType: 'min' as const,
    constraints,
    variables,
    ints: Object.keys(variables).reduce((acc: any, key) => {
      acc[key] = 1;
      return acc;
    }, {}),
  };

  let result;
  try {
    result = solver.Solve(model);
  } catch (error) {
    console.error('ILP solver failed, falling back to greedy:', error);
    // Fallback to greedy if solver fails
    const greedy = await import('./greedy.js');
    return greedy.greedyAllocate(agents, rooms, redundantRooms);
  }

  // Check if solution is feasible
  if (!result || !result.feasible) {
    // Fallback to greedy if ILP is infeasible
    const greedy = await import('./greedy.js');
    return greedy.greedyAllocate(agents, rooms, redundantRooms);
  }

  // Extract assignments
  const assignments = new Map<string, string[]>();
  for (const agent of agents) {
    assignments.set(agent.id, []);
  }

  if (result && result.feasible) {
    for (const varName in result) {
      if (varName.startsWith('x_') && result[varName] === 1) {
        const parts = varName.split('_');
        const agentId = parts[1];
        const roomId = parts[2];

        if (assignments.has(agentId)) {
          assignments.get(agentId)!.push(roomId);
        }
      }
    }
  }

  return { assignments };
}
