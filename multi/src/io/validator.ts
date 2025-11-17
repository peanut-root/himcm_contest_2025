// Input validator for building topology validation

import { Building } from '../models/building.js';
import { Graph } from '../models/graph.js';

export interface ValidationError {
  field: string;
  message: string;
}

export function validateBuildingTopology(building: Building): ValidationError[] {
  const errors: ValidationError[] = [];

  // Check unique node IDs
  const nodeIds = new Set<string>();
  for (const node of building.nodes) {
    if (nodeIds.has(node.id)) {
      errors.push({ field: 'nodes', message: `Duplicate node ID: ${node.id}` });
    }
    nodeIds.add(node.id);
  }

  // Check unique edge IDs
  const edgeIds = new Set<string>();
  for (const edge of building.edges) {
    if (edgeIds.has(edge.id)) {
      errors.push({ field: 'edges', message: `Duplicate edge ID: ${edge.id}` });
    }
    edgeIds.add(edge.id);

    // Validate edge references valid nodes
    if (!nodeIds.has(edge.from)) {
      errors.push({ field: `edges.${edge.id}`, message: `Edge references non-existent node: ${edge.from}` });
    }
    if (!nodeIds.has(edge.to)) {
      errors.push({ field: `edges.${edge.id}`, message: `Edge references non-existent node: ${edge.to}` });
    }

    // Check no self-loops
    if (edge.from === edge.to) {
      errors.push({ field: `edges.${edge.id}`, message: `Edge creates self-loop: ${edge.id}` });
    }
  }

  // Check unique room IDs
  const roomIds = new Set<string>();
  const doorNodes = new Set<string>();
  for (const room of building.rooms) {
    if (roomIds.has(room.id)) {
      errors.push({ field: 'rooms', message: `Duplicate room ID: ${room.id}` });
    }
    roomIds.add(room.id);

    // Validate room references valid door node
    if (!nodeIds.has(room.doorNode)) {
      errors.push({ field: `rooms.${room.id}`, message: `Room references non-existent door node: ${room.doorNode}` });
    } else {
      const node = building.nodes.find((n) => n.id === room.doorNode);
      if (node && node.kind !== 'DOOR') {
        errors.push({ field: `rooms.${room.id}`, message: `Room doorNode must reference a DOOR node, got: ${node.kind}` });
      }
    }

    // Check each door used only once
    if (doorNodes.has(room.doorNode)) {
      errors.push({ field: `rooms.${room.id}`, message: `Door node ${room.doorNode} used by multiple rooms` });
    }
    doorNodes.add(room.doorNode);
  }

  // Validate entrances/exits reference valid EXIT nodes
  for (const entrance of building.entrances) {
    if (!nodeIds.has(entrance)) {
      errors.push({ field: 'entrances', message: `Entrance references non-existent node: ${entrance}` });
    } else {
      const node = building.nodes.find((n) => n.id === entrance);
      if (node && node.kind !== 'EXIT') {
        errors.push({ field: 'entrances', message: `Entrance must reference EXIT node, got: ${node.kind}` });
      }
    }
  }

  for (const exit of building.exits) {
    if (!nodeIds.has(exit)) {
      errors.push({ field: 'exits', message: `Exit references non-existent node: ${exit}` });
    } else {
      const node = building.nodes.find((n) => n.id === exit);
      if (node && node.kind !== 'EXIT') {
        errors.push({ field: 'exits', message: `Exit must reference EXIT node, got: ${node.kind}` });
      }
    }
  }

  // Check graph connectivity (all rooms reachable from at least one entrance)
  if (errors.length === 0) {
    const graph = new Graph();
    building.nodes.forEach((node) => graph.addNode(node));
    building.edges.forEach((edge) => graph.addEdge(edge));

    for (const room of building.rooms) {
      let reachable = false;
      for (const entrance of building.entrances) {
        if (graph.hasPath(entrance, room.doorNode)) {
          reachable = true;
          break;
        }
      }
      if (!reachable) {
        errors.push({ field: `rooms.${room.id}`, message: `Room ${room.id} is unreachable from any entrance` });
      }
    }
  }

  return errors;
}
