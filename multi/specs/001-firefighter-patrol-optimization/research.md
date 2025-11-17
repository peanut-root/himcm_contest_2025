# Research: Firefighter Patrol Optimization System

**Feature**: 001-firefighter-patrol-optimization
**Date**: 2025-11-12
**Status**: Complete

## Overview

This document resolves all NEEDS CLARIFICATION items from the Technical Context and establishes the technology stack for implementing the firefighter patrol optimization system.

---

## Decision 1: Graph and Pathfinding Library

**Decision**: Use **graphology** with custom A* implementation

**Rationale**:
- **graphology** (npm: `graphology`) is a robust, well-maintained TypeScript/JavaScript graph data structure library
- Provides flexible graph data structures with support for weighted edges and node/edge attributes
- Excellent TypeScript definitions included
- Does NOT include A* built-in, but provides the graph primitives needed for a clean implementation
- More control over A* implementation allows us to implement dynamic edge weights (w(e) = c_e + κ_e for uncleared edges)
- Active maintenance and good documentation

**Alternatives Considered**:
- **ngraph.path**: Includes A* but less flexible for custom weight functions; older maintenance history
- **pathfinding**: Good A* implementation but limited graph structure flexibility; primarily for grid-based pathfinding
- **Custom implementation from scratch**: Rejected due to time constraints and potential for bugs in fundamental data structures

**Installation**:
```bash
npm install graphology
npm install --save-dev @types/graphology
```

**Implementation Notes**:
- Use `graphology` for graph structure (MultiGraph or DirectedGraph based on edge directionality needs)
- Implement custom A* in `src/algorithms/pathfinding/astar.ts` with dynamic weight calculation
- Edge attributes will store: `baseTime`, `firstUseClearTime`, `cleared` state

---

## Decision 2: Optimization Library for Task Assignment

**Decision**: Use **javascript-lp-solver** for ILP and custom Hungarian algorithm implementation

**Rationale**:
- **javascript-lp-solver** (npm: `javascript-lp-solver`) provides Integer Linear Programming capabilities in pure JavaScript/TypeScript
- Suitable for modeling the task assignment problem as ILP with constraints (coverage ≥1, redundancy ≥2, makespan minimization)
- No native dependencies, works in Node.js
- For Hungarian algorithm: No mature TypeScript Hungarian implementation found; will implement custom version in `src/algorithms/allocation/hungarian.ts` (algorithm is well-documented, ~200 lines)
- Hungarian is deterministic and educational for research/contest context

**Alternatives Considered**:
- **munkres-js**: Hungarian algorithm implementation but unmaintained (last update 2016), no TypeScript types
- **Google OR-Tools**: Powerful but requires native bindings, complex setup, overkill for this scale
- **lpsolve**: C library with Node.js bindings, but native dependencies complicate deployment
- **Custom ILP**: Too complex to implement from scratch correctly

**Installation**:
```bash
npm install javascript-lp-solver
```

**Implementation Notes**:
- Use ILP solver as primary allocation method (more flexible for constraints)
- Implement Hungarian algorithm for comparison and educational purposes
- Implement greedy baseline for benchmarking
- All three approaches in `src/algorithms/allocation/` directory

---

## Decision 3: Testing Framework

**Decision**: Use **Vitest**

**Rationale**:
- **Vitest** is a modern, fast testing framework designed for TypeScript/Vite projects
- Native TypeScript support without configuration complexity
- Compatible with Jest API (familiar syntax) but faster execution
- Excellent watch mode for development
- Built-in coverage reporting with c8
- Better ESM module support than Jest
- Active development and modern architecture

**Alternatives Considered**:
- **Jest**: Industry standard but slower, more configuration needed for TypeScript, ESM support issues
- **Node.js native test runner**: Too minimal, lacks assertion library and coverage tools
- **Mocha + Chai**: Older architecture, more configuration required

**Installation**:
```bash
npm install --save-dev vitest @vitest/ui
npm install --save-dev @types/node
```

