# Implementation Plan: Web Demonstration Application

**Branch**: `002-web-demo` | **Date**: 2025-11-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-web-demo/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create an interactive web application to demonstrate the firefighter patrol optimization system. The web app provides a visual canvas for building design, animated visualization of optimization results, and form-based mission configuration. Primary goal is to make the CLI tool accessible through a visual interface, enabling users to design buildings, run optimizations, and understand results through spatial animations within 5 minutes instead of editing JSON files manually.

## Technical Context

**Language/Version**: TypeScript 5.9 with strict mode (existing codebase)
**Primary Dependencies**:
- **Konva.js 9.x** - Interactive 2D canvas rendering (~75KB gzipped)
- **GSAP 3.12+** - Animation timeline and playback controls (~47KB gzipped)
- **Vite 5.x** - Build tool and dev server
- **Vitest + Playwright** - Testing framework (unit + E2E)

**Storage**: Browser LocalStorage (for scenario persistence), no backend database required
**Testing**: Vitest for unit/integration tests, Playwright for E2E browser automation
**Target Platform**: Modern desktop browsers (Chrome, Firefox, Safari, Edge) with minimum 1024px width
**Project Type**: Web (static site with frontend only, reuses existing TypeScript CLI algorithms)
**Performance Goals**: 30 FPS animation playback, <100ms UI interaction response, support 20 rooms + 10 agents
**Constraints**: Static deployment (no server), offline-capable after initial load, bi-directional CLI compatibility
**Scale/Scope**: Single-user demonstration tool, 4 user stories (P1-P4), approximately 20 screens/views
**Total Bundle Size**: ~122KB gzipped (Konva + GSAP) + existing CLI algorithms

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Check (Before Phase 0)

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| I. Graph-Based Building Representation | Web app must use same graph model G=(V,E) as CLI | ✅ PASS | Web canvas will visualize and edit the same graph structure; export/import JSON ensures compatibility |
| II. Complete Coverage with Redundancy | Web app must validate coverage constraints | ✅ PASS | Reuses existing validator from CLI; UI will display validation errors visually |
| III. Makespan Optimization | Web app must call existing optimization algorithms | ✅ PASS | No new algorithms; web UI triggers existing ILP/Hungarian/Greedy allocators |
| IV. Task Allocation and Pathfinding | Web app must use existing A* and allocation | ✅ PASS | Reuses all existing algorithms; only adds visualization layer on top |
| V. Mathematical Rigor | Web app must maintain typed interfaces | ✅ PASS | TypeScript frontend will import and use existing typed models |
| Data Structure Standards | Must use identical Node/Edge/Room/Agent interfaces | ✅ PASS | Frontend will share type definitions from existing codebase |
| Algorithm Validation Gate | No new algorithms to validate | ✅ PASS | All optimization logic already validated in CLI implementation |
| Simulation Output Requirements | Must display same metrics as CLI | ✅ PASS | Web UI will render JSON output from existing simulation engine |

**Pre-Design Result**: ✅ **PASS** - No constitution violations. Web application is a visualization and interaction layer over existing validated algorithms.

### Post-Design Check (After Phase 1)

Phase 1 design artifacts completed:
- ✅ research.md - Technology stack selected
- ✅ data-model.md - Data structures defined
- ✅ contracts/services.md - Service interfaces defined
- ✅ quickstart.md - Developer guide created

**Re-validation Against Constitution**:

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| I. Graph-Based Building Representation | Data model uses same graph structure | ✅ PASS | VisualNode/VisualEdge extend CLI Node/Edge; reuses graphology |
| II. Complete Coverage with Redundancy | Services delegate to CLI validators | ✅ PASS | ValidationService wraps existing coverage validators |
| III. Makespan Optimization | OptimizationService calls CLI planner | ✅ PASS | No new optimization logic; pure delegation |
| IV. Task Allocation and Pathfinding | AnimationService renders existing routes | ✅ PASS | Visualizes Route[] from CLI without modification |
| V. Mathematical Rigor | TypeScript strict mode maintained | ✅ PASS | All interfaces typed; imports CLI types |
| Data Structure Standards | Node/Edge/Room/Agent interfaces preserved | ✅ PASS | Web models extend, not replace, CLI interfaces |

**Design Quality Checks**:

