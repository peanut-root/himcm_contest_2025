# Data Model - Web Demonstration Application

**Feature**: Web Demonstration Application
**Branch**: `002-web-demo`
**Date**: 2025-11-12
**Phase**: Phase 1 Design

---

## Overview

This document defines the data structures for the web demonstration application. The web app extends existing CLI models with UI-specific state while maintaining full compatibility with the CLI's JSON schema.

**Design Principle**: Reuse CLI models for core domain logic; create web-specific models only for UI state (canvas, animation, interaction).

---

## Model Categories

1. **Reused CLI Models** - Import directly from existing codebase
2. **Web View Models** - Extend CLI models with UI state
3. **Web-Only Models** - Canvas and animation state

---

## 1. Reused CLI Models

These models are imported from the existing TypeScript CLI codebase without modification.

### 1.1 Building Models

```typescript
// Imported from @models/building

interface Node {
  id: string;
  kind: 'CORRIDOR' | 'DOOR' | 'EXIT';
  x: number;
  y: number;
  label?: string;
}

interface Edge {
  id: string;
  from: string;
  to: string;
  baseTime: number;
  firstUseClearTime?: number;
  bidirectional: boolean;
}

interface Room {
  id: string;
  doorNode: string;
  verifyTime: number;
  redundancy?: boolean;
  label?: string;
}

interface Building {
  id: string;
  name: string;
  nodes: Node[];
  edges: Edge[];
  rooms: Room[];
}
```

**Validation Rules** (from existing validator):
- All node IDs must be unique
- All edge references must point to existing nodes
- All room doorNode references must point to existing DOOR nodes
- Node coordinates must be non-negative
- Time values must be positive

### 1.2 Mission Models

```typescript
// Imported from @models/mission

interface Agent {
  id: string;
  startNode: string;
  speed: number;
}

interface MissionConfig {
  buildingId: string;
  agentCount: number;
  startLocation: string;
  redundantRooms: string[];
  returnToExit: boolean;
  algorithm: 'ilp' | 'hungarian' | 'greedy';
}

interface Mission {
  id: string;
  building: Building;
  agents: Agent[];
  redundantRooms: string[];
  returnToExit: boolean;
}
```

### 1.3 Route Models

```typescript
// Imported from @models/route

type ActionType = 'MOVE' | 'ENTER' | 'INSPECT' | 'EXIT_ROOM' | 'RETURN';

interface AgentAction {
  type: ActionType;
  startTime: number;
  duration: number;
  endTime: number;
  location: string;
  targetRoom?: string;
  edge?: string;
  clearedEdge?: boolean;
}

interface Route {
  agentId: string;
  actions: AgentAction[];
  roomsInspected: string[];
  totalTime: number;
  pathLength: number;
  clearanceOperations: number;
}

interface OptimizationResults {
  missionId: string;
  makespan: number;
  routes: Route[];
  metrics: PerformanceMetrics;
  validation: ValidationResult;
}

interface PerformanceMetrics {
  makespan: number;
  individualTimes: Array<{ agentId: string; completionTime: number }>;
  totalPathLength: number;
  redundancyCoverage: {
    required: number;
    completed: number;
    rate: number;
  };
  clearanceEfficiency: {
    edgesCleared: number;
    totalEdgeTraversals: number;
    rate: number;
  };
  loadBalance: {
    mean: number;
    stdDev: number;
    maxDeviation: number;
  };
}
```

### 1.4 Validation Models

```typescript
// Imported from @algorithms/validation

interface ValidationResult {
  valid: boolean;
  coverage: {
    allRoomsInspected: boolean;
    missingRooms: string[];
  };
  redundancy: {
    redundancySatisfied: boolean;
    insufficientInspections: string[];
  };
  conflicts: {
    noRoomConflicts: boolean;
    conflictingActions: Array<{
      room: string;
      time: number;
      agents: string[];
    }>;
  };
  returnToExit: {
    allReturned: boolean;
    failedReturns: string[];
  };
  errors: string[];
}
```

---

## 2. Web View Models

These models extend CLI models with UI-specific properties for rendering and interaction.

### 2.1 Visual Node

Extends Node with rendering state:

```typescript
interface VisualNode extends Node {
  // UI state
  selected: boolean;
  hovered: boolean;
  dragging: boolean;

  // Visual properties
  renderX: number;  // Screen coordinates (after zoom/pan)
  renderY: number;
  radius: number;
  fillColor: string;
  strokeColor: string;

  // Konva reference
  shape?: Konva.Circle | Konva.Rect;
}

// Node color mapping
const NodeColors = {
  EXIT: '#4caf50',      // Green
  CORRIDOR: '#2196f3',  // Blue
  DOOR: '#ff9800'       // Orange
} as const;
```

