// A* pathfinding algorithm with dynamic edge weight support

import { Graph } from '../../models/graph.js';

interface AStarNode {
  id: string;
  g: number; // Cost from start
  h: number; // Heuristic to goal
  f: number; // Total cost (g + h)
  parent: string | null;
}

function euclideanDistance(x1: number, y1: number, x2: number, y2: number): number {
  return Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
}

export function astar(
  graph: Graph,
  startId: string,
  goalId: string
): { path: string[]; cost: number } | null {
  const startNode = graph.getNode(startId);
  const goalNode = graph.getNode(goalId);

  if (!startNode || !goalNode) {
    return null;
  }

  const openSet = new Map<string, AStarNode>();
  const closedSet = new Map<string, AStarNode>();

  // Initialize start node
  const heuristic = euclideanDistance(startNode.x, startNode.y, goalNode.x, goalNode.y);
  openSet.set(startId, {
    id: startId,
    g: 0,
    h: heuristic,
    f: heuristic,
    parent: null,
  });

  while (openSet.size > 0) {
    // Find node with lowest f score
    let current: AStarNode | null = null;
    let lowestF = Infinity;

    for (const node of openSet.values()) {
      if (node.f < lowestF) {
        lowestF = node.f;
        current = node;
      }
    }

    if (!current) break;

    // Goal reached
    if (current.id === goalId) {
      return reconstructPath(current, openSet, closedSet);
    }

    openSet.delete(current.id);
    closedSet.set(current.id, current);

    // Explore neighbors
    const neighbors = graph.getNeighbors(current.id);
    for (const neighborId of neighbors) {
      if (closedSet.has(neighborId)) continue;

      const neighborNode = graph.getNode(neighborId);
      if (!neighborNode) continue;

      // Calculate edge weight (dynamic based on clearance state)
      const graphInstance = graph.getGraphInstance();
      const edge = graphInstance.edge(current.id, neighborId);
      if (!edge) continue;

      const edgeWeight = graphInstance.getEdgeAttribute(edge, 'weight') as number;
      const tentativeG = current.g + edgeWeight;

      const existingNeighbor = openSet.get(neighborId);
      if (existingNeighbor && tentativeG >= existingNeighbor.g) {
        continue; // Not a better path
      }

      // This is the best path so far
      const h = euclideanDistance(neighborNode.x, neighborNode.y, goalNode.x, goalNode.y);
      openSet.set(neighborId, {
        id: neighborId,
        g: tentativeG,
        h,
        f: tentativeG + h,
        parent: current.id,
      });
    }
  }

  return null; // No path found
}

function reconstructPath(
  current: AStarNode,
  openSet: Map<string, AStarNode>,
  closedSet: Map<string, AStarNode>
): { path: string[]; cost: number } {
  const path: string[] = [];
  let node: AStarNode | undefined = current;

  // Build path from goal to start
  while (node) {
    path.unshift(node.id);
    if (node.parent === null) break;

    // Find parent in closed set or open set
    const parentInClosed = closedSet.get(node.parent);
    const parentInOpen = openSet.get(node.parent);
    node = parentInClosed || parentInOpen;
  }

  return { path, cost: current.g };
}
