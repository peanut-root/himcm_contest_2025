---

description: "Task list for web demonstration application implementation"
---

# Tasks: Web Demonstration Application

**Input**: Design documents from `/specs/003-web-demo/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), quickstart.md

**Tests**: Manual browser testing only (no automated test framework per plan.md)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web demo**: `demo/` directory at repository root
- Static files: HTML, CSS, JavaScript modules, JSON data
- No build tools, no bundlers, no frameworks

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create demo/ directory structure with subdirectories: styles/, scripts/, data/
- [X] T002 Create demo/index.html with basic HTML structure, canvas element, and UI layout
- [X] T003 [P] Create demo/styles/main.css with layout styles, controls, and metrics panel
- [X] T004 [P] Create demo/README.md with overview and quick start instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data and rendering infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create demo/data/building.json with 6-room office layout (nodes, rooms, exits, hallway)
- [X] T006 Copy results-basic.json from CLI tool to demo/data/results-basic.json
- [X] T007 Create demo/scripts/building.js with canvas rendering setup and drawBuilding() function
- [X] T008 Add room rendering to demo/scripts/building.js (drawRoom, drawHallway, drawExits)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Load and Visualize Pre-Computed Routes (Priority: P1) 🎯 MVP

**Goal**: Display 6-room office layout and animate 2 agents moving along pre-computed patrol routes with room color changes

**Independent Test**: Load demo/index.html in browser, verify building displays, click Play, verify agents animate along routes and rooms change color (yellow→blue→green)

### Implementation for User Story 1

- [X] T009 [US1] Implement buildingLayout loading in demo/scripts/building.js (fetch and parse building.json)
- [X] T010 [US1] Implement results loading in demo/scripts/building.js (fetch and parse results-basic.json)
- [X] T011 [US1] Create demo/scripts/animation.js with AnimationController class (state management, time tracking)
- [X] T012 [US1] Implement agent position calculation in demo/scripts/animation.js (updateAgents method)
- [X] T013 [US1] Implement agent rendering in demo/scripts/animation.js (drawAgents method with colored circles and labels)
- [X] T014 [US1] Add animation loop in demo/scripts/animation.js using requestAnimationFrame()
- [X] T015 [US1] Implement room state tracking in demo/scripts/building.js (pending/in-progress/completed)
- [X] T016 [US1] Update room colors based on agent actions in demo/scripts/building.js
- [X] T017 [US1] Create demo/scripts/metrics.js with metrics display panel (makespan, agent times, path length, coverage)
- [X] T018 [US1] Update metrics panel in demo/scripts/metrics.js when animation loads
- [X] T019 [US1] Wire up basic Play functionality in demo/index.html to start animation

**Checkpoint**: At this point, User Story 1 should be fully functional - building displays, agents animate, rooms change color, metrics show

---

## Phase 4: User Story 2 - Control Animation Playback (Priority: P2)

**Goal**: Add interactive playback controls (play, pause, restart, speed control, timeline scrubber) for animation

**Independent Test**: Load demo, start animation, pause mid-execution, change speed to 2x, scrub timeline to different time, verify agents respond correctly

### Implementation for User Story 2

- [X] T020 [US2] Create demo/scripts/controls.js with playback state management (isPlaying, speed, currentTime)
- [X] T021 [P] [US2] Implement play/pause functionality in demo/scripts/controls.js
- [X] T022 [P] [US2] Implement restart button in demo/scripts/controls.js (reset to time 0)
- [X] T023 [P] [US2] Add speed control slider in demo/index.html (0.5x to 3x range)
- [X] T024 [US2] Implement speed multiplier logic in demo/scripts/controls.js (scale time delta)
- [X] T025 [US2] Add timeline scrubber input in demo/index.html (range 0 to makespan)
- [X] T026 [US2] Implement scrubTo(time) method in demo/scripts/controls.js (jump to specific time)
- [X] T027 [US2] Connect controls to AnimationController in demo/scripts/animation.js
- [X] T028 [US2] Update UI button states in demo/scripts/controls.js (disable/enable based on playback state)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - full playback control over animation

---

## Phase 5: User Story 3 - Compare Different Scenarios (Priority: P3)

**Goal**: Load and switch between different pre-computed scenarios (basic, redundancy, return-to-exit, multi-agent)

**Independent Test**: Load basic scenario, select "Redundancy Scenario" from dropdown, verify display updates to show 3 agents and updated metrics

### Implementation for User Story 3

- [X] T029 [P] [US3] Copy results-redundancy.json from CLI tool to demo/data/results-redundancy.json
- [X] T030 [P] [US3] Copy results-return.json from CLI tool to demo/data/results-return.json
- [X] T031 [P] [US3] Copy results-multi.json from CLI tool to demo/data/results-multi.json
- [X] T032 [US3] Add scenario dropdown menu in demo/index.html (Basic, Redundancy, Return to Exit, Multi-Agent)
- [X] T033 [US3] Implement scenario loading logic in demo/scripts/controls.js (loadScenario method)
- [X] T034 [US3] Update building display when scenario changes in demo/scripts/building.js
- [X] T035 [US3] Reset animation state when scenario switches in demo/scripts/animation.js
- [X] T036 [US3] Update metrics panel when scenario loads in demo/scripts/metrics.js
- [X] T037 [US3] Display current scenario name and description in demo/index.html

**Checkpoint**: All user stories should now be independently functional - can load any scenario and control playback

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [X] T038 [P] Add tooltips for agents in demo/scripts/animation.js (show agent ID, current action, elapsed time on hover)
- [X] T039 [P] Add tooltips for rooms in demo/scripts/building.js (show room ID, inspection status, visiting agents on hover)
- [X] T040 [P] Add error handling for missing/invalid data files in demo/scripts/building.js
- [X] T041 [P] Add loading indicators in demo/index.html while fetching JSON files
- [X] T042 Optimize canvas rendering performance in demo/scripts/building.js and demo/scripts/animation.js
- [X] T043 Test browser compatibility (Chrome, Firefox, Safari, Edge) and fix issues
- [X] T044 Validate against quickstart.md manual testing checklist
- [X] T045 Update demo/README.md with final instructions and troubleshooting

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 AnimationController but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses US1 building/animation and US2 controls but independently testable

### Within Each User Story

- Building components before animation components
- Animation controller before controls
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T003 and T004 can run in parallel (different files)
- T021, T022, T023 can run in parallel (independent control features)
- T029, T030, T031 can run in parallel (copying different scenario files)
- T038, T039, T040, T041 can run in parallel (different enhancement areas)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)

---

## Parallel Example: User Story 1

```bash
# After foundation is ready, these can start together:
Task: "Implement buildingLayout loading in demo/scripts/building.js"
Task: "Implement results loading in demo/scripts/building.js"

