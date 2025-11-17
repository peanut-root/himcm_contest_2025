# Quickstart Guide: Firefighter Patrol Optimization System

**Feature**: 001-firefighter-patrol-optimization
**Date**: 2025-11-12
**Audience**: Users, researchers, and developers

## Overview

This guide shows how to use the firefighter patrol optimization system to generate optimal inspection routes for emergency building searches.

---

## Prerequisites

- Node.js 18+ installed
- TypeScript project configured (via `package.json`)
- Building configuration file in JSON format

---

## Installation

```bash
# Clone repository
git clone <repository-url>
cd himcm

# Install dependencies
npm install

# Build the project
npm run build
```

---

## Quick Example: 6-Room Office Building

### Step 1: Create Building Configuration

Create `my-building.json`:

```json
{
  "id": "office-6-room",
  "nodes": [
    {"id": "exit-north", "kind": "EXIT", "x": 0, "y": 0},
    {"id": "exit-south", "kind": "EXIT", "x": 60, "y": 0},
    {"id": "corridor-1", "kind": "CORRIDOR", "x": 10, "y": 0},
    {"id": "corridor-2", "kind": "CORRIDOR", "x": 20, "y": 0},
    {"id": "corridor-3", "kind": "CORRIDOR", "x": 30, "y": 0},
    {"id": "corridor-4", "kind": "CORRIDOR", "x": 40, "y": 0},
    {"id": "corridor-5", "kind": "CORRIDOR", "x": 50, "y": 0},
    {"id": "door-R1", "kind": "DOOR", "x": 10, "y": 5, "label": "Room 1 Door"},
    {"id": "door-R2", "kind": "DOOR", "x": 20, "y": 5, "label": "Room 2 Door"},
    {"id": "door-R3", "kind": "DOOR", "x": 30, "y": 5, "label": "Room 3 Door"},
    {"id": "door-R4", "kind": "DOOR", "x": 10, "y": -5, "label": "Room 4 Door"},
    {"id": "door-R5", "kind": "DOOR", "x": 20, "y": -5, "label": "Room 5 Door"},
    {"id": "door-R6", "kind": "DOOR", "x": 30, "y": -5, "label": "Room 6 Door"}
  ],
  "edges": [
    {"id": "e1", "from": "exit-north", "to": "corridor-1", "baseTime": 10},
    {"id": "e2", "from": "corridor-1", "to": "corridor-2", "baseTime": 10},
    {"id": "e3", "from": "corridor-2", "to": "corridor-3", "baseTime": 10},
    {"id": "e4", "from": "corridor-3", "to": "corridor-4", "baseTime": 10},
    {"id": "e5", "from": "corridor-4", "to": "corridor-5", "baseTime": 10},
    {"id": "e6", "from": "corridor-5", "to": "exit-south", "baseTime": 10},
    {"id": "e7", "from": "corridor-1", "to": "door-R1", "baseTime": 5},
    {"id": "e8", "from": "corridor-2", "to": "door-R2", "baseTime": 5},
    {"id": "e9", "from": "corridor-3", "to": "door-R3", "baseTime": 5},
    {"id": "e10", "from": "corridor-1", "to": "door-R4", "baseTime": 5},
    {"id": "e11", "from": "corridor-2", "to": "door-R5", "baseTime": 5},
    {"id": "e12", "from": "corridor-3", "to": "door-R6", "baseTime": 5}
  ],
  "rooms": [
    {"id": "R1", "doorNode": "door-R1", "verifyTime": 30, "label": "Office 1"},
    {"id": "R2", "doorNode": "door-R2", "verifyTime": 30, "label": "Office 2"},
    {"id": "R3", "doorNode": "door-R3", "verifyTime": 30, "label": "Office 3"},
    {"id": "R4", "doorNode": "door-R4", "verifyTime": 30, "label": "Office 4"},
    {"id": "R5", "doorNode": "door-R5", "verifyTime": 30, "label": "Office 5"},
    {"id": "R6", "doorNode": "door-R6", "verifyTime": 30, "label": "Office 6"}
  ],
  "entrances": ["exit-north", "exit-south"],
  "exits": ["exit-north", "exit-south"],
  "metadata": {
    "name": "Basic 6-Room Office Building",
    "description": "Single-floor office with 6 rooms along a corridor"
  }
}
```

### Step 2: Run Route Planning

```bash
# Plan routes with 2 agents starting from north entrance
npm run cli -- plan \
  --building my-building.json \
  --agents 2 \
  --start exit-north \
  --output results.json

# Or use the programmatic API (see below)
```

