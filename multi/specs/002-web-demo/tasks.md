# Tasks: Web Demonstration Application

**Input**: Design documents from `/specs/002-web-demo/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/services.md

**Tests**: No explicit test requirements in specification. Tests omitted per task generation rules.

**Organization**: Tasks are grouped by user story (P1-P4) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `web/src/` for web application code
- **Existing CLI**: `src/` at repository root (reused by web app)
- **Static assets**: `web/assets/`
- **Build output**: `web/dist/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and build configuration

- [ ] T001 Install web dependencies (konva, gsap, vite, vitest, playwright)
- [ ] T002 Create vite.config.ts with path aliases to existing src/ directory
- [ ] T003 [P] Create tsconfig.web.json extending base tsconfig.json
- [ ] T004 [P] Create web/index.html entry point
- [ ] T005 [P] Create web/src/main.ts application entry point
- [ ] T006 [P] Create web/assets/styles/main.css with base styles
- [ ] T007 [P] Add npm scripts for dev, build, preview, test to package.json
- [ ] T008 Create web directory structure (components, services, models, utils, assets, tests)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T009 Implement CoordinateMapper utility in web/src/utils/coordinates.ts for graph↔screen conversion
- [ ] T010 [P] Implement AppState class in web/src/models/AppState.ts with observer pattern
- [ ] T011 [P] Create VisualNode interface extending Node in web/src/models/VisualNode.ts
- [ ] T012 [P] Create VisualEdge interface extending Edge in web/src/models/VisualEdge.ts
- [ ] T013 [P] Create VisualRoom interface extending Room in web/src/models/VisualRoom.ts
- [ ] T014 [P] Create CanvasState interface in web/src/models/CanvasState.ts
- [ ] T015 [P] Implement BuildingService in web/src/services/BuildingService.ts (CRUD, validation, export)
- [ ] T016 [P] Implement ValidationService in web/src/services/ValidationService.ts (delegates to CLI validator)
- [ ] T017 [P] Implement StorageService in web/src/services/StorageService.ts (LocalStorage persistence)
- [ ] T018 [P] Copy 4 example JSON files to web/assets/examples/ (basic-6-room, redundancy, return, multi-agent)
- [ ] T019 [P] Implement ExampleService in web/src/services/ExampleService.ts to load examples

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Interactive Building Configuration (Priority: P1) 🎯 MVP

**Goal**: Users can visually design building layouts using canvas with nodes, edges, and rooms

**Independent Test**: Create a 6-room building with nodes and edges, export as JSON, validate against CLI schema

### Implementation for User Story 1

- [ ] T020 [P] [US1] Implement CanvasService.initialize() in web/src/services/CanvasService.ts to create Konva stage
- [ ] T021 [P] [US1] Implement NodeRenderer component in web/src/components/canvas/NodeRenderer.ts to draw nodes
- [ ] T022 [P] [US1] Implement EdgeRenderer component in web/src/components/canvas/EdgeRenderer.ts to draw edges
- [ ] T023 [P] [US1] Implement RoomRenderer component in web/src/components/canvas/RoomRenderer.ts to draw room labels
- [ ] T024 [US1] Implement CanvasService.renderBuilding() to render complete building using renderers (depends on T020-T023)
- [ ] T025 [US1] Implement BuildingCanvas controller in web/src/components/canvas/BuildingCanvas.ts coordinating renderers
- [ ] T026 [P] [US1] Create DrawingTools toolbar component in web/src/components/toolbar/DrawingTools.ts
- [ ] T027 [P] [US1] Create PropertyEditor component in web/src/components/toolbar/PropertyEditor.ts
- [ ] T028 [US1] Implement click-to-add node functionality in BuildingCanvas with mode handling
- [ ] T029 [US1] Implement drag-to-connect edge functionality in BuildingCanvas
- [ ] T030 [US1] Implement node drag-and-move functionality updating graph coordinates
- [ ] T031 [US1] Implement click-to-select node/edge with selection state updates
- [ ] T032 [US1] Implement property editing panel showing selected element properties
- [ ] T033 [US1] Add validation feedback display using ValidationService
- [ ] T034 [US1] Implement BuildingService.addNode() with ID generation
- [ ] T035 [US1] Implement BuildingService.addEdge() with validation
- [ ] T036 [US1] Implement BuildingService.addRoom() associating door with room
- [ ] T037 [US1] Implement BuildingService.exportToJSON() and downloadFile()
- [ ] T038 [US1] Implement BuildingService.importFromFile() with JSON parsing
- [ ] T039 [US1] Add delete functionality for nodes/edges/rooms with confirmation
- [ ] T040 [US1] Implement zoom controls (in/out/fit-to-content) in CanvasService
- [ ] T041 [US1] Implement pan functionality with mouse drag in CanvasService
- [ ] T042 [US1] Create main editor UI integrating canvas, toolbar, and property panel in web/src/app.ts

