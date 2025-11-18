# Tasks: Multi-Floor Building Inspection Simulation

**Input**: Design documents from `/specs/001-multi-floor-inspection/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - not included per research simulation pattern

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: Repository root (multi_floor_building_inspection.py)
- Paths shown below use repository root structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create ./output/ directory for generated visualizations
- [x] T002 [P] Verify Python 3.9+ installed and numpy/matplotlib dependencies available
- [x] T003 [P] Review F1.pdf, F3.pdf, F4.pdf floor plans to prepare for room transcription

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 [P] Create Room dataclass with area and door_position properties in multi_floor_building_inspection.py
- [x] T005 [P] Create Floor dataclass with get_room_by_name() method in multi_floor_building_inspection.py
- [x] T006 [P] Create Stairwell dataclass with get_vertical_distance() and get_transition_time() methods in multi_floor_building_inspection.py
- [x] T007 [P] Create Person dataclass with add_waypoint() and move_to() methods in multi_floor_building_inspection.py
- [x] T008 [P] Implement sweep_time_gt() function (copy from complex_single_level_building_inspection.py) in multi_floor_building_inspection.py
- [x] T009 [P] Implement distance() helper function for Euclidean distance calculation in multi_floor_building_inspection.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Multi-Floor Inspection Simulation (Priority: P1) 🎯 MVP

**Goal**: 2-person team inspecting 3-floor building with greedy assignment and visualization

**Independent Test**: Run simulation with default parameters, verify all rooms inspected exactly once, visualization shows 3 floors with paths and stairwell transitions

### Room Data Transcription for User Story 1

- [x] T010 [P] [US1] Transcribe F1 rooms from F1.pdf (Toilet, Coffee, Public Activity Area, Entrance, Stairwell, self-service, Equipment) with dimensions in multi_floor_building_inspection.py __init__()
- [x] T011 [P] [US1] Transcribe F3 rooms from F3.pdf (Multi-media, Specialty Museum, Erotic reading materials, Children's Exhibition Room, parent-child interaction, Stairwell, Toilet) in multi_floor_building_inspection.py __init__()
- [x] T012 [P] [US1] Transcribe F4 rooms from F4.pdf (Office x2, Meeting x2, Professional bookstore, Stairwell, Toilet) in multi_floor_building_inspection.py __init__()
- [x] T013 [US1] Create 3 Floor instances (F1, F3, F4) with transcribed rooms in multi_floor_building_inspection.py __init__()
- [x] T014 [US1] Create Stairwell instance connecting F1↔F3↔F4 with positions at ~5000mm (5m) from left edge in multi_floor_building_inspection.py __init__()

### Path Finding and Assignment for User Story 1

- [x] T015 [US1] Implement get_path_distance() method for same-floor corridor distance in multi_floor_building_inspection.py
- [x] T016 [US1] Implement get_path_distance_3d() method for multi-floor distance via stairwell in multi_floor_building_inspection.py
- [x] T017 [US1] Implement greedy_assign() method with 3D distance heuristic (assign nearest room to person with lowest total time) in multi_floor_building_inspection.py
- [x] T018 [US1] Add stairwell transition logic in greedy_assign() to update person floor and add waypoints in multi_floor_building_inspection.py
- [x] T019 [US1] Implement find_nearest_exit() method to return closest exit for personnel in multi_floor_building_inspection.py
- [x] T020 [US1] Add return-to-exit logic in greedy_assign() after all rooms assigned in multi_floor_building_inspection.py

### Visualization for User Story 1

- [x] T021 [US1] Implement visualize() method with matplotlib 3-floor vertical stacking (figsize=(18, 24), 3 subplots) in multi_floor_building_inspection.py
- [x] T022 [US1] Implement _draw_floor_layout() helper to render room rectangles with pastel colors and labels in multi_floor_building_inspection.py
- [x] T023 [US1] Add door wedge rendering (matplotlib.patches.Wedge) with correct angles in _draw_floor_layout() in multi_floor_building_inspection.py
- [x] T024 [US1] Implement _draw_paths_on_floor() to trace personnel paths (red for Person 1, blue for Person 2) in multi_floor_building_inspection.py
- [x] T025 [US1] Add stairwell transition visual markers (dashed purple lines between subplots) in visualize() in multi_floor_building_inspection.py
- [x] T026 [US1] Add room inspection time labels (room.name + time) on visualization in _draw_floor_layout() in multi_floor_building_inspection.py
- [x] T027 [US1] Add START/END markers for personnel paths in _draw_paths_on_floor() in multi_floor_building_inspection.py
- [x] T028 [US1] Save visualization to ./output/multi_floor_building_inspection.png at 300 DPI in visualize() in multi_floor_building_inspection.py

### Text Output for User Story 1

- [x] T029 [US1] Implement print_results() method to display personnel paths, distances, times in multi_floor_building_inspection.py
- [x] T030 [US1] Add total distance and max completion time summary to print_results() in multi_floor_building_inspection.py

### Main Execution for User Story 1

- [x] T031 [US1] Create main() function to instantiate MultiFloorBuildingInspection class in multi_floor_building_inspection.py
- [x] T032 [US1] Call greedy_assign() with default start positions (both on F1 entrance) in main() in multi_floor_building_inspection.py
- [x] T033 [US1] Call print_results() and visualize() in main() in multi_floor_building_inspection.py
- [x] T034 [US1] Add if __name__ == "__main__" guard and main() invocation in multi_floor_building_inspection.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently - Run python3 multi_floor_building_inspection.py to verify

---

## Phase 4: User Story 2 - Optimization Strategy Comparison (Priority: P2)

**Goal**: Compare greedy vs. load-balanced strategies to analyze makespan differences

**Independent Test**: Run simulation with both strategies on same building config, verify different room assignments and time metrics displayed

### Load-Balanced Strategy for User Story 2

- [ ] T035 [US2] Implement load_balanced_assign() method with makespan minimization heuristic in multi_floor_building_inspection.py
- [ ] T036 [US2] Add logic to assign rooms to person with lower current total time (balance workload) in load_balanced_assign() in multi_floor_building_inspection.py
- [ ] T037 [US2] Reuse get_path_distance_3d() and return-to-exit logic from greedy_assign() in load_balanced_assign() in multi_floor_building_inspection.py

### Strategy Comparison Output for User Story 2

- [ ] T038 [US2] Create compare_strategies() method to run both greedy_assign() and load_balanced_assign() in multi_floor_building_inspection.py
- [ ] T039 [US2] Implement print_comparison() method to display side-by-side metrics (total time, max time, distance, room distribution) in multi_floor_building_inspection.py
- [ ] T040 [US2] Update main() to optionally call compare_strategies() when strategy comparison flag is set in multi_floor_building_inspection.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - Verify both strategies produce different results

---

## Phase 5: User Story 3 - Configurable Building Parameters (Priority: P3)

**Goal**: Enable parameter modification without code editing for sensitivity analysis

**Independent Test**: Modify configuration parameters (personnel count, speeds, complexity), verify simulation executes with updated values

### Configurable Parameters for User Story 3

- [ ] T041 [P] [US3] Add corridor_speed and stairwell_speed_factor parameters to greedy_assign() signature in multi_floor_building_inspection.py
- [ ] T042 [P] [US3] Add corridor_speed and stairwell_speed_factor parameters to load_balanced_assign() signature in multi_floor_building_inspection.py
- [ ] T043 [US3] Update all speed calculations to use configurable parameters instead of hardcoded values in greedy_assign() and load_balanced_assign() in multi_floor_building_inspection.py
- [ ] T044 [US3] Add start_positions parameter (list of (x, y, floor) tuples) to greedy_assign() and load_balanced_assign() in multi_floor_building_inspection.py
- [ ] T045 [US3] Implement greedy_assign_n_personnel() method to support variable personnel count (2+) in multi_floor_building_inspection.py
- [ ] T046 [US3] Update main() to demonstrate parameter configuration examples (commented out) in multi_floor_building_inspection.py

**Checkpoint**: All user stories should now be independently functional - Parameter customization works without code changes to core logic

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T047 [P] Add validation checks for room count (all rooms assigned exactly once) in greedy_assign() in multi_floor_building_inspection.py
- [ ] T048 [P] Add path continuity validation (no gaps) in visualize() in multi_floor_building_inspection.py
- [ ] T049 [P] Add error handling for stairwell_speed_factor == 0 (raise ValueError) in greedy_assign() in multi_floor_building_inspection.py
- [ ] T050 Update README.md with Multi-Floor Building Inspection section (usage, parameters, output)
- [ ] T051 Add docstrings to all public methods (greedy_assign, load_balanced_assign, visualize, print_results) in multi_floor_building_inspection.py
- [ ] T052 Run quickstart.md validation checklist (verify all acceptance criteria pass)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Reuses US1 infrastructure but is independently testable
  - User Story 3 (P3): Can start after Foundational - Extends US1/US2 with parameterization but is independently testable
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (FULLY INDEPENDENT)
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Reuses path finding from US1 but adds independent strategy (MOSTLY INDEPENDENT, can demo side-by-side)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Extends US1/US2 with parameterization (INDEPENDENT extension, works with either strategy)

### Within Each User Story

**User Story 1 (P1)**:
1. Room transcription tasks (T010-T012) can run in parallel
2. T013-T014 depend on transcription complete
3. Path finding (T015-T020) depends on Floor/Stairwell/Person entities
4. Visualization (T021-T028) can develop in parallel with path finding (different methods)
5. Text output (T029-T030) depends on Person entities
6. Main execution (T031-T034) depends on all above complete

**User Story 2 (P2)**:
1. Load-balanced implementation (T035-T037) can start after US1 path finding complete (reuse)
2. Comparison output (T038-T040) depends on both strategies implemented

**User Story 3 (P3)**:
1. Parameter additions (T041-T044) can run in parallel
2. N-personnel method (T045) depends on parameter additions
3. Main update (T046) depends on all parameter tasks

### Parallel Opportunities

- **Setup Phase**: All tasks (T001-T003) can run in parallel
- **Foundational Phase**: All dataclass/function tasks (T004-T009) can run in parallel
- **User Story 1 Room Transcription**: T010, T011, T012 can run in parallel (different floors)
- **User Story 1 Visualization**: T022-T028 can develop in parallel with T015-T020 (different methods)
- **User Story 3 Parameters**: T041, T042, T044 can run in parallel (different method signatures)
- **Polish Phase**: T047, T048, T049, T051 can run in parallel (different validation/doc tasks)

---

## Parallel Example: User Story 1

```bash
# Launch room transcription in parallel:
Task: "Transcribe F1 rooms from F1.pdf..."  # T010
Task: "Transcribe F3 rooms from F3.pdf..."  # T011
Task: "Transcribe F4 rooms from F4.pdf..."  # T012