**State Transitions**:
- `selected = true` when clicked
- `hovered = true` when mouse enters
- `dragging = true` during drag operation
- Colors change based on state (e.g., darker on hover)

### 2.2 Visual Edge

Extends Edge with rendering state:

```typescript
interface VisualEdge extends Edge {
  // UI state
  selected: boolean;
  hovered: boolean;
  highlighted: boolean;  // Part of active route

  // Visual properties
  strokeColor: string;
  strokeWidth: number;
  opacity: number;

  // Konva reference
  line?: Konva.Line;
  arrow?: Konva.Arrow;

  // Layout
  midpoint: { x: number; y: number };  // For label placement
}

// Edge visualization states
const EdgeStates = {
  NORMAL: { color: '#757575', width: 2, opacity: 0.6 },
  SELECTED: { color: '#2196f3', width: 3, opacity: 1.0 },
  HIGHLIGHTED: { color: '#f44336', width: 3, opacity: 1.0 },
  CLEARED: { color: '#4caf50', width: 2, opacity: 0.8 }
} as const;
```

### 2.3 Visual Room

Extends Room with inspection state:

```typescript
interface VisualRoom extends Room {
  // UI state
  inspectionState: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
  inspectedBy: string[];  // Agent IDs
  hasConflict: boolean;

  // Visual properties
  fillColor: string;
  strokeColor: string;
  labelVisible: boolean;

  // Associated visual elements
  doorVisualNode?: VisualNode;
  boundingBox?: { x: number; y: number; width: number; height: number };
}

// Room state colors
const RoomStateColors = {
  PENDING: '#ffd54f',       // Yellow
  IN_PROGRESS: '#29b6f6',   // Light blue
  COMPLETED: '#66bb6a',     // Green
  CONFLICT: '#f44336'       // Red
} as const;
```

---

## 3. Web-Only Models

These models exist only in the web application for UI state management.

### 3.1 Canvas State

Manages the building canvas viewport and interaction mode:

```typescript
interface CanvasState {
  // Viewport
  zoom: number;           // 0.1 to 3.0
  panX: number;
  panY: number;

  // Dimensions
  width: number;
  height: number;

  // Interaction mode
  mode: DrawingMode;

  // Selection
  selectedNodes: string[];
  selectedEdges: string[];
  selectedRooms: string[];

  // Grid
  gridVisible: boolean;
  gridSize: number;
  snapToGrid: boolean;

  // Temporary state during editing
  pendingEdge?: {
    fromNode: string;
    toX: number;
    toY: number;
  };
}

type DrawingMode =
  | 'SELECT'      // Default: select and move elements
  | 'ADD_EXIT'    // Click to add exit node
  | 'ADD_CORRIDOR'// Click to add corridor node
  | 'ADD_DOOR'    // Click to add door node
  | 'ADD_EDGE'    // Click two nodes to connect
  | 'DELETE'      // Click to delete element
  | 'PAN';        // Drag to pan canvas
```

**State Transitions**:
- Toolbar buttons set `mode`
- Mouse events update `selectedNodes`/`selectedEdges`/`selectedRooms`
- Zoom gestures update `zoom`, pan drags update `panX`/`panY`

### 3.2 Animation State

Manages route playback and visualization:

```typescript
interface AnimationState {
  // Playback control
  isPlaying: boolean;
  isPaused: boolean;
  currentTime: number;      // Milliseconds from start
  duration: number;         // Total animation duration
  speed: number;            // 0.1 to 3.0 (playback rate)

  // Loop control
  loop: boolean;

  // Timeline
  timelineVisible: boolean;
  timelineHeight: number;

  // Agent visualization
  agents: AnimatedAgent[];

  // Active highlights
  activeRooms: Set<string>;     // Currently being inspected
  activeEdges: Set<string>;     // Currently being traversed

  // Conflict display
  showConflicts: boolean;
  conflictMarkers: ConflictMarker[];
}

interface AnimatedAgent {
  id: string;

  // Current state
  currentAction: AgentAction | null;
  currentPosition: { x: number; y: number };

  // Visual properties
  color: string;
  radius: number;

  // Konva reference
  shape?: Konva.Circle;
  label?: Konva.Text;

  // Route data
  route: Route;
  actionIndex: number;
}

interface ConflictMarker {
  room: string;
  time: number;
  agents: string[];
  position: { x: number; y: number };
  visible: boolean;
}

// Agent colors (distinct for visualization)
const AgentColors = [
  '#f44336', // Red
  '#2196f3', // Blue
  '#4caf50', // Green
  '#ff9800', // Orange
  '#9c27b0', // Purple
  '#00bcd4', // Cyan
  '#ffeb3b', // Yellow
  '#795548', // Brown
  '#607d8b', // Blue Grey
  '#e91e63'  // Pink
] as const;
```

