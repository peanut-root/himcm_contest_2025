# Feature Specification: Multi-Floor Building Inspection Simulation

**Feature Branch**: `001-multi-floor-inspection`
**Created**: 2025-11-17
**Status**: Draft
**Input**: User description: "create a simulation demo similar to that in complex_single_level_building_inspection.py but with differences: new demo has a 3-floor building, different floors connected via stairs, each floor can be referenced from pdf files within docs folder and each room can use the corresponding name in the pdf file"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Multi-Floor Inspection Simulation (Priority: P1)

A researcher needs to simulate a 2-person team inspecting a 3-floor building to optimize room assignment and minimize total inspection time. The simulation should model realistic movement between floors via stairwells and produce a visual representation of the inspection paths.

**Why this priority**: This is the MVP - it delivers the core value of extending single-floor simulation to multi-floor scenarios with proper vertical movement modeling. Without this, the feature provides no value.

**Independent Test**: Can be fully tested by running the simulation with default parameters on the 3-floor building (F1, F3, F4 from PDFs) and verifying that both personnel paths are generated, all rooms are inspected exactly once, and visualization shows complete paths including stairwell transitions.

**Acceptance Scenarios**:

1. **Given** a 3-floor building with rooms from F1.pdf, F3.pdf, F4.pdf, **When** the simulation runs with 2 personnel starting at designated entry points, **Then** all rooms across all three floors are assigned to personnel with no room inspected twice or missed
2. **Given** personnel assigned to rooms on different floors, **When** path calculation occurs, **Then** stairwell transitions are included with appropriate time penalties for vertical movement
3. **Given** completed simulation, **When** results are generated, **Then** visualization shows each floor layout with room names from PDFs, personnel paths traced with sequence numbers, and stairwell connections clearly marked
4. **Given** simulation execution, **When** time calculations are performed, **Then** total time includes horizontal movement (corridors), vertical movement (stairwells at reduced speed), and room inspection times based on complexity

---

### User Story 2 - Optimization Strategy Comparison (Priority: P2)

A researcher wants to compare different room assignment strategies (greedy nearest-neighbor vs. load-balanced) to determine which minimizes the maximum completion time (makespan) for multi-floor building inspection.

**Why this priority**: This builds on P1 by enabling comparative analysis of optimization algorithms, which is valuable for research but not essential for basic simulation functionality.

**Independent Test**: Can be tested by running the same 3-floor building configuration with both strategies and verifying that each produces different room assignments with corresponding time/distance metrics displayed for comparison.

**Acceptance Scenarios**:

1. **Given** a 3-floor building configuration, **When** the simulation runs with greedy strategy, **Then** rooms are assigned based on nearest available room to current personnel position
2. **Given** the same building configuration, **When** the simulation runs with load-balanced strategy, **Then** rooms are assigned to minimize the maximum completion time between the two personnel
3. **Given** both strategies have been executed, **When** results are displayed, **Then** side-by-side comparison shows total time, max time, distance per person, and room distribution for each strategy

---

### User Story 3 - Configurable Building Parameters (Priority: P3)

A researcher wants to modify building parameters (number of personnel, starting positions, movement speeds, room complexity factors) without editing code to explore sensitivity analysis and "what-if" scenarios.

**Why this priority**: This enhances usability and research flexibility but is not essential for demonstrating the multi-floor simulation capability.

**Independent Test**: Can be tested by modifying configuration parameters (e.g., change personnel count from 2 to 3, adjust corridor speed from 1.5 m/s to 2.0 m/s) and verifying that simulation executes correctly with updated values reflected in results.

**Acceptance Scenarios**:

1. **Given** a configuration file or function parameters, **When** user specifies personnel count, **Then** simulation assigns all rooms across the 3 floors to the specified number of personnel
2. **Given** adjustable movement speeds, **When** user sets corridor speed and stairwell speed multiplier, **Then** all time calculations reflect the updated speeds
3. **Given** room complexity adjustments, **When** user modifies complexity factors for specific room types, **Then** inspection times are recalculated using the updated factors

---

### Edge Cases

- What happens when all rooms are on a single floor (degenerate case where stairwells are unused)?
- How does the system handle buildings where some floors have no exit (must use stairwells to reach exit on another floor)?
- What happens if personnel start on different floors (F1 vs F4)?
- How are ties handled when two personnel are equidistant from the nearest unassigned room?
- What happens when stairwell speed multiplier is set to 0 (infinite time penalty - should error or warn)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST simulate a 3-floor building structure with floors corresponding to F1.pdf, F3.pdf, and F4.pdf from the docs/ folder
- **FR-002**: System MUST extract room names, dimensions, and door positions from the PDF floor plans and use them in the simulation
- **FR-003**: System MUST model stairwell locations that connect the three floors with explicit vertical transition times
- **FR-004**: System MUST assign all rooms across all three floors to 2 personnel such that each room is inspected exactly once
- **FR-005**: System MUST calculate inspection time for each room using the sweep_time_gt formula incorporating area, visibility, halt probability, and complexity factor
- **FR-006**: System MUST calculate path distance including both horizontal corridor movement and vertical stairwell movement
- **FR-007**: System MUST apply a reduced speed factor for stairwell vertical movement compared to horizontal corridor movement (default: 0.5x)
- **FR-008**: System MUST track each personnel's complete path as a sequence of waypoints from start → rooms → stairwells → exit
- **FR-009**: System MUST calculate total time for each personnel as sum of movement time and inspection time
- **FR-010**: System MUST support greedy room assignment strategy (assign nearest unassigned room to personnel with lowest current total time)
- **FR-011**: System MUST generate visualization output showing all three floors with room layouts, personnel paths, stairwell connections, and exits
- **FR-012**: System MUST display room names from PDFs on the visualization with inspection times shown
- **FR-013**: System MUST mark stairwell transitions clearly in the visualization with different styling from regular corridor movement
- **FR-014**: System MUST output text results including personnel assignments, distances, times, and completion statistics
- **FR-015**: System MUST identify and return each personnel to the nearest exit after completing all assigned room inspections