**Configuration**:
- Create `vitest.config.ts` with TypeScript settings
- Use `describe`, `test`, `expect` API (Jest-compatible)
- Coverage via `vitest --coverage`

---

## Decision 4: Visualization Library for Timeline/Gantt Charts

**Decision**: Use **mermaid** for timeline generation (text-based) + optional **D3.js** for advanced rendering

**Rationale**:
- **Mermaid** (npm: `mermaid`) generates timeline diagrams from text descriptions
- Can output SVG/HTML for embedding in reports or web views
- Gantt chart support built-in with syntax: `gantt` diagram type
- Lightweight and suitable for batch generation
- For more advanced interactive visualizations: **D3.js** (npm: `d3`) provides full control but requires more implementation effort
- Initial implementation uses Mermaid; D3.js can be added later for interactive features

**Alternatives Considered**:
- **Chart.js**: Good for charts but limited Gantt support
- **Plotly.js**: Powerful but heavy dependency
- **Pure D3.js from start**: Too much implementation effort for initial version
- **ASCII art**: Not publication-quality for contest report

**Installation**:
```bash
npm install mermaid
npm install --save-dev @types/mermaid
# Optional for advanced visualization:
npm install d3
npm install --save-dev @types/d3
```

**Implementation Notes**:
- Generate Mermaid syntax strings in `src/visualization/gantt.ts`
- Use Mermaid CLI or programmatic API to render to SVG
- Timeline format: sections for each agent, tasks as bars with start/end times
- Export both Mermaid source (for editing) and rendered SVG (for reports)

---

## Decision 5: Additional Development Dependencies

**Decision**: Standard TypeScript development stack

**Rationale**: Comprehensive tooling for code quality and developer experience

**Dependencies**:

### Core TypeScript tooling:
```bash
npm install --save-dev typescript ts-node
npm install --save-dev @types/node
```

### Code quality:
```bash
npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install --save-dev prettier
```

### CLI framework:
```bash
npm install commander  # For building CLI with subcommands
npm install chalk      # For colored terminal output
```

### JSON schema validation:
```bash
npm install ajv        # For validating building configuration JSON files
npm install ajv-formats
```

---

## Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | TypeScript | 5.x | Core language with strong typing |
| Runtime | Node.js | 18+ | Execution environment |
| Graph Structure | graphology | 0.25+ | Graph data structure |
| Pathfinding | Custom A* | N/A | Dynamic weighted shortest path |
| Optimization | javascript-lp-solver | 0.4+ | ILP for task assignment |
| Task Assignment | Custom Hungarian | N/A | Alternative allocation algorithm |
| Testing | Vitest | 1.x | Unit and integration testing |
| Visualization | Mermaid | 10+ | Timeline/Gantt generation |
| CLI | Commander | 11+ | Command-line interface |
| Validation | Ajv | 8+ | JSON schema validation |
| Code Quality | ESLint + Prettier | Latest | Linting and formatting |

---

## Algorithm Implementation Plan

### A* Pathfinding (Custom Implementation)

**Mathematical Foundation**:
- Priority queue (min-heap) for open set
- f(n) = g(n) + h(n) where:
  - g(n) = actual cost from start to node n
  - h(n) = heuristic (Euclidean distance for geometric graphs)
- Dynamic weight calculation: w(e) = baseTime + (cleared ? 0 : firstUseClearTime)

**Key Features**:
- Update edge `cleared` state during traversal
- Return both path (node sequence) and total cost
- Support for multiple invocations with shared clearance state

**Validation**:
- Hand-worked example: 3-node path with one clearable edge
- Verify that second agent doesn't pay clearance cost
- Edge case: unreachable target (return null/error)

### Hungarian Algorithm (Custom Implementation)

**Mathematical Foundation**:
- Kuhn-Munkres algorithm for min-cost bipartite matching
- O(n³) complexity for n×n cost matrix
- Rows = agents, Columns = rooms, Values = estimated completion times