**State Transitions**:
- `play()` sets `isPlaying = true`, starts GSAP timeline
- `pause()` sets `isPaused = true`, pauses GSAP timeline
- `scrub(time)` updates `currentTime`, seeks GSAP timeline
- Animation frame updates `currentPosition` for each agent

### 3.3 UI State

Global UI state for panels, modals, and active views:

```typescript
interface UIState {
  // Active view
  activeView: 'EDITOR' | 'ANIMATOR' | 'RESULTS';

  // Panel visibility
  panels: {
    properties: boolean;
    metrics: boolean;
    validation: boolean;
    scenarios: boolean;
    timeline: boolean;
  };

  // Modal state
  activeModal: 'NONE' | 'MISSION_CONFIG' | 'EXPORT' | 'IMPORT' | 'SAVE_SCENARIO' | 'LOAD_SCENARIO';

  // Mission configuration (temporary during config)
  missionForm?: Partial<MissionConfig>;

  // Notifications
  notifications: Notification[];

  // Loading state
  isOptimizing: boolean;
  optimizationProgress?: number;
}

interface Notification {
  id: string;
  type: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR';
  message: string;
  timestamp: number;
  dismissible: boolean;
}
```

### 3.4 Scenario Model

Saved scenarios for LocalStorage persistence:

```typescript
interface SavedScenario {
  id: string;
  name: string;
  description?: string;
  createdAt: number;
  updatedAt: number;

  // Saved data
  building: Building;
  missionConfig?: MissionConfig;
  results?: OptimizationResults;

  // Metadata
  isExample: boolean;
  tags: string[];
}

// Example scenarios (pre-loaded)
const ExampleScenarios = {
  BASIC: 'basic-6-room',
  REDUNDANCY: 'redundancy-scenario',
  RETURN: 'return-to-exit-scenario',
  MULTI_AGENT: 'multi-agent-scenario'
} as const;
```

---

## 4. Coordinate Systems

The web app uses two coordinate systems:

### 4.1 Graph Coordinates

- **Definition**: Abstract coordinates from Building JSON (node.x, node.y)
- **Range**: Unbounded (typically 0-1000 for example buildings)
- **Usage**: Stored in JSON, used for pathfinding distances

### 4.2 Screen Coordinates

- **Definition**: Pixel coordinates on HTML canvas element
- **Range**: 0 to canvas width/height
- **Usage**: Rendering, mouse events, Konva shapes

### 4.3 Coordinate Conversion

```typescript
class CoordinateMapper {
  constructor(
    private canvasState: CanvasState,
    private graphBounds: { minX: number; minY: number; maxX: number; maxY: number }
  ) {}

  // Graph → Screen
  toScreen(graphX: number, graphY: number): { x: number; y: number } {
    const scale = this.calculateScale();
    return {
      x: (graphX - this.graphBounds.minX) * scale * this.canvasState.zoom + this.canvasState.panX,
      y: (graphY - this.graphBounds.minY) * scale * this.canvasState.zoom + this.canvasState.panY
    };
  }

  // Screen → Graph
  toGraph(screenX: number, screenY: number): { x: number; y: number } {
    const scale = this.calculateScale();
    return {
      x: (screenX - this.canvasState.panX) / (scale * this.canvasState.zoom) + this.graphBounds.minX,
      y: (screenY - this.canvasState.panY) / (scale * this.canvasState.zoom) + this.graphBounds.minY
    };
  }

  private calculateScale(): number {
    const graphWidth = this.graphBounds.maxX - this.graphBounds.minX;
    const graphHeight = this.graphBounds.maxY - this.graphBounds.minY;
    const padding = 50; // pixels

    const scaleX = (this.canvasState.width - 2 * padding) / graphWidth;
    const scaleY = (this.canvasState.height - 2 * padding) / graphHeight;

    return Math.min(scaleX, scaleY);
  }
}
```

---

## 5. State Management

The web app uses a simple centralized state pattern (no external state library needed):

```typescript
class AppState {
  // Core state
  building: Building | null = null;
  missionConfig: MissionConfig | null = null;
  results: OptimizationResults | null = null;

  // UI state
  canvas: CanvasState;
  animation: AnimationState;
  ui: UIState;

  // Scenarios
  scenarios: SavedScenario[] = [];

  // Observers (for reactive updates)
  private observers: Array<(state: AppState) => void> = [];

  subscribe(callback: (state: AppState) => void): () => void {
    this.observers.push(callback);
    return () => {
      const index = this.observers.indexOf(callback);
      if (index > -1) this.observers.splice(index, 1);
    };
  }

  private notify() {
    this.observers.forEach(callback => callback(this));
  }

  // State updates
  updateBuilding(building: Building) {
    this.building = building;
    this.notify();
  }

  updateCanvasState(updates: Partial<CanvasState>) {
    this.canvas = { ...this.canvas, ...updates };
    this.notify();
  }

  // ... other update methods
}

// Singleton instance
export const appState = new AppState();
```

