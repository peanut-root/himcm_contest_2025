# Implementation Plan: Firefighter Patrol Optimization System

**Branch**: `001-firefighter-patrol-optimization` | **Date**: 2025-11-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-firefighter-patrol-optimization/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Emergency response patrol route optimization system that generates optimal firefighter inspection paths for building searches. The system models buildings as weighted graphs, implements task allocation algorithms (Hungarian/ILP) to balance workload across agents, uses A* pathfinding with dynamic edge costs for clearance tracking, and enforces complete room coverage with configurable redundancy while minimizing total mission completion time (makespan). Outputs structured JSON routes with timestamps, performance metrics, and optional timeline visualization.

## Technical Context

**Language/Version**: TypeScript (as specified in constitution Data Structure Standards)
**Primary Dependencies**: NEEDS CLARIFICATION (graph library for A*, optimization library for Hungarian/ILP, visualization library for Gantt charts)
**Storage**: JSON files for building configurations and mission outputs (no persistent database required)
**Testing**: NEEDS CLARIFICATION (TypeScript testing framework - Jest, Vitest, or similar)
**Target Platform**: Node.js for computation engine, browser for visualization (if web-based) or desktop application
**Project Type**: Single computational library with CLI interface and optional visualization frontend
**Performance Goals**: Generate optimal routes for 6-room/2-agent scenario in <5 seconds; support up to 20 rooms and 10 agents with reasonable performance (<30 seconds)
**Constraints**: Deterministic algorithms (reproducible results), exact or near-optimal solutions (within 15% of theoretical optimal), zero room-level conflicts in generated routes
**Scale/Scope**: Research/simulation tool for HiMCM contest; single-building scenarios; batch processing of multiple configurations; extensible to multi-floor buildings in future phases

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Graph-Based Building Representation
✅ **PASS** - Feature spec explicitly requires modeling buildings as graphs G=(V,E) with nodes (corridors, doors, exits) and edges (traversable paths with time costs). FR-001 mandates this structure.

### Principle II: Complete Coverage with Redundancy
✅ **PASS** - FR-005 guarantees complete coverage (every room inspected at least once). FR-006 supports configurable redundancy (rooms inspected twice by different agents). FR-007 enforces room-level mutual exclusion. FR-008 allows parallel corridor traversal.

### Principle III: Makespan Optimization
✅ **PASS** - FR-010 requires calculating optimal task assignment to minimize makespan. FR-012 defines total mission time as maximum of individual completion times. Success criteria SC-004 and SC-005 enforce optimization quality (within 15% of optimal, <20% workload variance).

### Principle IV: Task Allocation and Pathfinding
✅ **PASS** - Feature requires Hungarian/ILP for task allocation (constitution mandated). FR-019 requires shortest path calculation with dynamic edge costs. FR-009 tracks clearance state. FR-018 detects and resolves temporal conflicts. All constitution requirements met.

### Principle V: Mathematical Rigor and Extensibility
✅ **PASS** - Constitution mandates TypeScript with typed interfaces matching mathematical model - Technical Context confirms TypeScript. Constitution defines exact interfaces (Node, Edge, Room, Agent) which will be implemented. Feature spec includes extensibility notes (multi-floor buildings in Out of Scope but planned). Algorithm Validation Gate requirements will be followed (hand-worked examples, edge case testing per Development Workflow section).

### Performance Standards Compliance
✅ **PASS** - FR-014 requires all constitution-mandated metrics: T_max (makespan), path lengths, redundancy coverage rate, clearance efficiency. Success criteria SC-007 explicitly validates metric output.

### Algorithm Validation Gate (Development Workflow)
✅ **PASS** - Will be enforced during implementation. Plan includes Phase 0 research for algorithm selection with correctness proofs. Phase 1 will include hand-worked validation examples. Testing phase will cover edge cases (single agent, all rooms redundant, unreachable rooms per spec edge cases section).

### Simulation Output Requirements
✅ **PASS** - FR-015 requires JSON output with node IDs and timestamps. User Story 4 covers timeline visualization (Gantt chart). FR-014 covers performance metrics table. SC-002, SC-003, SC-008 cover validation requirements (coverage, redundancy, conflicts).

**GATE RESULT: ✅ PASS - All constitution principles satisfied. Proceed to Phase 0 research.**

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── graph.ts           # Node, Edge interfaces and graph data structure
│   ├── building.ts        # Building, Room entities
│   ├── agent.ts           # Agent/Firefighter entity
│   ├── mission.ts         # Mission configuration and results
│   └── route.ts           # Route/Path representation
├── algorithms/
│   ├── pathfinding/
│   │   ├── astar.ts       # A* implementation with dynamic weights
│   │   └── shortest-path.ts # Shortest path utilities
│   ├── allocation/
│   │   ├── hungarian.ts   # Hungarian algorithm for task assignment
│   │   ├── ilp.ts         # Integer Linear Programming solver
│   │   └── greedy.ts      # Greedy baseline for comparison
│   └── validation/
│       ├── coverage.ts    # Coverage verification
│       ├── conflicts.ts   # Temporal conflict detection
│       └── metrics.ts     # Performance metric calculation
├── simulation/
│   ├── engine.ts          # Main simulation orchestrator
│   ├── planner.ts         # Route planning coordinator
│   └── timeline.ts        # Timeline generation and conflict resolution
├── io/
│   ├── config-loader.ts   # Building configuration JSON loader
│   ├── output-formatter.ts # Route output JSON formatter
│   └── validator.ts       # Input validation
├── visualization/
│   ├── gantt.ts           # Gantt chart timeline generator
│   └── renderer.ts        # Rendering utilities (if implementing visualization)
└── cli/
    ├── index.ts           # CLI entry point
    └── commands/
        ├── plan.ts        # Route planning command
        ├── validate.ts    # Configuration validation command
        └── visualize.ts   # Timeline visualization command