### Assumptions

- **A-001**: The building has a consistent stairwell location that connects all three floors (inferred from typical building architecture shown in PDFs)
- **A-002**: Personnel can only move between floors via designated stairwells, not via elevators or other means
- **A-003**: Movement speed on corridors defaults to 1.5 m/s (matching existing single-level simulation)
- **A-004**: Stairwell vertical movement speed is 50% of corridor speed (0.75 m/s) due to climbing effort
- **A-005**: Floor dimensions use millimeter measurements from PDFs converted to meters (divide by 1000)
- **A-006**: Room complexity factors follow USAR standards: 1.0 (empty), 1.5 (furnished), 1.8 (equipment-heavy)
- **A-007**: Personnel start at building entry points (assumed to be on F1 based on typical building design)
- **A-008**: Exit locations are on F1 (Entrance) and potentially via stairwells to other floor exits

### Key Entities

- **Floor**: Represents a single level of the building (F1, F3, or F4), contains rooms, corridors, and stairwell access points. Attributes: floor identifier, floor height offset, room collection, corridor waypoints, exit locations
- **Room**: Represents an inspectable space within the building. Attributes: name (from PDF), floor assignment, dimensions (width, height in meters), door position and orientation, complexity factor (1.0-1.8), calculated area
- **Stairwell**: Represents vertical connection between floors. Attributes: location coordinates on each connected floor, vertical distance (floor height), connected floor pairs (F1↔F3, F3↔F4)
- **Person**: Represents an inspection team member. Attributes: unique ID, current position (x, y, floor), assigned rooms list, path waypoints (including floor transitions), total distance traveled, total time elapsed
- **Path Segment**: Represents a portion of personnel movement. Attributes: start position, end position, segment type (corridor/stairwell), distance, time required, floor transition indicator

**For simulation features**: Reference floor plan PDFs from `docs/` folder and specify:

- **Floor identification**: F1 (Floor 1), F3 (Floor 3), F4 (Floor 4) corresponding to F1.pdf, F3.pdf, F4.pdf
- **Room types and complexity factors**:
  - 1.0 (empty): Toilet, Stairwell, Entrance, parent-child interaction
  - 1.5 (furnished): Public Activity Area, Cafeteria, Multipurpose Classroom, Children's Exhibition Room, Professional bookstore, Meeting rooms, Office
  - 1.8 (equipment-heavy): Storage Room, Kitchen, Backstage Equipment Room, Equipment, self-service, Coffee, Multi-media, Specialty Museum, Erotic reading materials
- **Stairwell locations**: Based on PDF floor plans, stairwells are located at consistent positions (approximately 5000mm from left edge) across all three floors
- **Exit positions and accessibility**:
  - Primary exit (Entrance) on F1 at left side (0, 10)
  - Secondary exits accessible via stairwell to upper floors
  - All floors accessible via stairwell network

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Simulation completes room assignment for all rooms across 3 floors to 2 personnel in under 5 seconds execution time
- **SC-002**: All rooms from all three floor PDFs (F1, F3, F4) are inspected exactly once with zero rooms missed or double-counted
- **SC-003**: Visualization clearly distinguishes between corridor movement (horizontal) and stairwell movement (vertical) with 100% of stairwell transitions visually marked
- **SC-004**: Calculated total inspection time matches manual calculation verification within 5% margin (accounting for path optimization variations)
- **SC-005**: Room names displayed in visualization exactly match room names from PDF floor plans with 100% accuracy
- **SC-006**: Path continuity validation shows zero gaps or teleportation errors (every path segment connects to the next)
- **SC-007**: Personnel return to nearest exit after inspection, with final position within 1 meter of designated exit location
- **SC-008**: Comparison between greedy and load-balanced strategies produces measurably different makespan times (demonstrating optimization impact)

### Performance Expectations

- **PE-001**: Visualization renders all three floors with clear legibility at 300 DPI output resolution
- **PE-002**: Text output displays complete path sequences with room names, times, and distances for each personnel
- **PE-003**: Simulation supports buildings with up to 10 floors and 50 rooms without significant performance degradation (execution under 30 seconds)
