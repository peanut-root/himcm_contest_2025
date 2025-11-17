# Data Model: Firefighter Patrol Optimization System

**Feature**: 001-firefighter-patrol-optimization
**Date**: 2025-11-12
**Version**: 1.0

## Overview

This document defines the complete data model for the firefighter patrol optimization system, including TypeScript interfaces, relationships, validation rules, and state transitions. All interfaces align with the constitution's Data Structure Standards.

---

## Core Entities

### Node

Represents a location in the building graph (corridors, doors, exits).

**TypeScript Interface**:
```typescript
interface Node {
  id: string;                           // Unique identifier (e.g., "corridor-1", "door-R1", "exit-north")
  kind: 'CORRIDOR' | 'DOOR' | 'EXIT';   // Node type (UPPER_CASE per constitution)
  x: number;                            // X coordinate for spatial positioning
  y: number;                            // Y coordinate for spatial positioning
  label?: string;                       // Optional human-readable label
}
```

**Validation Rules**:
- `id` must be unique within a building
- `x` and `y` must be non-negative finite numbers
- `kind` must be one of the three enum values
- Coordinates should form a valid connected graph (no isolated nodes except intentionally disconnected)

**Relationships**:
- Connected to other nodes via `Edge` entities
- Doors are entry points to `Room` entities (referenced by `Room.doorNode`)
- Exits are terminal points for optional return-to-exit routing

---

### Edge

Represents a traversable connection between two nodes with time costs.

**TypeScript Interface**:
```typescript
interface Edge {
  id: string;                    // Unique identifier (e.g., "edge-1", "corridor-1-to-2")
  from: string;                  // Source node ID
  to: string;                    // Target node ID
  baseTime: number;              // c_e: Base traversal time (always incurred)
  firstUseClearTime?: number;    // κ_e: Additional time for first-use clearance (optional)
  cleared?: boolean;             // State: has this edge been cleared? (default: false)
  bidirectional?: boolean;       // Can traverse in both directions? (default: true)
}
```

**Validation Rules**:
- `id` must be unique within a building
- `from` and `to` must reference valid node IDs
- `from` !== `to` (no self-loops)
- `baseTime` must be positive
- `firstUseClearTime` must be non-negative if present
- If `bidirectional` is false, create separate Edge for reverse direction

**State Transitions**:
```
Initial: cleared = false (or undefined, treated as false)
After first traversal: cleared = true
Persistent: cleared remains true for mission duration
```

**Dynamic Weight Calculation**:
```typescript
function getEdgeWeight(edge: Edge): number {
  return edge.baseTime + (edge.cleared ? 0 : (edge.firstUseClearTime || 0));
}
```

---

### Room

Represents an inspection target within the building.

**TypeScript Interface**:
```typescript
interface Room {
  id: string;            // Unique identifier (e.g., "R1", "Office-201")
  doorNode: string;      // Node ID of the door providing access to this room
  verifyTime: number;    // Time required to inspect this room
  redundancy?: boolean;  // Is this room in R^(2)? (requires 2 inspections, default: false)
  label?: string;        // Optional human-readable name
}
```

**Validation Rules**:
- `id` must be unique within a building
- `doorNode` must reference a valid node with `kind: 'DOOR'`
- `verifyTime` must be positive
- Each `doorNode` should be referenced by exactly one room (1:1 mapping)

**Coverage Constraint**:
- Standard room: must be inspected ≥1 times (∑_a z[r,a] ≥ 1)
- Redundant room: must be inspected ≥2 times by different agents (∑_a z[r,a] ≥ 2)

---

### Agent (Firefighter)

Represents a patrol team member.

**TypeScript Interface**:
```typescript
interface Agent {
  id: string;          // Unique identifier (e.g., "A1", "Agent-Alpha")
  startNode: string;   // Node ID where agent begins mission (typically an EXIT node)
  speed: number;       // Movement speed in distance/time units
  label?: string;      // Optional human-readable name
}
```

**Validation Rules**:
- `id` must be unique within a mission
- `startNode` must reference a valid node (typically `kind: 'EXIT'`)
- `speed` must be positive
- All agents start simultaneously at time t=0

**Capabilities** (currently homogeneous):
- All agents can clear obstacles
- All agents can inspect all rooms
- Future extension: equipment flags (thermal imaging, breaching tools)

---

### Building

Represents the complete structure to be inspected.