# Once transcription done, launch floor creation:
Task: "Create 3 Floor instances..."  # T013
Task: "Create Stairwell instance..."  # T014

# Then launch path finding AND visualization in parallel:
Task: "Implement get_path_distance()..."  # T015 (path finding track)
Task: "Implement visualize() method..."   # T021 (visualization track)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T009) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T010-T034)
4. **STOP and VALIDATE**: Run python3 multi_floor_building_inspection.py
   - Verify all rooms inspected exactly once
   - Check visualization shows 3 floors with paths
   - Confirm stairwell transitions visible
5. Deploy/demo if ready (MVP complete!)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (T010-T034) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (T035-T040) → Test independently → Deploy/Demo (Strategy comparison enabled)
4. Add User Story 3 (T041-T046) → Test independently → Deploy/Demo (Full parameterization)
5. Polish (T047-T052) → Final validation → Release

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T009)
2. Once Foundational is done:
   - Developer A: User Story 1 (T010-T034)
   - Developer B: User Story 2 (T035-T040) - waits for US1 path finding, then proceeds
   - Developer C: User Story 3 (T041-T046) - waits for US1/US2, then proceeds
3. Stories complete and integrate independently

**Recommended**: Single developer should do MVP-first (US1 only), then add US2, then US3

---

## Notes

- [P] tasks = different files/methods, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No automated tests per research simulation pattern (visual validation)
- Commit after each logical group (e.g., after T009, after T034, after T040, etc.)
- Stop at any checkpoint to validate story independently
- Room count: Expected ~17 rooms total (F1: 7, F3: 7, F4: 3 - adjust based on actual PDF content)
- Avoid: vague tasks, same method conflicts, cross-story dependencies that break independence
