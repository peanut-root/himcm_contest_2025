// Route planner coordinator - integrates allocation and pathfinding

import { MissionConfig, MissionResult } from '../models/mission.js';
import { Route, Action } from '../models/route.js';
import { Graph } from '../models/graph.js';
import { ilpAllocate } from '../algorithms/allocation/ilp.js';
import { findShortestPath } from '../algorithms/pathfinding/shortest-path.js';
import { verifyCoverage, verifyReturnToExit } from '../algorithms/validation/coverage.js';
import { calculateMetrics } from '../algorithms/validation/metrics.js';
import { detectRoomConflicts } from '../algorithms/validation/conflicts.js';

export class MissionPlanner {
  async planMission(config: MissionConfig): Promise<MissionResult> {
    // Build graph
    const graph = new Graph();
    for (const node of config.building.nodes) {
      graph.addNode(node);
    }
    for (const edge of config.building.edges) {
      graph.addEdge(edge);
    }

    // Step 1: Allocate rooms to agents
    const allocation = await ilpAllocate(config.agents, config.building.rooms, config.redundantRooms);

    // Step 2: Generate routes for each agent
    const routes: Route[] = [];

    for (const agent of config.agents) {
      const assignedRooms = allocation.assignments.get(agent.id) || [];
      if (assignedRooms.length === 0) {
        // Agent has no assignments
        routes.push({
          agentId: agent.id,
          actions: [],
          roomsInspected: [],
          totalTime: 0,
          pathLength: 0,
          clearanceOperations: 0,
        });
        continue;
      }

      // Generate route for this agent
      const route = await this.generateRoute(agent.id, agent.startNode, assignedRooms, graph, config);
      routes.push(route);
    }

    // Step 3: Calculate metrics
    const metrics = calculateMetrics(routes, config.redundantRooms.length);

    // Step 4: Validate
    const coverage = verifyCoverage(config.building.rooms, routes, config.redundantRooms);
    const returnCheck = verifyReturnToExit(routes, config.building.exits, config.returnToExit);
    const conflicts = detectRoomConflicts(routes);

    const validation = {
      valid: coverage.allRoomsInspected && coverage.redundancySatisfied && returnCheck.allReturned && conflicts.noRoomConflicts,
      coverage: {
        allRoomsInspected: coverage.allRoomsInspected,
        missingRooms: coverage.missingRooms,
      },
      redundancy: {
        redundancySatisfied: coverage.redundancySatisfied,
        insufficientInspections: coverage.insufficientInspections,
      },
      conflicts,
      returnToExit: returnCheck,
      errors: [] as string[],
    };

    if (!validation.valid) {
      if (!coverage.allRoomsInspected) {
        validation.errors.push(`Missing room coverage: ${coverage.missingRooms.join(', ')}`);
      }
      if (!coverage.redundancySatisfied) {
        validation.errors.push(`Insufficient redundancy inspections`);
      }
      if (!conflicts.noRoomConflicts) {
        validation.errors.push(`Room conflicts detected: ${conflicts.conflictingActions.length} conflict(s)`);
      }
      if (!returnCheck.allReturned) {
        validation.errors.push(`Agents failed to return to exit: ${returnCheck.failedReturns.join(', ')}`);
      }
    }

    return {
      routes,
      makespan: metrics.makespan,
      metrics,
      validation,
    };
  }

  private async generateRoute(
    agentId: string,
    startNode: string,
    roomIds: string[],
    graph: Graph,
    config: MissionConfig
  ): Promise<Route> {
    const actions: Action[] = [];
    const roomsInspected: string[] = [];
    let currentNode = startNode;
    let currentTime = 0;
    let pathLength = 0;
    let clearanceOps = 0;

    // Visit each assigned room
    for (const roomId of roomIds) {
      const room = config.building.rooms.find((r) => r.id === roomId);
      if (!room) continue;

      // Find path to room door
      const pathToRoom = findShortestPath(graph, currentNode, room.doorNode);
      if (!pathToRoom.success) {
        continue;
      }

      // Add MOVE actions for each segment
      for (let i = 0; i < pathToRoom.path.length - 1; i++) {
        const from = pathToRoom.path[i];
        const to = pathToRoom.path[i + 1];

        const edge = graph.getAllEdges().find((e) =>
          (e.from === from && e.to === to) || (e.bidirectional !== false && e.from === to && e.to === from)
        );

        if (edge) {
          const travelTime = edge.baseTime;
          const clearTime = (!edge.cleared && edge.firstUseClearTime) ? edge.firstUseClearTime : 0;
          const duration = travelTime + clearTime;

          if (clearTime > 0) {
            edge.cleared = true;
            clearanceOps++;
          }

          actions.push({
            type: 'MOVE',
            startTime: currentTime,
            duration,
            endTime: currentTime + duration,
            location: to,
            edge: edge.id,
            clearedEdge: clearTime > 0,
          });

          currentTime += duration;
          pathLength += travelTime;
        }
      }

      currentNode = room.doorNode;

      // ENTER room
      const enterDuration = config.timeParameters.enterTime;
      actions.push({
        type: 'ENTER',
        startTime: currentTime,
        duration: enterDuration,
        endTime: currentTime + enterDuration,
        location: room.doorNode,
        targetRoom: room.id,
      });
      currentTime += enterDuration;

      // INSPECT room
      const inspectDuration = room.verifyTime;
      actions.push({
        type: 'INSPECT',
        startTime: currentTime,
        duration: inspectDuration,
        endTime: currentTime + inspectDuration,
        location: room.id,
        targetRoom: room.id,
      });
      currentTime += inspectDuration;
      roomsInspected.push(room.id);

      // EXIT room
      const exitDuration = config.timeParameters.exitTime;
      actions.push({
        type: 'EXIT_ROOM',
        startTime: currentTime,
        duration: exitDuration,
        endTime: currentTime + exitDuration,
        location: room.doorNode,
        targetRoom: room.id,
      });
      currentTime += exitDuration;
    }

    // Return to exit if required
    if (config.returnToExit && config.building.exits.length > 0) {
      // Find nearest exit
      let nearestExit = config.building.exits[0];
      let minDist = Infinity;

      for (const exit of config.building.exits) {
        const pathToExit = findShortestPath(graph, currentNode, exit);
        if (pathToExit.success && pathToExit.cost < minDist) {
          minDist = pathToExit.cost;
          nearestExit = exit;
        }
      }

      // Move to exit
      const pathToExit = findShortestPath(graph, currentNode, nearestExit);
      if (pathToExit.success) {
        for (let i = 0; i < pathToExit.path.length - 1; i++) {
          const from = pathToExit.path[i];
          const to = pathToExit.path[i + 1];

          const edge = graph.getAllEdges().find((e) =>
            (e.from === from && e.to === to) || (e.bidirectional !== false && e.from === to && e.to === from)
          );

          if (edge) {
            const travelTime = edge.baseTime;
            const clearTime = (!edge.cleared && edge.firstUseClearTime) ? edge.firstUseClearTime : 0;
            const duration = travelTime + clearTime;

            if (clearTime > 0) {
              edge.cleared = true;
              clearanceOps++;
            }

            actions.push({
              type: 'MOVE',
              startTime: currentTime,
              duration,
              endTime: currentTime + duration,
              location: to,
              edge: edge.id,
              clearedEdge: clearTime > 0,
            });

            currentTime += duration;
            pathLength += travelTime;
          }
        }
        currentNode = nearestExit;
      }
    }

    return {
      agentId,
      actions,
      roomsInspected,
      totalTime: currentTime,
      pathLength,
      clearanceOperations: clearanceOps,
    };
  }
}
