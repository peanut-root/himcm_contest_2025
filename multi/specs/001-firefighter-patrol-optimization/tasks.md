# Tasks: Firefighter Patrol Optimization System

**Input**: Design documents from `/specs/001-firefighter-patrol-optimization/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are NOT included in this implementation plan as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths assume single project structure as specified in plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize TypeScript project with package.json and tsconfig.json
- [x] T002 Install core dependencies: graphology, javascript-lp-solver, commander, chalk, ajv
- [x] T003 [P] Install dev dependencies: vitest, @vitest/ui, @types/node, typescript, ts-node
- [x] T004 [P] Configure ESLint and Prettier for code quality
- [x] T005 [P] Create vitest.config.ts for testing framework configuration
- [x] T006 [P] Create project directory structure per plan.md (src/, tests/, examples/)
- [x] T007 [P] Copy building configuration examples from quickstart.md to examples/ directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 [P] Implement Node interface in src/models/graph.ts
- [x] T009 [P] Implement Edge interface in src/models/graph.ts
- [x] T010 [P] Implement Room interface in src/models/building.ts
- [x] T011 [P] Implement Agent interface in src/models/agent.ts
- [x] T012 [P] Implement Building interface in src/models/building.ts
- [x] T013 [P] Implement Action and ActionType types in src/models/route.ts
- [x] T014 [P] Implement Route interface in src/models/route.ts
- [x] T015 [P] Implement MissionConfig interface in src/models/mission.ts
- [x] T016 [P] Implement MissionResult interface in src/models/mission.ts
- [x] T017 [P] Implement Mission interface in src/models/mission.ts
- [x] T018 [P] Implement PerformanceMetrics interface in src/models/mission.ts
- [x] T019 [P] Implement ValidationResult interface in src/models/mission.ts
- [x] T020 [P] Implement TimelineData interface in src/models/mission.ts
- [x] T021 Create Graph class wrapper around graphology in src/models/graph.ts with method getEdgeWeight(edge)
- [x] T022 Implement building configuration loader in src/io/config-loader.ts with JSON schema validation using Ajv
- [x] T023 [P] Implement input validator in src/io/validator.ts for building topology validation (reachability, unique IDs)
- [x] T024 [P] Implement output formatter in src/io/output-formatter.ts for mission result JSON generation

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Building Patrol Planning (Priority: P1) 🎯 MVP

**Goal**: Generate optimal patrol routes for firefighters with complete room coverage and makespan minimization

**Independent Test**: Provide building layout with 6 rooms and 2 firefighters, verify system generates complete coverage routes with calculated completion times

### Implementation for User Story 1

- [x] T025 [P] [US1] Implement A* pathfinding algorithm in src/algorithms/pathfinding/astar.ts with dynamic edge weight support
- [x] T026 [P] [US1] Implement shortest path utilities in src/algorithms/pathfinding/shortest-path.ts using graphology and A*
- [x] T027 [P] [US1] Implement greedy task allocation baseline in src/algorithms/allocation/greedy.ts
- [x] T028 [P] [US1] Implement Hungarian algorithm for task assignment in src/algorithms/allocation/hungarian.ts (~200 lines)
- [x] T029 [P] [US1] Implement ILP task allocation using javascript-lp-solver in src/algorithms/allocation/ilp.ts
- [x] T030 [US1] Implement coverage verification in src/algorithms/validation/coverage.ts (check all rooms inspected ≥1 times)
- [x] T031 [P] [US1] Implement performance metrics calculator in src/algorithms/validation/metrics.ts (makespan, path length, load balance)
- [x] T032 [US1] Implement route planner coordinator in src/simulation/planner.ts integrating allocation + A* pathfinding
- [x] T033 [US1] Implement simulation engine in src/simulation/engine.ts orchestrating mission planning workflow
- [x] T034 [US1] Create CLI entry point in src/cli/index.ts with commander.js
- [x] T035 [US1] Implement plan command in src/cli/commands/plan.ts (load building, configure mission, run planner, output results)
- [x] T036 [US1] Implement validate command in src/cli/commands/validate.ts for configuration and result validation
- [x] T037 [US1] Create basic 6-room example configuration in examples/basic-6-room.json per quickstart.md
- [x] T038 [US1] Add npm scripts to package.json: build, cli, test, validate

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently - MVP complete!

---

## Phase 4: User Story 2 - Redundancy Mode for Critical Verification (Priority: P2)

**Goal**: Support designating high-risk rooms for double-checking by different firefighters

**Independent Test**: Take any building from User Story 1, mark specific rooms as redundant, verify exactly 2 different firefighters inspect those rooms

### Implementation for User Story 2

- [ ] T039 [US2] Update ILP allocation algorithm in src/algorithms/allocation/ilp.ts to handle redundancy constraints (Σ_a x[a][r] ≥ 2 for r ∈ R^(2))
- [ ] T040 [US2] Update Hungarian algorithm in src/algorithms/allocation/hungarian.ts to duplicate redundant room columns and enforce different-agent constraint
- [ ] T041 [US2] Implement redundancy verification in src/algorithms/validation/coverage.ts (check redundant rooms inspected ≥2 times by different agents)
- [ ] T042 [US2] Update route planner in src/simulation/planner.ts to process redundantRooms configuration parameter
- [ ] T043 [US2] Update plan command in src/cli/commands/plan.ts to accept --redundant flag for comma-separated room IDs
- [ ] T044 [US2] Update performance metrics in src/algorithms/validation/metrics.ts to calculate redundancy coverage rate
- [ ] T045 [US2] Create redundancy scenario example in examples/redundancy-scenario.json

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Return-to-Exit Mission Planning (Priority: P3)

**Goal**: Ensure firefighters return to designated exit points after completing inspections

**Independent Test**: Configure any patrol mission to require exit return, verify routes include return paths and updated completion times

### Implementation for User Story 3

- [ ] T046 [P] [US3] Implement return path calculation in src/algorithms/pathfinding/shortest-path.ts (find nearest exit from final room)
- [ ] T047 [US3] Update route planner in src/simulation/planner.ts to append return-to-exit paths when returnToExit=true
- [ ] T048 [US3] Update validation in src/algorithms/validation/coverage.ts to verify all agents end at exit nodes (when required)
- [ ] T049 [US3] Update plan command in src/cli/commands/plan.ts to accept --return-to-exit boolean flag
- [ ] T050 [US3] Update performance metrics in src/algorithms/validation/metrics.ts to include return path time in makespan
- [ ] T051 [US3] Update basic example in examples/basic-6-room.json with optional returnToExit configuration parameter

**Checkpoint**: All user stories (1, 2, 3) should now be independently functional

---

## Phase 6: User Story 4 - Mission Timeline Visualization (Priority: P4)

**Goal**: Provide visual timeline of all firefighter activities showing parallel operations and bottlenecks

**Independent Test**: Generate any patrol mission and verify visualization displays concurrent activities, time markers, and highlights conflicts

### Implementation for User Story 4

- [ ] T052 [P] [US4] Install Mermaid dependency: npm install mermaid @types/mermaid
- [ ] T053 [P] [US4] Implement timeline builder in src/simulation/timeline.ts to extract activities from routes and detect room conflicts
- [ ] T054 [US4] Implement temporal conflict detection in src/algorithms/validation/conflicts.ts (identify simultaneous room inspections)
- [ ] T055 [US4] Implement wait-time insertion in src/simulation/timeline.ts when room conflicts detected
- [ ] T056 [US4] Update route planner in src/simulation/planner.ts to integrate conflict detection and resolution
- [ ] T057 [P] [US4] Implement Mermaid Gantt syntax generator in src/visualization/gantt.ts (convert TimelineData to Mermaid format)
- [ ] T058 [P] [US4] Implement SVG renderer in src/visualization/renderer.ts using Mermaid API
- [ ] T059 [US4] Implement visualize command in src/cli/commands/visualize.ts with --format and --output flags
- [ ] T060 [US4] Update simulation engine in src/simulation/engine.ts to optionally generate timeline data
- [ ] T061 [US4] Update output formatter in src/io/output-formatter.ts to include timeline in mission result JSON

**Checkpoint**: All user stories should now be independently functional with complete feature set

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T062 [P] Add comprehensive error handling and user-friendly error messages throughout CLI commands
- [ ] T063 [P] Add colored terminal output using chalk for better UX in CLI
- [ ] T064 [P] Create README.md with installation, usage, and examples
- [ ] T065 [P] Add JSDoc comments to all public APIs in src/models/, src/algorithms/, src/simulation/
- [ ] T066 [P] Implement benchmark command in src/cli/commands/benchmark.ts for comparing ILP vs Hungarian vs greedy
- [ ] T067 [P] Add algorithm selection flag to plan command (--algorithm ilp|hungarian|greedy)
- [ ] T068 [P] Create multi-agent scenario example in examples/multi-agent-scenario.json
- [ ] T069 [P] Add input validation error messages with specific fix suggestions
- [ ] T070 [P] Implement configuration file schema validation using Ajv with helpful error messages
- [ ] T071 [P] Add performance logging to track algorithm execution times
- [ ] T072 Run quickstart.md validation: execute all examples and verify outputs match expected results

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 allocation algorithms but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Extends US1 pathfinding but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - May integrate with US1-3 but visualization is independently testable

### Within Each User Story

- Models implemented in Phase 2 (Foundational) are shared
- A* pathfinding before shortest path utilities
- Allocation algorithms (greedy, Hungarian, ILP) can be implemented in parallel
- Route planner depends on allocation + pathfinding
- Simulation engine depends on route planner
- CLI commands depend on simulation engine
- Validation utilities can be implemented in parallel with core algorithms

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within User Story 1: T025-T029, T031 can run in parallel (different files)
- Within User Story 4: T052-T054, T057-T058 can run in parallel
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch pathfinding and allocation algorithms together:
Task T025: "Implement A* pathfinding in src/algorithms/pathfinding/astar.ts"
Task T026: "Implement shortest path utilities in src/algorithms/pathfinding/shortest-path.ts"
Task T027: "Implement greedy allocation in src/algorithms/allocation/greedy.ts"
Task T028: "Implement Hungarian algorithm in src/algorithms/allocation/hungarian.ts"
Task T029: "Implement ILP allocation in src/algorithms/allocation/ilp.ts"
Task T031: "Implement metrics calculator in src/algorithms/validation/metrics.ts"

# Then sequentially integrate:
Task T032: "Implement route planner (depends on T025-T029)"
Task T033: "Implement simulation engine (depends on T032)"
Task T034-T038: "CLI and examples (depends on T033)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently with basic-6-room.json
5. Deploy/demo if ready

**Expected MVP Outcome**:
- Input: Building JSON with 6 rooms, 2 agents
- Output: Optimal routes with complete coverage, makespan <5 seconds
- Validation: 100% room coverage, zero conflicts, metrics calculated
- CLI: `npm run cli -- plan --building examples/basic-6-room.json --agents 2 --output results.json`

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T025-T038)
   - Developer B: User Story 2 (T039-T045) - can start after US1 allocation exists
   - Developer C: User Story 3 (T046-T051) - can start after US1 pathfinding exists
   - Developer D: User Story 4 (T052-T061) - can start after US1 planner exists
3. Stories complete and integrate independently

---

## Task Statistics

### Total Tasks: 72

**By Phase**:
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 17 tasks (CRITICAL)
- Phase 3 (US1 - MVP): 14 tasks
- Phase 4 (US2): 7 tasks
- Phase 5 (US3): 6 tasks
- Phase 6 (US4): 10 tasks
- Phase 7 (Polish): 11 tasks

**By User Story**:
- User Story 1 (P1): 14 tasks (T025-T038)
- User Story 2 (P2): 7 tasks (T039-T045)
- User Story 3 (P3): 6 tasks (T046-T051)
- User Story 4 (P4): 10 tasks (T052-T061)
- Infrastructure: 24 tasks (Setup + Foundational)
- Polish: 11 tasks (T062-T072)

**Parallelization**:
- 36 tasks marked [P] (50% parallelizable)
- Setup: 6/7 tasks parallel
- Foundational: 13/17 tasks parallel
- US1: 6/14 tasks parallel
- US4: 4/10 tasks parallel
- Polish: 11/11 tasks parallel

---

## Critical Path Analysis

**Minimum Sequential Tasks** (assuming unlimited parallel capacity):

1. T001 (Initialize project) → T008-T020 (Any one foundational model) → T025 or T027 (Pathfinding or allocation) → T032 (Planner) → T033 (Engine) → T034 (CLI) → T035 (Plan command)

**Estimated Minimum Time**: ~7-10 sequential steps if fully parallelized

**Realistic Single-Developer Timeline**:
- Phase 1: 1 day
- Phase 2: 3-4 days
- Phase 3 (MVP): 5-7 days
- **MVP Complete**: 9-12 days

**Full Feature Timeline**:
- Phase 1-3 (MVP): 9-12 days
- Phase 4 (Redundancy): 2 days
- Phase 5 (Return-to-exit): 1-2 days
- Phase 6 (Visualization): 3-4 days
- Phase 7 (Polish): 2-3 days
- **Total**: 17-23 days

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Validation Checkpoints

### After Phase 2 (Foundational)
- All interfaces compile without errors
- Config loader successfully parses building JSON
- Validator correctly identifies invalid topologies
- Graph class correctly calculates edge weights

### After Phase 3 (User Story 1 - MVP)
- CLI command successfully loads building and generates routes
- Output JSON validates against schema
- Coverage verification confirms 100% room coverage
- Makespan < 5 seconds for 6-room scenario
- Performance metrics match manual calculation for simple test case

### After Phase 4 (User Story 2)
- Redundant rooms inspected by 2 different agents
- Redundancy coverage rate = 1.0
- Makespan increases appropriately for additional inspections

### After Phase 5 (User Story 3)
- All agents end at exit nodes when returnToExit=true
- Return path time included in makespan
- Return validation passes

### After Phase 6 (User Story 4)
- Timeline visualization displays all agent activities
- Parallel corridor traversal shown as overlapping bars
- Room mutual exclusion shown as non-overlapping bars
- Wait actions correctly inserted for room conflicts

### After Phase 7 (Polish)
- All examples from quickstart.md execute successfully
- Error messages are clear and actionable
- README documentation complete
- Benchmark command compares algorithm performance