---

## 6. Validation Rules

All data must satisfy both CLI validation rules and web-specific constraints:

### 6.1 Building Validation

From existing CLI validator:
- ✅ All node IDs unique
- ✅ All edge references valid
- ✅ All room door references valid
- ✅ Graph is connected (BFS reachability)
- ✅ At least one EXIT node
- ✅ Positive time values

Web-specific additions:
- ✅ Node coordinates within canvas bounds (0 to 10000)
- ✅ No overlapping nodes (minimum distance 20 units)
- ✅ Edge length reasonable (maximum 1000 units)

### 6.2 Mission Validation

- ✅ Agent count > 0
- ✅ Start location is valid EXIT or CORRIDOR node
- ✅ Redundant rooms exist in building
- ✅ All rooms reachable from start location

### 6.3 UI State Validation

- ✅ Zoom within bounds (0.1 to 3.0)
- ✅ Animation speed within bounds (0.1 to 3.0)
- ✅ Selected element IDs exist
- ✅ Current time ≤ duration

---

## 7. Data Flow

### 7.1 Building Editor Flow

1. User clicks "Add Node" → Updates `CanvasState.mode`
2. User clicks canvas → Creates `VisualNode`, adds to `Building.nodes`
3. User drags node → Updates `VisualNode.renderX/Y`, updates `Node.x/y`
4. User clicks "Validate" → Calls `validateBuilding()` → Updates `UIState.notifications`
5. User clicks "Export" → Serializes `Building` to JSON → Downloads file

### 7.2 Optimization Flow

1. User clicks "Configure Mission" → Shows mission modal, initializes `UIState.missionForm`
2. User fills form → Updates `MissionConfig`
3. User clicks "Optimize" → Sets `UIState.isOptimizing = true`
4. Calls `MissionPlanner.plan()` with building and config
5. Receives `OptimizationResults` → Updates `appState.results`
6. Transitions to animation view → Initializes `AnimationState`

### 7.3 Animation Flow

1. Load `OptimizationResults` → Create `AnimatedAgent[]` from routes
2. Build GSAP timeline from agent actions
3. User clicks "Play" → Sets `AnimationState.isPlaying = true`, starts timeline
4. Animation frame updates → Updates `AnimatedAgent.currentPosition`
5. Render agents on canvas using `Konva.Circle`
6. Update room colors based on `inspectionState`
7. Show conflicts when detected

---

## 8. Persistence

### 8.1 LocalStorage Schema

```typescript
// Key format: himcm:scenario:{id}
interface StorageSchema {
  scenarios: Record<string, SavedScenario>;
  settings: {
    lastOpenedScenario?: string;
    defaultAlgorithm: 'ilp' | 'hungarian' | 'greedy';
    animationSpeed: number;
  };
}

class StorageService {
  private readonly PREFIX = 'himcm:';

  saveScenario(scenario: SavedScenario): void {
    const key = `${this.PREFIX}scenario:${scenario.id}`;
    localStorage.setItem(key, JSON.stringify(scenario));
  }

  loadScenario(id: string): SavedScenario | null {
    const key = `${this.PREFIX}scenario:${id}`;
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : null;
  }

  listScenarios(): SavedScenario[] {
    const scenarios: SavedScenario[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith(`${this.PREFIX}scenario:`)) {
        const data = localStorage.getItem(key);
        if (data) scenarios.push(JSON.parse(data));
      }
    }
    return scenarios.sort((a, b) => b.updatedAt - a.updatedAt);
  }
}
```

---

## Summary

**Model Categories**:
1. **Reused CLI Models** (11 interfaces): Building, Node, Edge, Room, Mission, Agent, Route, etc.
2. **Web View Models** (3 interfaces): VisualNode, VisualEdge, VisualRoom
3. **Web-Only Models** (6 interfaces): CanvasState, AnimationState, AnimatedAgent, UIState, SavedScenario, ConflictMarker

**Design Benefits**:
- ✅ Maintains CLI compatibility (imports existing types)
- ✅ Separation of concerns (domain logic vs. UI state)
- ✅ Type safety throughout (TypeScript strict mode)
- ✅ Clear state management (centralized AppState)
- ✅ Efficient rendering (visual state cached in UI models)

**Next Step**: Define API contracts for service layer interactions.
