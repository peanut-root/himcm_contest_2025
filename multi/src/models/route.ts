// Route model - Action sequences and routes for agents

export type ActionType = 'MOVE' | 'CLEAR' | 'ENTER' | 'INSPECT' | 'EXIT_ROOM' | 'WAIT';

export interface Action {
  type: ActionType;
  startTime: number;
  duration: number;
  endTime: number;
  location: string;
  targetRoom?: string;
  edge?: string;
  clearedEdge?: boolean;
  waitReason?: string;
}

export interface Route {
  agentId: string;
  actions: Action[];
  roomsInspected: string[];
  totalTime: number;
  pathLength: number;
  clearanceOperations: number;
}
