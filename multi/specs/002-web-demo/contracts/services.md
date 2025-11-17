# Service Layer Contracts - Web Demonstration Application

**Feature**: Web Demonstration Application
**Branch**: `002-web-demo`
**Date**: 2025-11-12
**Phase**: Phase 1 Design

---

## Overview

This document defines the contracts (interfaces) for all service layer components in the web application. Services encapsulate business logic and provide a clean API between UI components and the underlying CLI algorithms.

**Design Principle**: Services are stateless facades that delegate to existing CLI functions. They do not duplicate business logic.

---

## 1. BuildingService

Manages building creation, editing, validation, and persistence.

### Interface

```typescript
interface IBuildingService {
  // Creation
  createEmptyBuilding(name: string): Building;
  loadFromJSON(json: string): Promise<Building>;
  importFromFile(file: File): Promise<Building>;

  // Node operations
  addNode(building: Building, node: Omit<Node, 'id'>): Node;
  updateNode(building: Building, nodeId: string, updates: Partial<Node>): Node;
  deleteNode(building: Building, nodeId: string): void;
  moveNode(building: Building, nodeId: string, x: number, y: number): void;

  // Edge operations
  addEdge(building: Building, edge: Omit<Edge, 'id'>): Edge;
  updateEdge(building: Building, edgeId: string, updates: Partial<Edge>): Edge;
  deleteEdge(building: Building, edgeId: string): void;

  // Room operations
  addRoom(building: Building, room: Omit<Room, 'id'>): Room;
  updateRoom(building: Building, roomId: string, updates: Partial<Room>): Room;
  deleteRoom(building: Building, roomId: string): void;

  // Validation
  validate(building: Building): ValidationResult;
  checkConnectivity(building: Building): { connected: boolean; unreachableNodes: string[] };

  // Export
  exportToJSON(building: Building): string;
  exportToFile(building: Building, filename: string): void;

  // Utilities
  calculateBounds(building: Building): { minX: number; minY: number; maxX: number; maxY: number };
  findNode(building: Building, id: string): Node | undefined;
  findEdge(building: Building, id: string): Edge | undefined;
  findRoom(building: Building, id: string): Room | undefined;
  getEdgesForNode(building: Building, nodeId: string): Edge[];
  getRoomForDoor(building: Building, doorNodeId: string): Room | undefined;
}
```

### Example Usage

```typescript
const buildingService = new BuildingService();

// Create new building
const building = buildingService.createEmptyBuilding('Office Building');

// Add nodes
const exit = buildingService.addNode(building, {
  kind: 'EXIT',
  x: 100,
  y: 100,
  label: 'Main Entrance'
});

const corridor = buildingService.addNode(building, {
  kind: 'CORRIDOR',
  x: 200,
  y: 100
});

// Connect with edge
const edge = buildingService.addEdge(building, {
  from: exit.id,
  to: corridor.id,
  baseTime: 10,
  bidirectional: true
});

// Validate
const validation = buildingService.validate(building);
if (!validation.valid) {
  console.error('Validation errors:', validation.errors);
}

// Export
const json = buildingService.exportToJSON(building);
```

### Implementation Notes

- **ID Generation**: Use `crypto.randomUUID()` for unique IDs
- **Validation**: Delegates to existing `validateBuilding()` from `@/io/validator`
- **Connectivity**: Uses BFS on graphology graph
- **Export**: JSON.stringify with pretty printing (2-space indent)

---

## 2. OptimizationService

Triggers route optimization using existing CLI planner.

### Interface

```typescript
interface IOptimizationService {
  // Optimization
  optimize(config: OptimizationRequest): Promise<OptimizationResults>;
  cancel(): void;

  // Algorithm selection
  setAlgorithm(algorithm: 'ilp' | 'hungarian' | 'greedy'): void;
  compareAlgorithms(config: OptimizationRequest): Promise<AlgorithmComparison>;

  // Utilities
  estimateDuration(building: Building, agentCount: number): number;
  checkFeasibility(config: OptimizationRequest): FeasibilityCheck;
}

interface OptimizationRequest {
  building: Building;
  agentCount: number;
  startLocation: string;
  redundantRooms: string[];
  returnToExit: boolean;
  algorithm?: 'ilp' | 'hungarian' | 'greedy';
}

interface AlgorithmComparison {
  ilp: OptimizationResults | { error: string };
  hungarian: OptimizationResults;
  greedy: OptimizationResults;
  executionTimes: {
    ilp: number;
    hungarian: number;
    greedy: number;
  };
}

interface FeasibilityCheck {
  feasible: boolean;
  issues: string[];
  warnings: string[];
}
```