**TypeScript Interface**:
```typescript
interface Building {
  id: string;                  // Unique identifier
  nodes: Node[];               // All locations in the building
  edges: Edge[];               // All connections between nodes
  rooms: Room[];               // All inspection targets
  entrances: string[];         // Node IDs designated as entrances (subset of nodes with kind: 'EXIT')
  exits: string[];             // Node IDs designated as exits (subset of nodes with kind: 'EXIT')
  metadata?: {
    name?: string;
    description?: string;
    floor?: number;            // For future multi-floor support
    dimensions?: {
      width: number;
      height: number;
    };
  };
}
```

**Validation Rules**:
- `id` must be unique across configurations
- `nodes`, `edges`, `rooms` arrays must not be empty
- All `edges[].from` and `edges[].to` must reference valid node IDs from `nodes[]`
- All `rooms[].doorNode` must reference valid node IDs from `nodes[]`
- All `entrances[]` and `exits[]` must reference valid node IDs with `kind: 'EXIT'`
- Graph must be connected: all rooms reachable from at least one entrance
- Entrance and exit sets may overlap (same node can be both)

**Graph Properties**:
- Represented as G=(V,E) where V=nodes, E=edges
- Must form a connected graph (no unreachable rooms)
- May contain cycles (corridors with multiple paths)
- Bidirectional edges modeled as single Edge with `bidirectional: true` or two separate edges

---

### Action

Represents a single action taken by an agent during mission execution.

**TypeScript Interface**:
```typescript
type ActionType = 'MOVE' | 'CLEAR' | 'ENTER' | 'INSPECT' | 'EXIT_ROOM' | 'WAIT';

interface Action {
  type: ActionType;          // Type of action
  startTime: number;         // When action begins (seconds from mission start)
  duration: number;          // How long action takes
  endTime: number;           // When action completes (startTime + duration)
  location: string;          // Node or Room ID where action occurs
  targetRoom?: string;       // Room ID (for ENTER, INSPECT, EXIT_ROOM actions)
  edge?: string;             // Edge ID (for MOVE actions)
  clearedEdge?: boolean;     // Did this MOVE action clear an edge? (for MOVE actions)
  waitReason?: string;       // Explanation for WAIT actions
}
```

**Action Types**:
- **MOVE**: Traverse an edge from one node to another
- **CLEAR**: Clear an obstacle on an edge (included in MOVE duration if first use)
- **ENTER**: Enter a room through its door (fixed time: t_enter)
- **INSPECT**: Perform room inspection (duration: Room.verifyTime)
- **EXIT_ROOM**: Exit room back to corridor (fixed time: t_exit)
- **WAIT**: Idle period waiting for room availability or coordination

**Validation Rules**:
- `startTime` ≥ 0
- `duration` > 0 (except WAIT may have duration 0 if instant coordination)
- `endTime` = `startTime` + `duration`
- Actions for an agent must be ordered by `startTime` with no overlaps
- INSPECT actions for same room by different agents must not overlap in time (mutual exclusion)

---

### Route (Path)

Represents the planned sequence of actions for one agent.

**TypeScript Interface**:
```typescript
interface Route {
  agentId: string;              // Which agent executes this route
  actions: Action[];            // Ordered sequence of actions
  roomsInspected: string[];     // List of room IDs inspected (for coverage tracking)
  totalTime: number;            // Total mission time for this agent (last action endTime)
  pathLength: number;           // Total distance/time traveled (sum of baseTime for all edges)
  clearanceOperations: number;  // Count of edges cleared by this agent
}
```

**Validation Rules**:
- `actions` must be ordered by `startTime`
- `actions` must not overlap in time
- `totalTime` = `actions[actions.length - 1].endTime`
- `roomsInspected` must match INSPECT actions
- Each room in `roomsInspected` appears at most once (no duplicate inspections by same agent)

**Coverage Tracking**:
- Route must contribute to global coverage constraint
- Redundant rooms: may appear in multiple agents' `roomsInspected` lists

---

### Mission

Represents the complete patrol operation with configuration and results.

**TypeScript Interface**:
```typescript
interface MissionConfig {
  building: Building;           // Building to inspect
  agents: Agent[];              // Firefighters assigned to mission
  redundantRooms: string[];     // Room IDs requiring 2 inspections (R^(2))
  returnToExit: boolean;        // Must agents return to an exit after completing inspections?
  timeParameters: {
    enterTime: number;          // t_enter: time to enter a room
    exitTime: number;           // t_exit: time to exit a room
  };
}

interface MissionResult {
  routes: Route[];              // One route per agent
  makespan: number;             // T_max: maximum agent completion time
  metrics: PerformanceMetrics;  // Detailed performance metrics
  validation: ValidationResult;  // Coverage and constraint verification
  timeline?: TimelineData;      // Optional: timeline visualization data
}

interface Mission {
  id: string;
  config: MissionConfig;
  result?: MissionResult;       // Populated after planning completes
  status: 'PENDING' | 'PLANNING' | 'COMPLETED' | 'FAILED';
  createdAt: Date;
  completedAt?: Date;
  error?: string;               // Error message if status = 'FAILED'
}
```

