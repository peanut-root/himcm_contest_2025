// Shortest path utilities using A*

import { Graph } from '../../models/graph.js';
import { astar } from './astar.js';

export interface PathResult {
  path: string[];
  cost: number;
  success: boolean;
}

export function findShortestPath(graph: Graph, from: string, to: string): PathResult {
  const result = astar(graph, from, to);

  if (result) {
    return {
      path: result.path,
      cost: result.cost,
      success: true,
    };
  }

  return {
    path: [],
    cost: Infinity,
    success: false,
  };
}

export function findNearestExit(graph: Graph, fromNode: string, exits: string[]): PathResult {
  let bestPath: PathResult = {
    path: [],
    cost: Infinity,
    success: false,
  };

  for (const exit of exits) {
    const path = findShortestPath(graph, fromNode, exit);
    if (path.success && path.cost < bestPath.cost) {
      bestPath = path;
    }
  }

  return bestPath;
}

export function calculatePathCost(graph: Graph, path: string[]): number {
  let totalCost = 0;

  for (let i = 0; i < path.length - 1; i++) {
    const from = path[i];
    const to = path[i + 1];

    const graphInstance = graph.getGraphInstance();
    const edge = graphInstance.edge(from, to);

    if (edge) {
      const weight = graphInstance.getEdgeAttribute(edge, 'weight') as number;
      totalCost += weight;
    }
  }

  return totalCost;
}
