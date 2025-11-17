# Firefighter Patrol Modeling System Constitution

<!--
Sync Impact Report:
===================
Version change: [INITIAL] → 1.0.0
Created: First version of constitution based on requirements document

Principles defined:
- Graph-Based Building Representation
- Complete Coverage with Redundancy
- Makespan Optimization
- Task Allocation and Pathfinding
- Mathematical Rigor

Templates status:
✅ plan-template.md - reviewed, no updates needed (generic template)
✅ spec-template.md - reviewed, no updates needed (generic template)
✅ tasks-template.md - reviewed, no updates needed (generic template)

Follow-up TODOs:
- RATIFICATION_DATE to be confirmed by project lead
-->

## Core Principles

### I. Graph-Based Building Representation

The system MUST model buildings as weighted graphs G=(V,E) where:
- Nodes (V) represent corridors, doors, exits
- Edges (E) represent traversable paths with time costs
- Edge weights include base traversal time (c_e) and first-use clearance time (κ_e)
- Clearance operations are idempotent (executed only once per edge)

**Rationale**: Graph abstraction enables algorithmic optimization, supports A* pathfinding, and provides extensibility for multi-floor buildings and dynamic obstacles.

### II. Complete Coverage with Redundancy

The system MUST guarantee:
- Every room is inspected at least once: ∑(a∈A) z(r,a) ≥ 1, ∀r∈R
- Redundant rooms are inspected twice by different agents: ∑(a∈A) z(r,a) ≥ 2, ∀r∈R^(2)
- Node-level mutual exclusion: only one agent may inspect a room at any given time
- Corridor parallel traversal: multiple agents may use corridors simultaneously

**Rationale**: Ensures no trapped persons are missed while allowing configurable redundancy for critical verification without blocking parallel operations in corridors.

### III. Makespan Optimization

The primary objective function MUST minimize total mission completion time:
- T_max = max(a∈A) T_a
- Each agent's time T_a includes: movement, clearance, room entry/exit, inspection, and optional return to exit
- Load balancing across agents to prevent individual bottlenecks

**Rationale**: In emergency scenarios, minimizing completion time directly correlates with lives saved. Balancing workload prevents idle resources while one agent is overwhelmed.

### IV. Task Allocation and Pathfinding

The system MUST implement:
- Optimal task assignment using Hungarian algorithm or ILP to balance agent workloads
- Dynamic A* pathfinding with edge weights: w(e) = c_e + 𝟙[¬cleared(e)]·κ_e
- Clearance state tracking: once an edge is cleared, subsequent traversals exclude κ_e
- Collision detection and wait-time insertion when agents attempt simultaneous room access
- Sequential path updates reflecting evolving graph state

**Rationale**: Optimal allocation minimizes makespan; A* ensures shortest paths; dynamic weights correctly model clearance mechanics; collision handling enforces room mutual exclusion.

### V. Mathematical Rigor and Extensibility

All algorithms and constraints MUST be:
- Expressed in formal mathematical notation for unambiguous specification
- Implemented in TypeScript with typed interfaces matching the mathematical model
- Validated against analytical edge cases before simulation
- Designed for extension: multi-floor graphs (V = V_floor1 ∪ V_floor2 ∪ ...), time-varying edge costs c_e(t), and incomplete information scenarios

**Rationale**: Formal specification prevents implementation ambiguity; strong typing reduces bugs; extensibility supports future research phases (HiMCM contest progression).

## Performance Standards

The system MUST track and report:

| Metric | Definition | Calculation |
|--------|------------|-------------|
| T_max | Maximum completion time | max(a∈A) T_a |
| Path Length | Total traversal distance | Sum of edge weights traversed |
| Redundancy Coverage | Proportion of redundant rooms verified | |R^(2) completed| / |R^(2)| |
| Clearance Efficiency | Clearance operations per total edges | First-clearances / Total edges traversed |

**Rationale**: Quantitative metrics enable objective comparison of allocation strategies and validation against hand-computed solutions.

## Data Structure Standards

TypeScript implementations MUST adhere to:

```typescript
interface Node {
  id: string;
  kind: 'CORRIDOR' | 'DOOR' | 'EXIT';  // Use UPPER_CASE for enums
  x: number;
  y: number;
}

interface Edge {
  id: string;
  from: string;
  to: string;
  baseTime: number;              // c_e
  firstUseClearTime?: number;    // κ_e
  cleared?: boolean;             // State tracking
}

interface Room {
  id: string;
  doorNode: string;
  verifyTime: number;
  redundancy?: boolean;          // Marks R^(2) membership
}

interface Agent {
  id: string;
  startNode: string;
  speed: number;
}
```

**Rationale**: Explicit typing prevents runtime errors; naming convention matches mathematical notation; optional fields support flexible configuration.

## Development Workflow

### Algorithm Validation Gate

Before implementing any optimization algorithm:
1. Document mathematical correctness proof or cite established algorithm
2. Provide hand-worked example with 2 agents, 3 rooms demonstrating correct allocation
3. Identify edge cases (e.g., all rooms redundant, single agent, unreachable rooms)
4. Implement unit tests covering normal and edge cases
5. Only then proceed with integration into simulation

**Rationale**: Algorithmic correctness is foundational; errors in allocation or pathfinding invalidate all simulation results.

### Simulation Output Requirements

Every simulation run MUST produce:
- JSON path sequences: ordered node IDs with timestamps
- Timeline visualization: Gantt chart of agent activities
- Performance metrics table: all values from Performance Standards section
- Validation summary: coverage verification, redundancy compliance

**Rationale**: Standardized outputs enable reproducibility, facilitate debugging, and support contest report generation.

## Governance

This constitution supersedes all informal design discussions and requirements interpretations. Any ambiguity in the requirements document (消防员巡视建模需求说明书_Basic.md) MUST be resolved by:

1. Consulting the mathematical formulation (sections 3-4 of requirements document)
2. Defaulting to the most conservative interpretation that guarantees complete coverage
3. Documenting the decision in `/docs/decisions/` with rationale
4. Updating this constitution if the decision establishes a new principle

### Amendment Procedure

Constitution changes require:
- Clear justification: why existing principles are insufficient
- Impact analysis: which templates, existing code, or documentation must update
- Version bump following semantic versioning:
  - MAJOR: Principle removal or incompatible constraint changes
  - MINOR: New principle addition or material expansion
  - PATCH: Clarifications, typos, non-semantic improvements
- Synchronization of all dependent templates and command files within same commit

### Compliance Verification

All pull requests and implementations MUST:
- Reference which principles govern the implemented feature
- Include tests validating constraints (e.g., coverage ≥ 1, redundancy ≥ 2)
- Justify any complexity deviations in implementation plan's Complexity Tracking section

**Version**: 1.0.0 | **Ratified**: 2025-11-12 | **Last Amended**: 2025-11-12