Expected output:
```
Planning mission for office-6-room...
Agents: 2
Rooms: 6
Algorithm: ILP allocation + A* pathfinding

✓ Task allocation complete (45ms)
✓ Route planning complete (120ms)
✓ Validation: All rooms covered
✓ Validation: No conflicts detected

Results:
  Makespan: 185s
  Agent A1: 185s (rooms: R1, R3, R5)
  Agent A2: 180s (rooms: R2, R4, R6)
  Load balance: 2.7% deviation

Output written to results.json
```

### Step 3: View Results

```bash
# Display summary
npm run cli -- summarize results.json

# Generate timeline visualization
npm run cli -- visualize results.json --output timeline.svg

# Validate results
npm run cli -- validate results.json
```

---

## Programmatic Usage

### TypeScript API

```typescript
import { MissionPlanner } from './src/simulation/planner';
import { loadBuildingConfig } from './src/io/config-loader';
import { formatMissionOutput } from './src/io/output-formatter';

// Load building configuration
const building = loadBuildingConfig('my-building.json');

// Create mission configuration
const missionConfig = {
  building,
  agents: [
    { id: 'A1', startNode: 'exit-north', speed: 1.0 },
    { id: 'A2', startNode: 'exit-north', speed: 1.0 }
  ],
  redundantRooms: [],  // No redundancy for basic scenario
  returnToExit: false,
  timeParameters: {
    enterTime: 5,
    exitTime: 5
  }
};

// Plan mission
const planner = new MissionPlanner();
const result = await planner.planMission(missionConfig);

// Check results
if (result.validation.valid) {
  console.log(`Mission complete! Makespan: ${result.makespan}s`);
  console.log(`Coverage: ${result.validation.coverage.allRoomsInspected ? '✓' : '✗'}`);

  // Export to JSON
  const outputJson = formatMissionOutput(result);
  fs.writeFileSync('output.json', JSON.stringify(outputJson, null, 2));
} else {
  console.error('Validation errors:', result.validation.errors);
}
```

---

## Common Scenarios

### Scenario 1: Redundancy Mode

Mark critical rooms for double-checking:

```bash
npm run cli -- plan \
  --building my-building.json \
  --agents 2 \
  --redundant R1,R3 \
  --output results-redundant.json
```

Or programmatically:
```typescript
const missionConfig = {
  building,
  agents: [...],
  redundantRooms: ['R1', 'R3'],  // These rooms inspected twice by different agents
  returnToExit: false,
  timeParameters: { enterTime: 5, exitTime: 5 }
};
```

Expected behavior:
- Rooms R1 and R3 will be inspected by 2 different agents
- Other rooms inspected once
- Makespan will increase due to additional inspections

### Scenario 2: Return to Exit

Ensure agents return to exit points after inspection:

```bash
npm run cli -- plan \
  --building my-building.json \
  --agents 2 \
  --return-to-exit \
  --output results-return.json
```

Or programmatically:
```typescript
const missionConfig = {
  building,
  agents: [...],
  redundantRooms: [],
  returnToExit: true,  // Agents must end at an exit
  timeParameters: { enterTime: 5, exitTime: 5 }
};
```

Expected behavior:
- Each agent's route includes return path to nearest exit
- Makespan includes return travel time
- Validation checks last location is an exit

### Scenario 3: Obstacles with Clearance Time

Add clearance requirements to edges:

```json
{
  "edges": [
    {
      "id": "e2",
      "from": "corridor-1",
      "to": "corridor-2",
      "baseTime": 10,
      "firstUseClearTime": 20  // First agent pays 30s total, subsequent agents pay 10s
    }
  ]
}
```

Expected behavior:
- First agent to traverse pays baseTime + firstUseClearTime
- Subsequent agents pay only baseTime
- Clearance efficiency metric tracks this

### Scenario 4: Multiple Starting Points

Agents start from different entrances:

```typescript
const missionConfig = {
  building,
  agents: [
    { id: 'A1', startNode: 'exit-north', speed: 1.0 },
    { id: 'A2', startNode: 'exit-south', speed: 1.0 }
  ],
  // ... rest of config
};
```

Expected behavior:
- Agents start simultaneously from different locations
- Task allocation accounts for different starting positions
- Makespan optimization considers spatial distribution

---

## Validation

### Validate Building Configuration

```bash
# Validate before planning
npm run cli -- validate my-building.json --type building

# Check for common issues:
# - Unreachable rooms
# - Disconnected graph
# - Invalid references
# - Negative times
```

### Validate Mission Results

```bash
# Validate after planning
npm run cli -- validate results.json --type mission

# Verifies:
# - Complete coverage (all rooms inspected)
# - Redundancy compliance (redundant rooms inspected twice)
# - No temporal conflicts (room mutual exclusion)
# - Return-to-exit compliance (if enabled)
```