### Example Usage

```typescript
const optimizationService = new OptimizationService();

// Configure mission
const request: OptimizationRequest = {
  building,
  agentCount: 2,
  startLocation: 'exit-1',
  redundantRooms: ['R1', 'R6'],
  returnToExit: true,
  algorithm: 'ilp'
};

// Check feasibility first
const feasibility = optimizationService.checkFeasibility(request);
if (!feasibility.feasible) {
  console.error('Optimization not feasible:', feasibility.issues);
  return;
}

// Run optimization
try {
  const results = await optimizationService.optimize(request);
  console.log('Makespan:', results.makespan);
  console.log('Routes:', results.routes);
} catch (error) {
  console.error('Optimization failed:', error);
}
```

### Implementation Notes

- **Delegates to CLI**: Calls `MissionPlanner.plan()` from `@/simulation/planner`
- **Async Execution**: Wraps synchronous planner in `Promise` for UI responsiveness
- **Progress Updates**: Could emit progress events for long-running optimizations
- **Cancellation**: Sets flag that planner checks periodically
- **Fallback**: If ILP fails, automatically tries Hungarian, then Greedy

---

## 3. ValidationService

Validates buildings, missions, and results.

### Interface

```typescript
interface IValidationService {
  // Building validation
  validateBuilding(building: Building): BuildingValidation;
  validateTopology(building: Building): TopologyValidation;
  validateReachability(building: Building, fromNode: string): ReachabilityValidation;

  // Mission validation
  validateMissionConfig(config: MissionConfig, building: Building): MissionValidation;

  // Results validation
  validateResults(results: OptimizationResults, mission: Mission): ResultsValidation;

  // Real-time validation (for editor)
  validateNodePlacement(building: Building, x: number, y: number): PlacementValidation;
  validateEdgeCreation(building: Building, fromId: string, toId: string): EdgeValidation;
}

interface BuildingValidation {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

interface ValidationError {
  code: string;
  message: string;
  context?: any;
}

interface ValidationWarning {
  code: string;
  message: string;
  suggestion?: string;
}

interface TopologyValidation {
  connected: boolean;
  components: string[][];  // Connected components
  isolatedNodes: string[];
  missingExits: boolean;
}

interface ReachabilityValidation {
  allReachable: boolean;
  reachableNodes: string[];
  unreachableNodes: string[];
}

interface MissionValidation {
  valid: boolean;
  errors: ValidationError[];
  agentCountOk: boolean;
  startLocationValid: boolean;
  redundantRoomsValid: boolean;
  allRoomsReachable: boolean;
}

interface ResultsValidation extends ValidationResult {
  // Extends CLI ValidationResult
  performanceOk: boolean;
  efficiencyScore: number;  // 0-100
}

interface PlacementValidation {
  valid: boolean;
  reason?: string;
  tooCloseToNode?: string;
  outOfBounds?: boolean;
}

interface EdgeValidation {
  valid: boolean;
  reason?: string;
  createsDisconnectedGraph?: boolean;
  duplicateEdge?: boolean;
}
```

### Example Usage

```typescript
const validationService = new ValidationService();

// Validate building
const buildingValidation = validationService.validateBuilding(building);
if (!buildingValidation.valid) {
  buildingValidation.errors.forEach(error => {
    console.error(`[${error.code}] ${error.message}`);
  });
}

// Real-time validation during editing
const placement = validationService.validateNodePlacement(building, mouseX, mouseY);
if (!placement.valid) {
  showTooltip(placement.reason);
}

// Validate mission before optimization
const missionValidation = validationService.validateMissionConfig(config, building);
if (!missionValidation.valid) {
  showErrorDialog(missionValidation.errors);
}
```

### Implementation Notes