# After data loading is done, these rendering tasks can proceed:
Task: "Create demo/scripts/animation.js with AnimationController class"
Task: "Create demo/scripts/metrics.js with metrics display panel"
```

---

## Parallel Example: User Story 2

```bash
# These control features can be developed in parallel:
Task: "Implement play/pause functionality in demo/scripts/controls.js"
Task: "Implement restart button in demo/scripts/controls.js"
Task: "Add speed control slider in demo/index.html"
```

---

## Parallel Example: User Story 3

```bash
# Copy all scenario files at once:
Task: "Copy results-redundancy.json from CLI tool to demo/data/"
Task: "Copy results-return.json from CLI tool to demo/data/"
Task: "Copy results-multi.json from CLI tool to demo/data/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004) - ~1 hour
2. Complete Phase 2: Foundational (T005-T008) - ~2-3 hours
3. Complete Phase 3: User Story 1 (T009-T019) - ~2 days
4. **STOP and VALIDATE**: Open demo/index.html in browser, test animation works
5. Demo the working visualization (MVP complete!)

**Estimated MVP Timeline**: 2-3 days

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (~4 hours)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! - 2-3 days total)
3. Add User Story 2 → Test independently → Deploy/Demo (4-5 days total)
4. Add User Story 3 → Test independently → Deploy/Demo (5-6 days total)
5. Add Polish → Final validation → Production ready (6-7 days total)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (~4 hours)
2. Once Foundational is done:
   - Developer A: User Story 1 (T009-T019)
   - Developer B: User Story 2 (T020-T028) - needs US1 AnimationController interface
   - Developer C: User Story 3 (T029-T037) - needs US1 building/animation components
3. Stories complete and integrate independently
4. Team collaborates on Polish phase

**Note**: True parallel development requires coordination on shared interfaces (AnimationController, building.js exports)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No automated tests (manual browser testing per plan.md)
- Use modern browser dev tools for debugging
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently in browser
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All files use vanilla JavaScript ES6+ (no transpilation needed)