**Key Features**:
- Convert makespan problem to assignment problem
- Augment for redundancy: duplicate room columns for rooms requiring 2 inspections
- Add constraint: redundant rooms must be assigned to different agents

**Validation**:
- Hand-worked 2×3 example (2 agents, 3 rooms)
- Verify optimal assignment matches intuition
- Edge case: more rooms than agents (sequential assignment for one agent)

### ILP Formulation (Using javascript-lp-solver)

**Variables**:
- x[a][r] = binary variable (agent a inspects room r)
- T_max = continuous variable (makespan)

**Constraints**:
- Coverage: Σ_a x[a][r] ≥ 1 ∀r
- Redundancy: Σ_a x[a][r] ≥ 2 ∀r ∈ R^(2)
- Makespan: T_a ≤ T_max ∀a
- T_a = Σ_r (x[a][r] · time[a][r])

**Objective**: Minimize T_max

**Validation**:
- Compare ILP solution to Hungarian solution
- Verify constraint satisfaction programmatically
- Benchmark against greedy baseline

---

## Performance Benchmarks (Expected)

Based on algorithmic complexity analysis:

| Scenario | Rooms | Agents | Expected Time | Bottleneck |
|----------|-------|--------|---------------|------------|
| Basic | 6 | 2 | <100ms | Graph construction |
| Small | 10 | 3 | <500ms | A* pathfinding |
| Medium | 20 | 5 | <5s | ILP solving |
| Large | 20 | 10 | <30s | Multiple A* calls |

**Performance Goals (from Success Criteria)**:
- ✅ SC-001: 6-room scenario in <5 seconds (expect ~100ms, 50x headroom)
- ✅ SC-010: Support 1-20 rooms, 1-10 agents (all within reasonable time)

---

## Development Workflow

### Phase 0: Complete ✅
- Technology stack decisions finalized
- All NEEDS CLARIFICATION items resolved

### Phase 1: Next Steps (Data Model & Contracts)
1. Define TypeScript interfaces in `src/models/` matching constitution standards
2. Create JSON schema for building configuration files (`contracts/building-schema.json`)
3. Create JSON schema for mission output (`contracts/mission-output-schema.json`)
4. Write quickstart.md with example usage

### Phase 2: Implementation (via /speckit.tasks)
1. Setup project structure and dependencies
2. Implement core models
3. Implement algorithms (A*, Hungarian, ILP)
4. Implement simulation engine
5. Implement CLI interface
6. Implement validation and metrics
7. Add visualization
8. Write tests

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Hungarian algorithm bugs | Medium | High | Extensive unit tests, hand-worked validation |
| ILP solver performance issues | Low | Medium | Fallback to Hungarian, greedy baseline |
| Graph library limitations | Low | Low | Graphology is mature and flexible |
| A* implementation errors | Medium | High | Test with known shortest paths, edge cases |
| Temporal conflict detection complexity | Medium | Medium | Simple interval overlap detection, thorough testing |

---

## Open Questions (Resolved)

~~Q1: Which optimization library for task assignment?~~
**A1**: javascript-lp-solver for ILP + custom Hungarian implementation

~~Q2: Which testing framework?~~
**A2**: Vitest

~~Q3: Visualization approach?~~
**A3**: Mermaid for timeline generation, optional D3.js for advanced features

~~Q4: Graph library for A*?~~
**A4**: graphology with custom A* implementation

---

## References

- Graphology documentation: https://graphology.github.io/
- Hungarian algorithm explanation: https://en.wikipedia.org/wiki/Hungarian_algorithm
- A* pathfinding: https://en.wikipedia.org/wiki/A*_search_algorithm
- ILP formulation for scheduling: standard operations research literature
- Vitest documentation: https://vitest.dev/
- Mermaid Gantt charts: https://mermaid.js.org/syntax/gantt.html

---

**Status**: All research complete. Ready for Phase 1 (Data Model & Contracts).