- **Delegates to CLI**: Uses `validateBuilding()` from `@/io/validator` and `validateCoverage()` from `@/algorithms/validation/coverage`
- **Real-time Validation**: Lightweight checks for immediate UI feedback
- **Error Codes**: Standardized codes for i18n and testing (e.g., `NODE_TOO_CLOSE`, `EDGE_DUPLICATE`)
- **Suggestions**: Actionable suggestions for fixing validation errors

---

## 4. StorageService

Manages scenario persistence in browser LocalStorage.

### Interface

```typescript
interface IStorageService {
  // Scenario management
  saveScenario(scenario: SavedScenario): Promise<void>;
  loadScenario(id: string): Promise<SavedScenario | null>;
  deleteScenario(id: string): Promise<void>;
  listScenarios(): Promise<SavedScenario[]>;
  scenarioExists(id: string): Promise<boolean>;

  // Settings
  saveSettings(settings: AppSettings): Promise<void>;
  loadSettings(): Promise<AppSettings>;

  // Utilities
  getStorageUsage(): Promise<StorageUsage>;
  clearAll(): Promise<void>;
  exportAllScenarios(): Promise<string>;  // JSON export
  importScenarios(json: string): Promise<number>;  // Returns count imported
}

interface AppSettings {
  lastOpenedScenario?: string;
  defaultAlgorithm: 'ilp' | 'hungarian' | 'greedy';
  animationSpeed: number;
  gridVisible: boolean;
  snapToGrid: boolean;
  theme: 'light' | 'dark';
}

interface StorageUsage {
  used: number;      // Bytes
  available: number; // Bytes (typically ~5-10MB for LocalStorage)
  percentage: number;
  scenarios: Array<{
    id: string;
    name: string;
    size: number;
  }>;
}
```

### Example Usage

```typescript
const storageService = new StorageService();

// Save current scenario
const scenario: SavedScenario = {
  id: crypto.randomUUID(),
  name: 'My Office Building',
  description: 'Test scenario with 6 rooms',
  createdAt: Date.now(),
  updatedAt: Date.now(),
  building,
  missionConfig,
  results,
  isExample: false,
  tags: ['office', 'test']
};

await storageService.saveScenario(scenario);

// Load saved scenarios
const scenarios = await storageService.listScenarios();
scenarios.forEach(s => {
  console.log(`${s.name} (${new Date(s.updatedAt).toLocaleDateString()})`);
});

// Check storage usage
const usage = await storageService.getStorageUsage();
console.log(`Storage: ${usage.used / 1024}KB / ${usage.available / 1024}KB (${usage.percentage}%)`);
```

### Implementation Notes

- **Async API**: Uses `Promise` for consistency, even though LocalStorage is synchronous
- **Key Prefix**: All keys prefixed with `himcm:` to avoid conflicts
- **Serialization**: JSON.stringify for storage, JSON.parse for retrieval
- **Error Handling**: Catches `QuotaExceededError` and provides helpful message
- **Compression**: Could use LZ-string library to compress large scenarios

---

## 5. ExampleService

Loads pre-configured example scenarios.

### Interface

```typescript
interface IExampleService {
  // List examples
  listExamples(): ExampleScenario[];
  getExample(id: string): ExampleScenario | undefined;

  // Load example data
  loadExample(id: string): Promise<SavedScenario>;

  // Categories
  getExamplesByCategory(category: string): ExampleScenario[];
  getCategories(): string[];
}

interface ExampleScenario {
  id: string;
  name: string;
  description: string;
  category: 'basic' | 'advanced' | 'optimization' | 'special';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  thumbnail?: string;  // Base64 or URL
  features: string[];  // ['redundancy', 'return-to-exit', 'multiple-agents']
}
```

### Example Usage

```typescript
const exampleService = new ExampleService();

// List all examples
const examples = exampleService.listExamples();
examples.forEach(ex => {
  console.log(`${ex.name} [${ex.difficulty}] - ${ex.description}`);
});

// Load specific example
const scenario = await exampleService.loadExample('basic-6-room');
console.log('Loaded building:', scenario.building.name);

// Filter by category
const basicExamples = exampleService.getExamplesByCategory('basic');
```

### Implementation Notes