---

## Performance Tips

### For Large Buildings (10+ rooms, 5+ agents)

1. **Use ILP solver for optimal results** (default):
   ```bash
   npm run cli -- plan --algorithm ilp ...
   ```

2. **Use Hungarian for faster approximate solutions**:
   ```bash
   npm run cli -- plan --algorithm hungarian ...
   ```

3. **Use greedy for baseline comparison**:
   ```bash
   npm run cli -- plan --algorithm greedy ...
   ```

### Benchmarking

```bash
# Compare algorithms
npm run cli -- benchmark \
  --building my-building.json \
  --agents 2,3,4,5 \
  --algorithms ilp,hungarian,greedy \
  --output benchmark-results.csv
```

---

## Visualization

### Generate Timeline (Gantt Chart)

```bash
# Using Mermaid (text-based)
npm run cli -- visualize results.json --format mermaid --output timeline.mmd

# Render to SVG
npm run cli -- visualize results.json --format svg --output timeline.svg

# Interactive HTML (if D3.js visualization implemented)
npm run cli -- visualize results.json --format html --output timeline.html
```

### Timeline Features

- Each agent shown as separate row
- Activities color-coded:
  - Blue: MOVE actions
  - Green: INSPECT actions
  - Yellow: WAIT actions
  - Red: CLEAR actions
- Parallel corridor traversal shown as overlapping blue bars
- Room mutual exclusion shown as non-overlapping green bars
- Hover for action details (in HTML format)

---

## Example Output Structure

```json
{
  "missionId": "mission-001",
  "makespan": 185.0,
  "routes": [
    {
      "agentId": "A1",
      "totalTime": 185.0,
      "pathLength": 150.0,
      "clearanceOperations": 2,
      "roomsInspected": ["R1", "R3", "R5"],
      "actions": [
        {
          "type": "MOVE",
          "startTime": 0,
          "duration": 10,
          "endTime": 10,
          "location": "corridor-1",
          "edge": "e1"
        },
        {
          "type": "MOVE",
          "startTime": 10,
          "duration": 5,
          "endTime": 15,
          "location": "door-R1",
          "edge": "e7"
        },
        {
          "type": "ENTER",
          "startTime": 15,
          "duration": 5,
          "endTime": 20,
          "location": "door-R1",
          "targetRoom": "R1"
        },
        {
          "type": "INSPECT",
          "startTime": 20,
          "duration": 30,
          "endTime": 50,
          "location": "R1",
          "targetRoom": "R1"
        }
        // ... more actions
      ]
    }
  ],
  "metrics": {
    "makespan": 185.0,
    "individualTimes": [
      {"agentId": "A1", "completionTime": 185.0},
      {"agentId": "A2", "completionTime": 180.0}
    ],
    "redundancyCoverage": {"required": 0, "completed": 0, "rate": 1.0},
    "clearanceEfficiency": {"edgesCleared": 3, "totalEdgeTraversals": 18, "rate": 0.167},
    "loadBalance": {"mean": 182.5, "stdDev": 2.5, "maxDeviation": 5.0}
  },
  "validation": {
    "valid": true,
    "coverage": {"allRoomsInspected": true, "missingRooms": []},
    "redundancy": {"redundancySatisfied": true, "insufficientInspections": []},
    "conflicts": {"noRoomConflicts": true, "conflictingActions": []},
    "returnToExit": {"allReturned": false, "failedReturns": []},
    "errors": []
  }
}
```

---

## Troubleshooting

### "Building validation failed"
- Check that all node/edge IDs are unique
- Verify all edge references point to valid nodes
- Ensure all rooms reference DOOR-type nodes
- Confirm entrances/exits reference EXIT-type nodes

### "Unreachable rooms detected"
- Graph is disconnected
- Add missing edges to connect all rooms to entrances
- Use CLI validation to identify unreachable rooms

### "Room conflict detected"
- Two agents scheduled to inspect same room simultaneously
- Report bug if this occurs (should be prevented by conflict resolution)

### "Performance is slow"
- Try Hungarian algorithm instead of ILP for large scenarios
- Reduce redundancy requirements if present
- Check for large clearance times creating complex dependencies

---

## Next Steps

- Read [data-model.md](./data-model.md) for detailed entity descriptions
- Review [contracts/](./contracts/) for JSON schema specifications
- See [research.md](./research.md) for algorithm implementation details
- Refer to [plan.md](./plan.md) for full project structure

---

## Support

For issues or questions:
- Check validation errors first
- Review example configurations in `examples/`
- Consult data model and API documentation
- Report bugs with minimal reproduction example