**Checkpoint**: User Story 1 complete - Users can design buildings and export valid JSON files

---

## Phase 4: User Story 2 - Visualize Optimization Results (Priority: P2)

**Goal**: Users see animated agent movements on building layout with performance metrics

**Independent Test**: Load pre-computed results JSON, play animation, verify agents move along routes at 30 FPS

### Implementation for User Story 2

- [ ] T043 [P] [US2] Create AnimationState interface in web/src/models/AnimationState.ts
- [ ] T044 [P] [US2] Create AnimatedAgent interface in web/src/models/AnimatedAgent.ts
- [ ] T045 [P] [US2] Create ConflictMarker interface in web/src/models/ConflictMarker.ts
- [ ] T046 [US2] Implement OptimizationService in web/src/services/OptimizationService.ts calling MissionPlanner
- [ ] T047 [US2] Implement AnimationService.initialize() in web/src/services/AnimationService.ts creating GSAP timeline
- [ ] T048 [US2] Implement AnimationService.buildAgentTimeline() converting Route actions to GSAP tweens
- [ ] T049 [US2] Implement AgentAnimator component in web/src/components/animation/AgentAnimator.ts rendering agent shapes
- [ ] T050 [US2] Implement AnimationService.play/pause/stop controls
- [ ] T051 [US2] Implement AnimationService.seek() for timeline scrubbing
- [ ] T052 [US2] Implement AnimationService.setSpeed() for playback rate control
- [ ] T053 [US2] Create AnimationController component in web/src/components/animation/AnimationController.ts with play/pause/speed UI
- [ ] T054 [US2] Create TimelineView component in web/src/components/animation/TimelineView.ts with scrubber
- [ ] T055 [US2] Implement room state visualization (pending/in-progress/completed colors) in RoomRenderer
- [ ] T056 [US2] Implement conflict detection display using existing detectRoomConflicts() from CLI
- [ ] T057 [US2] Add conflict markers on canvas when multiple agents in same room
- [ ] T058 [P] [US2] Create MetricsPanel component in web/src/components/panels/MetricsPanel.ts displaying makespan, coverage, load balance
- [ ] T059 [US2] Implement AnimationService event system (onTimeUpdate, onComplete, onAgentAction)
- [ ] T060 [US2] Connect AnimationController to AnimationService for playback control
- [ ] T061 [US2] Add agent hover tooltips showing agent ID, action, time
- [ ] T062 [US2] Add room hover tooltips showing inspection status and agents
- [ ] T063 [US2] Integrate animation view with results data loading
- [ ] T064 [US2] Add view toggle between editor mode and animation mode in UI

**Checkpoint**: User Story 2 complete - Users can watch animated patrol routes with metrics

---

## Phase 5: User Story 3 - Configure and Run Missions (Priority: P3)

**Goal**: Users configure mission parameters through forms and trigger optimization

**Independent Test**: Fill mission form, click optimize, verify results load and animation starts

### Implementation for User Story 3