- **Static Data**: Examples are bundled JSON files in `web/assets/examples/`
- **Lazy Loading**: Uses dynamic `import()` to load JSON on demand
- **Predefined Examples**: Must match CLI example files
  - `basic-6-room.json` - Simple office building
  - `redundancy-scenario.json` - Demonstrates redundant room inspection
  - `return-to-exit-scenario.json` - Agents return to exit
  - `multi-agent-scenario.json` - Large facility with 10 rooms, 5 agents

---

## 6. AnimationService

Manages animation playback using GSAP timelines.

### Interface

```typescript
interface IAnimationService {
  // Lifecycle
  initialize(results: OptimizationResults, canvas: BuildingCanvas): AnimatedAgents;
  dispose(): void;

  // Playback control
  play(): void;
  pause(): void;
  stop(): void;
  seek(time: number): void;
  setSpeed(speed: number): void;

  // State queries
  isPlaying(): boolean;
  getCurrentTime(): number;
  getDuration(): number;
  getAgentStates(): AgentState[];

  // Events
  onTimeUpdate(callback: (time: number) => void): () => void;
  onComplete(callback: () => void): () => void;
  onAgentAction(callback: (agent: string, action: AgentAction) => void): () => void;
}

interface AnimatedAgents {
  agents: AnimatedAgent[];
  timeline: gsap.core.Timeline;
}

interface AgentState {
  id: string;
  position: { x: number; y: number };
  currentAction: AgentAction | null;
  progress: number;  // 0-1 for current action
}
```

### Example Usage

```typescript
const animationService = new AnimationService();

// Initialize with results
const animated = animationService.initialize(results, buildingCanvas);

// Subscribe to time updates
animationService.onTimeUpdate((time) => {
  updateTimelineUI(time);
});

// Subscribe to agent actions
animationService.onAgentAction((agentId, action) => {
  if (action.type === 'INSPECT') {
    highlightRoom(action.targetRoom);
  }
});

// Playback controls
playButton.addEventListener('click', () => animationService.play());
pauseButton.addEventListener('click', () => animationService.pause());
speedSlider.addEventListener('input', (e) => {
  animationService.setSpeed(parseFloat(e.target.value));
});

// Scrubbing
timelineSlider.addEventListener('input', (e) => {
  animationService.seek(parseFloat(e.target.value));
});

// Cleanup
animationService.dispose();
```

### Implementation Notes

- **GSAP Timeline**: Creates one master timeline containing all agent movements
- **Interpolation**: Linear interpolation for MOVE actions, instant for ENTER/EXIT
- **Synchronization**: All agents animated in parallel on single timeline
- **Event System**: Uses callback registry for time/action events
- **Konva Integration**: Updates Konva shape positions each frame

---

## 7. CanvasService

Manages Konva canvas rendering and interaction.

### Interface

```typescript
interface ICanvasService {
  // Lifecycle
  initialize(container: HTMLDivElement, building: Building): Konva.Stage;
  dispose(): void;

  // Rendering
  renderBuilding(building: Building): void;
  renderResults(results: OptimizationResults): void;
  clear(): void;

  // Viewport
  zoomIn(): void;
  zoomOut(): void;
  setZoom(zoom: number): void;
  resetView(): void;
  fitToContent(): void;

  // Selection
  selectNode(nodeId: string): void;
  selectEdge(edgeId: string): void;
  clearSelection(): void;
  getSelection(): { nodes: string[]; edges: string[] };

  // Interaction
  enableEditing(): void;
  disableEditing(): void;
  setDrawingMode(mode: DrawingMode): void;

  // Hit detection
  getElementAtPoint(x: number, y: number): { type: 'node' | 'edge' | null; id: string } | null;

  // Visual effects
  highlightPath(nodeIds: string[]): void;
  clearHighlights(): void;
  showConflictMarker(room: string, agents: string[]): void;
}
```

### Example Usage