tests/
├── unit/
│   ├── models/
│   ├── algorithms/
│   └── simulation/
├── integration/
│   ├── planning-scenarios.test.ts
│   ├── redundancy.test.ts
│   └── edge-cases.test.ts
└── fixtures/
    ├── buildings/         # Sample building configurations
    └── expected/          # Expected outputs for validation

examples/
├── basic-6-room.json      # Basic 6-room scenario from requirements
├── redundancy-scenario.json
└── multi-agent-scenario.json
```

**Structure Decision**: Single project structure selected. This is a computational library with CLI interface, not a web or mobile application. The structure emphasizes:
- Clear separation between data models, algorithms, and simulation orchestration
- Algorithm modules grouped by function (pathfinding, allocation, validation)
- Dedicated I/O layer for configuration and output
- Optional visualization module for timeline generation
- CLI interface for command-line usage
- Comprehensive test structure covering unit, integration, and fixture-based validation

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations. This section intentionally left empty.

---

## Post-Phase 1 Constitution Re-evaluation

*Re-checked after completing research.md, data-model.md, contracts/, and quickstart.md*

### Technology Decisions vs Constitution Requirements

**✅ TypeScript Interfaces Match Constitution Standards**:
- All interfaces in data-model.md use UPPER_CASE enums (NODE kind: 'CORRIDOR' | 'DOOR' | 'EXIT')
- Exact interface definitions from constitution preserved (Node, Edge, Room, Agent)
- Optional fields marked with `?` as specified in constitution

**✅ Mathematical Rigor Maintained**:
- Data model includes formal validation rules and state transitions
- Algorithms documented with mathematical foundations in research.md
- JSON schemas provide unambiguous specification for inputs/outputs

**✅ Graph Representation Confirmed**:
- Building entity explicitly models G=(V,E) with nodes and edges
- Edge dynamic weight calculation documented: w(e) = baseTime + (cleared ? 0 : firstUseClearTime)
- Clearance state tracking included in Edge interface

**✅ Performance Metrics Tracked**:
- PerformanceMetrics interface includes all constitution-mandated metrics
- ValidationResult interface enforces constraint verification
- JSON schema guarantees metric output in mission results

**✅ Algorithm Validation Gate Designed**:
- Research.md includes hand-worked example requirements
- Data model specifies validation test structure
- Quickstart.md demonstrates validation workflows

### Design Decisions

1. **graphology + custom A***: Provides flexibility for dynamic edge weights while leveraging robust graph data structure
2. **javascript-lp-solver + custom Hungarian**: Balances optimization power (ILP) with educational value (Hungarian) and baseline comparison (greedy)
3. **Vitest**: Modern TypeScript-first testing with fast execution
4. **Mermaid + optional D3.js**: Lightweight timeline generation with upgrade path for interactivity

### Risks Identified and Mitigated

- Hungarian algorithm complexity: Mitigated by extensive unit testing and hand-worked validation
- ILP solver performance: Mitigated by fallback to Hungarian and greedy baseline
- A* implementation errors: Mitigated by testing with known shortest paths

**FINAL GATE RESULT: ✅ PASS - All constitution principles maintained through design phase. Ready for implementation via /speckit.tasks.**

---

## Phase Summary

### Phase 0: Research ✅ Complete
- **research.md**: All NEEDS CLARIFICATION resolved
- Technology stack finalized
- Algorithm approaches documented with mathematical foundations
- Performance benchmarks estimated

### Phase 1: Design ✅ Complete
- **data-model.md**: Complete entity definitions with TypeScript interfaces, validation rules, relationships
- **contracts/building-schema.json**: JSON schema for building configuration input
- **contracts/mission-output-schema.json**: JSON schema for mission result output
- **quickstart.md**: User guide with examples, API usage, troubleshooting

### Phase 2: Implementation (Next)
- Run `/speckit.tasks` to generate task breakdown
- Implement per tasks.md
- Follow constitution Algorithm Validation Gate requirements

---

## Artifacts Generated

| Artifact | Location | Status | Description |
|----------|----------|--------|-------------|
| Implementation Plan | plan.md | ✅ Complete | This document |
| Research | research.md | ✅ Complete | Technology decisions and algorithm foundations |
| Data Model | data-model.md | ✅ Complete | Complete TypeScript entity definitions |
| Building Schema | contracts/building-schema.json | ✅ Complete | JSON schema for input validation |
| Output Schema | contracts/mission-output-schema.json | ✅ Complete | JSON schema for output validation |
| Quickstart Guide | quickstart.md | ✅ Complete | User documentation and examples |
| Agent Context | /CLAUDE.md | ✅ Updated | Claude Code context file with TypeScript |

**Total Documentation**: 7 files, ~8000 lines

---

## Next Command

```bash
/speckit.tasks
```

This will generate `tasks.md` with implementation breakdown organized by user story (P1-P4) with specific file paths, parallelization opportunities, and dependency tracking.