**Validation Rules (MissionConfig)**:
- `agents` array must not be empty
- All `redundantRooms[]` must reference valid room IDs from `building.rooms[]`
- `timeParameters.enterTime` and `timeParameters.exitTime` must be non-negative
- All agents must start at valid nodes (typically exits)

**Mission Lifecycle**:
```
PENDING → (planning starts) → PLANNING → (success) → COMPLETED
                                       ↘ (failure) → FAILED
```

---

## Supporting Data Structures

### PerformanceMetrics

Tracks quantitative mission performance (constitution-mandated).

**TypeScript Interface**:
```typescript
interface PerformanceMetrics {
  makespan: number;                      // T_max: max(agent completion times)
  individualTimes: {                     // T_a for each agent
    agentId: string;
    completionTime: number;
  }[];
  totalPathLength: number;               // Sum of all edges traversed (all agents)
  redundancyCoverage: {
    required: number;                    // |R^(2)|
    completed: number;                   // Count of redundant rooms with 2 inspections
    rate: number;                        // completed / required
  };
  clearanceEfficiency: {
    edgesCleared: number;                // Count of edges cleared at least once
    totalEdgeTraversals: number;         // Total edge uses across all agents
    rate: number;                        // edgesCleared / totalEdgeTraversals
  };
  loadBalance: {
    mean: number;                        // Average agent completion time
    stdDev: number;                      // Standard deviation
    maxDeviation: number;                // |max - min| in absolute time
  };
}
```

**Calculation Notes**:
- `makespan` = max(routes[].totalTime)
- `redundancyCoverage.rate` = 1.0 if all redundant rooms have ≥2 inspections
- `clearanceEfficiency.rate` ∈ [0, 1]; higher is better (fewer redundant clearances)
- `loadBalance` metrics measure workload equity

---

### ValidationResult

Verifies constraint satisfaction and correctness.

**TypeScript Interface**:
```typescript
interface ValidationResult {
  valid: boolean;                        // Overall validation result
  coverage: {
    allRoomsInspected: boolean;          // ∑_a z[r,a] ≥ 1 ∀r
    missingRooms: string[];              // Room IDs with zero inspections
  };
  redundancy: {
    redundancySatisfied: boolean;        // ∑_a z[r,a] ≥ 2 ∀r ∈ R^(2)
    insufficientInspections: {           // Redundant rooms with <2 inspections
      roomId: string;
      inspectionCount: number;
    }[];
  };
  conflicts: {
    noRoomConflicts: boolean;            // No simultaneous room inspections
    conflictingActions: {                // Pairs of conflicting INSPECT actions
      agent1: string;
      agent2: string;
      roomId: string;
      time: number;
    }[];
  };
  returnToExit: {
    allReturned: boolean;                // All agents end at an exit (if required)
    failedReturns: string[];             // Agent IDs that didn't return
  };
  errors: string[];                      // List of all validation error messages
}
```

**Validation Logic**:
- `valid` = true iff all sub-checks pass
- Coverage: cross-reference routes[].roomsInspected with building.rooms[]
- Conflicts: check INSPECT action time intervals for overlaps
- Return-to-exit: check last action location is in building.exits[]

---

### TimelineData

Data structure for generating Gantt chart visualization.

**TypeScript Interface**:
```typescript
interface TimelineData {
  agents: {
    agentId: string;
    activities: {
      startTime: number;
      endTime: number;
      label: string;              // e.g., "Move to R1", "Inspect R1", "Wait"
      type: ActionType;
      color?: string;             // For visual distinction
    }[];
  }[];
  events: {                       // Key events for marking on timeline
    time: number;
    description: string;
    agents?: string[];            // Which agents involved
  }[];
  duration: number;               // Total mission duration (makespan)
}
```

**Usage**:
- Converted to Mermaid syntax for Gantt chart generation
- Exported to JSON for external visualization tools
- Activities include all actions from routes, possibly merged for readability

---

## Entity Relationships Diagram