- [ ] T065 [P] [US3] Create MissionConfig interface in web/src/models/MissionConfig.ts
- [ ] T066 [P] [US3] Create UIState interface in web/src/models/UIState.ts for modal/panel state
- [ ] T067 [P] [US3] Create MissionForm component in web/src/components/forms/MissionForm.ts
- [ ] T068 [P] [US3] Create RoomSelector component in web/src/components/forms/RoomSelector.ts for multi-select
- [ ] T069 [US3] Implement agent count input with validation (min 1) in MissionForm
- [ ] T070 [US3] Implement start location dropdown populated from EXIT/CORRIDOR nodes in MissionForm
- [ ] T071 [US3] Implement redundant rooms multi-select using RoomSelector
- [ ] T072 [US3] Implement return-to-exit checkbox in MissionForm
- [ ] T073 [US3] Implement algorithm selector (ILP/Hungarian/Greedy) in MissionForm
- [ ] T074 [US3] Implement ValidationService.validateMissionConfig() checking feasibility
- [ ] T075 [US3] Add form validation with error display before optimization
- [ ] T076 [US3] Implement "Optimize Routes" button triggering OptimizationService.optimize()
- [ ] T077 [US3] Add optimization progress indicator with loading state
- [ ] T078 [US3] Implement error handling for optimization failures with actionable messages
- [ ] T079 [US3] Add automatic transition to animation view on successful optimization
- [ ] T080 [US3] Implement OptimizationService.checkFeasibility() for pre-flight validation
- [ ] T081 [US3] Add mission configuration modal dialog with open/close controls
- [ ] T082 [US3] Integrate mission form with main UI workflow

**Checkpoint**: User Story 3 complete - Users can configure and run optimizations from web UI

---

## Phase 6: User Story 4 - Load and Save Scenarios (Priority: P4)

**Goal**: Users save scenarios to LocalStorage and load example templates

**Independent Test**: Save current scenario, reload page, load saved scenario and verify building restored

### Implementation for User Story 4

- [ ] T083 [P] [US4] Create SavedScenario interface in web/src/models/SavedScenario.ts
- [ ] T084 [P] [US4] Create ScenarioPanel component in web/src/components/panels/ScenarioPanel.ts
- [ ] T085 [US4] Implement StorageService.saveScenario() with JSON serialization to LocalStorage
- [ ] T086 [US4] Implement StorageService.loadScenario() with JSON parsing from LocalStorage
- [ ] T087 [US4] Implement StorageService.listScenarios() sorted by update time
- [ ] T088 [US4] Implement StorageService.deleteScenario() with confirmation
- [ ] T089 [US4] Implement StorageService.getStorageUsage() showing bytes used
- [ ] T090 [US4] Create save scenario dialog with name and description inputs
- [ ] T091 [US4] Create load scenario list UI showing saved and example scenarios
- [ ] T092 [US4] Implement scenario metadata (name, tags, created/updated timestamps)
- [ ] T093 [US4] Add "Save Scenario" button in toolbar triggering save dialog
- [ ] T094 [US4] Add "Load Scenario" button opening scenario list panel
- [ ] T095 [US4] Implement ExampleService.listExamples() returning 4 example scenarios
- [ ] T096 [US4] Implement ExampleService.loadExample() with dynamic import of JSON
- [ ] T097 [US4] Add example scenario cards in load dialog with descriptions
- [ ] T098 [US4] Implement scenario loading restoring building, config, and results if available
- [ ] T099 [US4] Add storage usage indicator in scenario panel
- [ ] T100 [US4] Handle QuotaExceededError with helpful message and cleanup suggestion
- [ ] T101 [US4] Implement delete scenario with confirmation dialog

**Checkpoint**: User Story 4 complete - Users can persist and restore scenarios

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T102 [P] Add keyboard shortcuts (Delete for delete, Ctrl+Z for undo, Escape for deselect)
- [ ] T103 [P] Add grid display and snap-to-grid functionality in CanvasService
- [ ] T104 [P] Implement undo/redo stack for building editor operations
- [ ] T105 [P] Add tooltips and help text for all UI controls
- [ ] T106 [P] Create ValidationPanel component showing validation errors with icons
- [ ] T107 [P] Implement notification system for success/error messages in UIState
- [ ] T108 [P] Add color-coded node types (green EXIT, blue CORRIDOR, orange DOOR)
- [ ] T109 [P] Optimize Konva layer caching for static building elements
- [ ] T110 [P] Add responsive canvas resize on window resize
- [ ] T111 [P] Implement edge labels showing base time and clearance time
- [ ] T112 [P] Add agent color assignment (10 distinct colors) in AnimationService
- [ ] T113 [P] Implement conflict highlighting in red with warning icons
- [ ] T114 [P] Add summary statistics panel (nodes, edges, rooms count)
- [ ] T115 [P] Polish CSS styling for all panels and controls in web/assets/styles/
- [ ] T116 [P] Add loading states for async operations (import, export, optimize)
- [ ] T117 [P] Implement error boundaries for graceful failure handling
- [ ] T118 [P] Add browser compatibility check for required features (Canvas, LocalStorage)
- [ ] T119 Create user documentation in web/README.md with screenshots
- [ ] T120 Add deployment instructions for static hosting (GitHub Pages, Netlify)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - **Requires** User Story 1 canvas rendering complete
  - User Story 3 (P3): Can start after Foundational - **Requires** User Story 2 OptimizationService
  - User Story 4 (P4): Can start after Foundational - Independent of other stories