```typescript
const canvasService = new CanvasService();

// Initialize
const container = document.getElementById('canvas-container') as HTMLDivElement;
const stage = canvasService.initialize(container, building);

// Render building
canvasService.renderBuilding(building);

// Enable editing
canvasService.enableEditing();
canvasService.setDrawingMode('ADD_DOOR');

// Handle clicks
stage.on('click', (e) => {
  const pos = stage.getPointerPosition();
  const element = canvasService.getElementAtPoint(pos.x, pos.y);

  if (element) {
    if (element.type === 'node') {
      canvasService.selectNode(element.id);
    }
  }
});

// Zoom controls
zoomInBtn.addEventListener('click', () => canvasService.zoomIn());
zoomOutBtn.addEventListener('click', () => canvasService.zoomOut());
fitBtn.addEventListener('click', () => canvasService.fitToContent());

// Highlight agent route
canvasService.highlightPath(['exit-1', 'corridor-1', 'door-R1']);
```

### Implementation Notes

- **Layer Management**: Separate layers for building (bottom), routes (middle), agents (top)
- **Performance**: Uses Konva layer caching for static elements
- **Hit Detection**: Konva's built-in hit detection with custom tolerance
- **Responsive**: Listens to window resize, adjusts stage dimensions
- **Coordinate Mapping**: Handles graph ↔ screen coordinate conversion

---

## 8. Service Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                      UI Components                          │
│  (Canvas, Forms, Panels, Animation, Timeline)               │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼─────────┐      ┌────────▼──────────┐
│ CanvasService   │      │ AnimationService  │
└────────┬────────┘      └─────────┬─────────┘
         │                         │
┌────────▼──────────────────────────▼─────────────────┐
│             Business Services                       │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Building     │  │ Optimization │  │ Validation│ │
│  │ Service      │  │ Service      │  │ Service   │ │
│  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘ │
│         │                 │                 │       │
│         └─────────────────┴─────────────────┘       │
│                           │                         │
└───────────────────────────┼─────────────────────────┘
                            │
        ┌───────────────────┴──────────────────┐
        │                                      │
┌───────▼──────────┐              ┌────────────▼─────────┐
│ StorageService   │              │  ExampleService      │
└──────────────────┘              └──────────────────────┘
                                               │
                                  ┌────────────▼─────────────┐
                                  │  Existing CLI Algorithms │
                                  │  (@models, @algorithms,  │
                                  │   @simulation)           │
                                  └──────────────────────────┘
```

---

## 9. Error Handling

All services must follow consistent error handling:

```typescript
class ServiceError extends Error {
  constructor(
    public code: string,
    public message: string,
    public context?: any
  ) {
    super(message);
    this.name = 'ServiceError';
  }
}

// Error codes
const ErrorCodes = {
  // Building errors
  INVALID_BUILDING: 'INVALID_BUILDING',
  NODE_NOT_FOUND: 'NODE_NOT_FOUND',
  DUPLICATE_ID: 'DUPLICATE_ID',

  // Optimization errors
  OPTIMIZATION_FAILED: 'OPTIMIZATION_FAILED',
  NO_SOLUTION_FOUND: 'NO_SOLUTION_FOUND',
  INFEASIBLE: 'INFEASIBLE',

  // Storage errors
  STORAGE_QUOTA_EXCEEDED: 'STORAGE_QUOTA_EXCEEDED',
  STORAGE_ERROR: 'STORAGE_ERROR',
  SCENARIO_NOT_FOUND: 'SCENARIO_NOT_FOUND',

  // Validation errors
  VALIDATION_FAILED: 'VALIDATION_FAILED',
  INVALID_CONFIGURATION: 'INVALID_CONFIGURATION'
} as const;

// Example usage
try {
  const results = await optimizationService.optimize(config);
} catch (error) {
  if (error instanceof ServiceError) {
    if (error.code === ErrorCodes.INFEASIBLE) {
      showNotification('No solution found. Try reducing redundancy requirements.', 'error');
    }
  } else {
    showNotification('Unexpected error occurred', 'error');
    console.error(error);
  }
}
```

---

## Summary

**Service Layer Design**:
- 8 service interfaces defined
- Stateless facades over CLI algorithms
- Consistent async API (even when synchronous)
- Type-safe contracts with TypeScript
- Standardized error handling
- Clear separation of concerns

**Benefits**:
- ✅ Testable (easy to mock services)
- ✅ Maintainable (single responsibility)
- ✅ Reusable (services used by multiple UI components)
- ✅ Type-safe (full IntelliSense support)
- ✅ CLI compatible (delegates to existing algorithms)

**Next Step**: Create quickstart guide for developers implementing these services.
