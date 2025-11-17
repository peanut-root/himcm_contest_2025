// Graph model - Nodes and Edges for building representation

export interface Node {
  id: string;
  kind: 'CORRIDOR' | 'DOOR' | 'EXIT';
  x: number;
  y: number;
  label?: string;
}

export interface Edge {
  id: string;
  from: string;
  to: string;
  baseTime: number;
  firstUseClearTime?: number;
  cleared?: boolean;
  bidirectional?: boolean;
}

// Dynamic edge weight calculation
export function getEdgeWeight(edge: Edge): number {
  return edge.baseTime + (edge.cleared ? 0 : edge.firstUseClearTime || 0);
}

// Graph class wrapper around graphology
import { UndirectedGraph } from 'graphology';

export class Graph {
  private graph: typeof UndirectedGraph.prototype;
  private edgeMap: Map<string, Edge>;

  constructor() {
    this.graph = new UndirectedGraph();
    this.edgeMap = new Map();
  }

  addNode(node: Node): void {
    this.graph.addNode(node.id, { ...node });
  }

  addEdge(edge: Edge): void {
    this.edgeMap.set(edge.id, edge);

    if (edge.bidirectional !== false) {
      // Bidirectional edge (default)
      this.graph.addEdge(edge.from, edge.to, {
        ...edge,
        weight: getEdgeWeight(edge),
      });
    } else {
      // Unidirectional edge
      this.graph.addDirectedEdge(edge.from, edge.to, {
        ...edge,
        weight: getEdgeWeight(edge),
      });
    }
  }

  getNode(id: string): Node | undefined {
    if (!this.graph.hasNode(id)) return undefined;
    return this.graph.getNodeAttributes(id) as Node;
  }

  getEdge(id: string): Edge | undefined {
    return this.edgeMap.get(id);
  }

  updateEdgeWeight(edgeId: string): void {
    const edge = this.edgeMap.get(edgeId);
    if (!edge) return;

    // Update weight in graph
    const graphEdge = this.graph.edge(edge.from, edge.to);
    if (graphEdge) {
      this.graph.setEdgeAttribute(graphEdge, 'weight', getEdgeWeight(edge));
    }
  }

  getNeighbors(nodeId: string): string[] {
    return this.graph.neighbors(nodeId);
  }

  hasPath(from: string, to: string): boolean {
    // Simple BFS to check connectivity
    if (!this.graph.hasNode(from) || !this.graph.hasNode(to)) return false;
    if (from === to) return true;

    const visited = new Set<string>();
    const queue = [from];
    visited.add(from);

    while (queue.length > 0) {
      const current = queue.shift()!;
      if (current === to) return true;

      for (const neighbor of this.getNeighbors(current)) {
        if (!visited.has(neighbor)) {
          visited.add(neighbor);
          queue.push(neighbor);
        }
      }
    }

    return false;
  }

  getAllNodes(): Node[] {
    return this.graph.nodes().map((id: string) => this.getNode(id)!);
  }

  getAllEdges(): Edge[] {
    return Array.from(this.edgeMap.values());
  }

  getGraphInstance() {
    return this.graph;
  }
}