- **Polish (Phase 7)**: Depends on desired user stories being complete

### User Story Dependencies

```
Phase 1 (Setup)
     ↓
Phase 2 (Foundational) ← BLOCKING
     ↓
     ├─→ User Story 1 (P1) ✓ MVP - Building Editor
     │        ↓
     ├─→ User Story 2 (P2) - Animation (needs US1 canvas)
     │        ↓
     ├─→ User Story 3 (P3) - Mission Config (needs US2 optimization)
     │
     └─→ User Story 4 (P4) - Scenarios (independent)
          ↓
Phase 7 (Polish)
```

### Within Each User Story

- **US1**: Renderers → Canvas controller → Drawing tools → CRUD operations → Export
- **US2**: Animation models → AnimationService → Agent animator → Controls → Metrics
- **US3**: Form components → Validation → Optimize button → Error handling
- **US4**: Storage service → Scenario panel → Save/load dialogs → Examples

### Parallel Opportunities

- **Phase 1**: All tasks T001-T008 can run in parallel
- **Phase 2**: Tasks T010-T019 marked [P] can run in parallel after T009
- **Within US1**: T020-T023 (renderers), T026-T027 (toolbar) can run in parallel
- **Within US2**: T043-T045 (models), T058 (metrics panel) can run in parallel
- **Within US3**: T065-T068 (form models/components) can run in parallel
- **Within US4**: T083-T084 (models/components) can run in parallel
- **Phase 7**: Most polish tasks T102-T118 can run in parallel

**Note**: While US2 depends on US1, and US3 depends on US2, within each story many tasks can be parallelized by different developers working on different files.

---

## Parallel Example: User Story 1

```bash
# After Foundational phase completes, launch renderers in parallel:
Task T020: "Implement CanvasService.initialize() in web/src/services/CanvasService.ts"
Task T021: "Implement NodeRenderer in web/src/components/canvas/NodeRenderer.ts"
Task T022: "Implement EdgeRenderer in web/src/components/canvas/EdgeRenderer.ts"
Task T023: "Implement RoomRenderer in web/src/components/canvas/RoomRenderer.ts"

# Then launch toolbar components in parallel:
Task T026: "Create DrawingTools in web/src/components/toolbar/DrawingTools.ts"
Task T027: "Create PropertyEditor in web/src/components/toolbar/PropertyEditor.ts"
```

---

## Parallel Example: User Story 2

