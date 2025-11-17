// Greedy task allocation baseline

import { Room } from '../../models/building.js';
import { Agent } from '../../models/agent.js';

export interface AllocationResult {
  assignments: Map<string, string[]>; // agentId -> roomIds[]
}

export function greedyAllocate(
  agents: Agent[],
  rooms: Room[],
  redundantRooms: string[]
): AllocationResult {
  const assignments = new Map<string, string[]>();

  // Initialize empty assignments for each agent
  for (const agent of agents) {
    assignments.set(agent.id, []);
  }

  // Create task list with redundancy
  const tasks: string[] = [];
  for (const room of rooms) {
    tasks.push(room.id);
    if (redundantRooms.includes(room.id)) {
      tasks.push(room.id); // Add twice for redundancy
    }
  }

  // Track agent workload (simplified: just count tasks)
  const workload = new Map<string, number>();
  for (const agent of agents) {
    workload.set(agent.id, 0);
  }

  // Assign tasks to agent with minimum workload
  for (const task of tasks) {
    let minAgent = agents[0].id;
    let minLoad = workload.get(minAgent) || 0;

    for (const agent of agents) {
      const load = workload.get(agent.id) || 0;
      if (load < minLoad) {
        minLoad = load;
        minAgent = agent.id;
      }
    }

    // Assign task
    const agentTasks = assignments.get(minAgent)!;
    agentTasks.push(task);
    workload.set(minAgent, minLoad + 1);
  }

  return { assignments };
}