```
Building
  ├─ nodes[] ──→ Node
  ├─ edges[] ──→ Edge
  │              ├─ from ──→ Node.id
  │              └─ to ──→ Node.id
  ├─ rooms[] ──→ Room
  │              └─ doorNode ──→ Node.id
  ├─ entrances[] ──→ Node.id (kind: EXIT)
  └─ exits[] ──→ Node.id (kind: EXIT)

Mission
  ├─ config
  │   ├─ building ──→ Building
  │   ├─ agents[] ──→ Agent
  │   │              └─ startNode ──→ Node.id
  │   └─ redundantRooms[] ──→ Room.id
  └─ result
      ├─ routes[] ──→ Route
      │              ├─ agentId ──→ Agent.id
      │              ├─ actions[] ──→ Action
      │              │              ├─ location ──→ Node.id
      │              │              ├─ targetRoom ──→ Room.id
      │              │              └─ edge ──→ Edge.id
      │              └─ roomsInspected[] ──→ Room.id
      ├─ metrics ──→ PerformanceMetrics
      ├─ validation ──→ ValidationResult
      └─ timeline ──→ TimelineData
```

---

## File Formats

### Input: Building Configuration (JSON)

See `contracts/building-schema.json` for full JSON schema.

**Example**:
```json
{
  "id": "office-building-6room",
  "nodes": [
    {"id": "exit-north", "kind": "EXIT", "x": 0, "y": 0},
    {"id": "corridor-1", "kind": "CORRIDOR", "x": 10, "y": 0},
    {"id": "door-R1", "kind": "DOOR", "x": 10, "y": 5}
  ],
  "edges": [
    {"id": "e1", "from": "exit-north", "to": "corridor-1", "baseTime": 10, "bidirectional": true}
  ],
  "rooms": [
    {"id": "R1", "doorNode": "door-R1", "verifyTime": 30}
  ],
  "entrances": ["exit-north"],
  "exits": ["exit-north", "exit-south"]
}
```

### Output: Mission Result (JSON)

See `contracts/mission-output-schema.json` for full JSON schema.

**Example**:
```json
{
  "missionId": "mission-001",
  "makespan": 145.5,
  "routes": [
    {
      "agentId": "A1",
      "totalTime": 145.5,
      "roomsInspected": ["R1", "R2", "R3"],
      "actions": [
        {"type": "MOVE", "startTime": 0, "duration": 10, "endTime": 10, "location": "corridor-1"}
      ]
    }
  ],
  "metrics": {
    "makespan": 145.5,
    "redundancyCoverage": {"required": 2, "completed": 2, "rate": 1.0}
  },
  "validation": {
    "valid": true,
    "coverage": {"allRoomsInspected": true, "missingRooms": []},
    "conflicts": {"noRoomConflicts": true, "conflictingActions": []}
  }
}
```

---

## State Management

### Graph State (Clearance Tracking)

**Mutable State**:
- `Edge.cleared` flag changes during simulation
- Initially: all edges have `cleared = false`
- After first traversal by any agent: `cleared = true`
- Shared state: all agents see updated clearance status

**Implementation Notes**:
- Use single graph instance shared across all agents during planning
- Update clearance state sequentially (agent 1 completes → agent 2 plans → etc.) OR
- Use optimistic planning: assume edges will be cleared when first agent reaches them

### Temporal State (Room Availability)

**Room Occupancy Tracking**:
- Maintain busy intervals: `Map<roomId, Interval[]>` where `Interval = {start, end}`
- When planning agent route: check if proposed INSPECT overlaps with existing intervals
- If overlap: insert WAIT action or delay inspection

**Conflict Resolution**:
- Priority: earlier-arriving agent gets room first
- Later agent waits until room is free
- Waiting time added to agent's total time

---

## Constants and Configuration

### Time Parameters

```typescript
interface TimeConstants {
  ENTER_TIME: number;      // Default: 5 seconds
  EXIT_TIME: number;       // Default: 5 seconds
  MIN_INSPECT_TIME: number; // Validation: Room.verifyTime ≥ this
  MAX_CLEARANCE_TIME: number; // Validation: Edge.firstUseClearTime ≤ this (optional)
}
```

### Performance Thresholds

```typescript
interface PerformanceThresholds {
  MAX_PLANNING_TIME_MS: number;      // SC-001: 5000ms for 6-room scenario
  OPTIMALITY_TOLERANCE: number;      // SC-004: 0.15 (within 15% of optimal)
  LOAD_BALANCE_TOLERANCE: number;    // SC-005: 0.20 (20% variance allowed)
}
```

---

## Data Model Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-12 | Initial data model based on feature spec and constitution |

---

## Next Steps

1. Generate JSON schemas in `contracts/` directory
2. Implement TypeScript interfaces in `src/models/`
3. Implement validation logic in `src/io/validator.ts`
4. Create example configurations in `examples/`