| Check | Status | Evidence |
|-------|--------|----------|
| No algorithm duplication | ✅ PASS | All services import from `@algorithms`, `@simulation` |
| Type safety preserved | ✅ PASS | Strict TypeScript; all service methods fully typed |
| CLI compatibility | ✅ PASS | JSON import/export uses same schema; validated by existing validator |
| Separation of concerns | ✅ PASS | UI state (Canvas/Animation) separate from domain models (Building/Route) |
| Testability | ✅ PASS | Services are stateless, easily mockable interfaces |

**Post-Design Result**: ✅ **PASS** - All constitution principles upheld. Design maintains CLI compatibility while adding visualization layer.

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
# Existing CLI codebase (unchanged)
src/
├── models/              # Shared types: Node, Edge, Room, Agent, Mission, Route
├── algorithms/          # Pathfinding (A*), allocation (ILP/Hungarian/Greedy), validation
├── simulation/          # Planner, engine, timeline builder
├── visualization/       # Gantt chart generators (text, mermaid, HTML)
├── io/                  # Config loader, validator, output formatter
└── cli/                 # CLI commands (plan, validate, visualize, benchmark)

# New web application (this feature)
web/
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── canvas/      # Canvas rendering components
│   │   │   ├── BuildingCanvas.ts     # Main canvas controller
│   │   │   ├── NodeRenderer.ts       # Draw nodes (exits, corridors, doors)
│   │   │   ├── EdgeRenderer.ts       # Draw edges between nodes
│   │   │   └── RoomRenderer.ts       # Draw room labels and highlights
│   │   ├── animation/   # Animation playback components
│   │   │   ├── AnimationController.ts # Play/pause/speed controls
│   │   │   ├── AgentAnimator.ts      # Animate agent movements
│   │   │   └── TimelineView.ts       # Timeline scrubber
│   │   ├── forms/       # Mission configuration forms
│   │   │   ├── MissionForm.ts        # Agent count, start location, options
│   │   │   └── RoomSelector.ts       # Redundant room multi-select
│   │   ├── panels/      # Information panels
│   │   │   ├── MetricsPanel.ts       # Performance metrics display
│   │   │   ├── ValidationPanel.ts    # Validation errors/warnings
│   │   │   └── ScenarioPanel.ts      # Save/load scenarios
│   │   └── toolbar/     # Canvas editing toolbar
│   │       ├── DrawingTools.ts       # Add node, connect edge, delete
│   │       └── PropertyEditor.ts     # Edit node/edge/room properties
│   ├── services/        # Business logic
│   │   ├── BuildingService.ts        # Building CRUD operations
│   │   ├── OptimizationService.ts    # Trigger CLI planner (via import)
│   │   ├── ValidationService.ts      # Building validation (via import)
│   │   ├── StorageService.ts         # LocalStorage persistence
│   │   └── ExampleService.ts         # Load example scenarios
│   ├── models/          # Web-specific view models (extend CLI models)
│   │   ├── CanvasState.ts            # Zoom, pan, drawing mode
│   │   ├── AnimationState.ts         # Playback state, current time
│   │   └── UIState.ts                # Active panel, selected elements
│   ├── utils/           # Helpers
│   │   ├── coordinates.ts            # Screen ↔ graph coordinate conversion
│   │   ├── rendering.ts              # Canvas drawing utilities
│   │   └── validation.ts             # UI-specific validation helpers
│   ├── app.ts           # Main application entry point
│   └── index.html       # HTML shell
├── assets/
│   ├── examples/        # Pre-loaded JSON scenarios (4 files)
│   └── styles/          # CSS for UI components
├── dist/                # Built static files (deployment target)
└── tests/
    ├── canvas/          # Canvas rendering tests
    ├── animation/       # Animation logic tests
    └── integration/     # End-to-end UI flow tests

# Shared configuration
tsconfig.json            # TypeScript config (existing)
tsconfig.web.json        # Web-specific TS config (extends base)
package.json             # Updated with web build scripts
```

**Structure Decision**: Web application is a separate `web/` directory to isolate frontend code from CLI. The web app imports existing models and algorithms from `src/` as library dependencies, ensuring code reuse and maintaining single source of truth for optimization logic. Static site output to `web/dist/` can be deployed to any static host or served locally.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations detected. This section is not applicable.