```bash
# Launch animation models in parallel:
Task T043: "Create AnimationState in web/src/models/AnimationState.ts"
Task T044: "Create AnimatedAgent in web/src/models/AnimatedAgent.ts"
Task T045: "Create ConflictMarker in web/src/models/ConflictMarker.ts"

# Launch independent UI component:
Task T058: "Create MetricsPanel in web/src/components/panels/MetricsPanel.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T019) - **CRITICAL**
3. Complete Phase 3: User Story 1 (T020-T042)
4. **STOP and VALIDATE**:
   - Create a 6-room building visually
   - Export as JSON
   - Import in CLI tool: `npm run cli -- validate exported-building.json`
   - Verify validation passes
5. Deploy web app to GitHub Pages or Netlify

**MVP Deliverable**: Interactive building editor with JSON export compatible with CLI

### Incremental Delivery

1. **Foundation** (Phases 1-2): Setup + core services → 2-3 days
2. **MVP** (Phase 3): User Story 1 → Test → Deploy → **Demo building editor** → 3-4 days
3. **Iteration 2** (Phase 4): User Story 2 → Test → Deploy → **Demo animations** → 3-4 days
4. **Iteration 3** (Phase 5): User Story 3 → Test → Deploy → **Demo end-to-end workflow** → 2-3 days
5. **Iteration 4** (Phase 6): User Story 4 → Test → Deploy → **Demo scenarios** → 1-2 days
6. **Polish** (Phase 7): Cross-cutting improvements → 2-3 days

**Total Estimated Time**: 13-19 days (2-3 weeks)

### Parallel Team Strategy

With 3 developers after Foundational phase completes:

1. **Developer A**: User Story 1 (Building Editor) - Priority 1
2. **Developer B**: User Story 4 (Scenarios) - Independent, can work in parallel
3. **Developer C**: Foundational polish and documentation

Once US1 completes:
4. **Developer A**: User Story 2 (Animation) - Depends on US1
5. **Developer B**: Continue US4 or start polish tasks

Once US2 completes:
6. **Developer A**: User Story 3 (Mission Config) - Depends on US2

This maximizes parallelism while respecting dependencies.

---

## Testing Strategy

### Manual Testing Checkpoints

After each user story phase:

**US1 Testing**:
1. Open web app in Chrome, Firefox, Safari
2. Create new building with 2 exits, 4 corridors, 6 doors, 6 rooms
3. Connect nodes with edges
4. Set room properties (inspection time, redundancy)
5. Export JSON
6. Import in CLI and validate: `npm run cli -- validate exported.json`
7. Verify no validation errors

**US2 Testing**:
1. Load pre-computed results from `results.json`
2. Click "Play" and verify agents move smoothly
3. Check animation runs at 30 FPS (use browser performance tools)
4. Hover over agents and rooms, verify tooltips appear
5. Check metrics panel shows correct makespan, coverage
6. Scrub timeline, verify agents jump to correct positions
7. Test pause, resume, speed controls

**US3 Testing**:
1. Load building from US1 test
2. Open mission configuration
3. Set agent count to 3
4. Select redundant rooms
5. Enable return-to-exit
6. Click "Optimize Routes"
7. Verify progress indicator appears
8. Verify results load and animation auto-starts
9. Test error handling with invalid config (0 agents)

**US4 Testing**:
1. Create or load a building
2. Click "Save Scenario" with name "Test Office"
3. Reload page (Ctrl+R)
4. Click "Load Scenario"
5. Verify "Test Office" appears in list
6. Load it and verify building restored
7. Load each of 4 example scenarios
8. Check storage usage indicator
9. Delete a scenario and verify removal

### Browser Compatibility Testing

Test in:
- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)

Verify:
- Canvas rendering works
- Drag-and-drop works
- LocalStorage works
- Animations smooth at 30 FPS

---

## Notes

- **[P] tasks**: Different files, no dependencies, can run in parallel
- **[Story] labels**: US1, US2, US3, US4 map to spec.md user stories
- **File paths**: All paths explicitly specified for each task
- **Dependencies**: US2 needs US1 canvas, US3 needs US2 optimization, US4 is independent
- **CLI Integration**: BuildingService, OptimizationService, ValidationService delegate to existing CLI code via imports
- **No test tasks**: Specification doesn't require automated tests; manual testing sufficient
- **Commit strategy**: Commit after completing each user story phase or logical task group
- **Validation**: Use existing CLI validator to ensure compatibility at each checkpoint

**Total Tasks**: 120 tasks across 7 phases
- Phase 1 (Setup): 8 tasks
- Phase 2 (Foundational): 11 tasks
- Phase 3 (US1 - MVP): 23 tasks
- Phase 4 (US2): 22 tasks
- Phase 5 (US3): 18 tasks
- Phase 6 (US4): 19 tasks
- Phase 7 (Polish): 19 tasks

**Estimated Timeline**: 2-3 weeks for full implementation (all 4 user stories + polish)
**MVP Timeline**: 5-7 days for User Story 1 only (building editor)
