// Building model - Building structure with rooms

import { Node, Edge } from './graph.js';

export interface Room {
  id: string;
  doorNode: string;
  verifyTime: number;
  redundancy?: boolean;
  label?: string;
}

export interface Building {
  id: string;
  nodes: Node[];
  edges: Edge[];
  rooms: Room[];
  entrances: string[];
  exits: string[];
  metadata?: {
    name?: string;
    description?: string;
    floor?: number;
    dimensions?: {
      width: number;
      height: number;
    };
  };
}
