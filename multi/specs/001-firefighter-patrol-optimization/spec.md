# Feature Specification: Firefighter Patrol Optimization System

**Feature Branch**: `001-firefighter-patrol-optimization`
**Created**: 2025-11-12
**Status**: Draft
**Input**: User description: "Firefighter patrol path optimization system for emergency building inspection with complete coverage, redundancy support, and makespan minimization"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Building Patrol Planning (Priority: P1)

Emergency response coordinator needs to generate optimal patrol routes for firefighters inspecting a single-floor building to ensure all rooms are checked with minimal time.

**Why this priority**: Core functionality enabling basic patrol route generation - without this, the system provides no value. This is the MVP that demonstrates the fundamental optimization capability.

**Independent Test**: Can be fully tested by providing a building layout with 6 rooms and 2 firefighters, then verifying that the system generates complete coverage patrol routes with calculated completion times.

**Acceptance Scenarios**:

1. **Given** a single-floor building layout with 6 rooms along a corridor, **When** coordinator inputs 2 firefighters starting from entrance, **Then** system generates patrol routes ensuring every room is visited at least once with total completion time displayed
2. **Given** generated patrol routes, **When** coordinator reviews the output, **Then** each route shows: room inspection sequence, estimated travel time, clearance operations, and total mission time
3. **Given** building layout with obstacles requiring clearance, **When** system generates routes, **Then** clearance operations are assigned only once per obstacle and shared across subsequent agent traversals

---

### User Story 2 - Redundancy Mode for Critical Verification (Priority: P2)

Emergency response coordinator wants to designate high-risk rooms for double-checking by different firefighters to ensure accuracy in critical areas.

**Why this priority**: Adds safety redundancy for critical scenarios without blocking basic functionality. Builds on P1 by adding configurable verification levels.

**Independent Test**: Can be tested independently by taking any building from User Story 1, marking specific rooms as "redundant", and verifying that exactly 2 different firefighters inspect those rooms.

**Acceptance Scenarios**:

1. **Given** a building layout, **When** coordinator marks specific rooms as requiring redundant inspection, **Then** system ensures those rooms are inspected by two different firefighters
2. **Given** redundant inspection requirements, **When** system generates routes, **Then** completion time accounts for both inspections while minimizing overall makespan
3. **Given** redundant room inspections by two agents, **When** routes are executed, **Then** no two agents attempt to inspect the same room simultaneously (time conflicts are avoided)

---

### User Story 3 - Return-to-Exit Mission Planning (Priority: P3)

Emergency response coordinator wants firefighters to return to designated exit points after completing inspections to ensure safe evacuation tracking.

**Why this priority**: Operational enhancement for realistic mission scenarios. Adds complete mission planning but not essential for the core optimization value.

**Independent Test**: Can be tested by configuring any patrol mission to require exit return, then verifying that routes include return paths and updated completion times.

**Acceptance Scenarios**:

1. **Given** a patrol mission configuration, **When** coordinator enables "return to exit" option, **Then** system adds return paths to nearest exit for each firefighter route
2. **Given** multiple exit points, **When** system plans return routes, **Then** each firefighter is routed to their optimal (nearest) exit to minimize total time
3. **Given** routes with exit return enabled, **When** reviewing mission timeline, **Then** completion time includes return travel and clearly indicates mission end at exit location

---

### User Story 4 - Mission Timeline Visualization (Priority: P4)

Emergency response coordinator wants to see a visual timeline of all firefighter activities to understand parallel operations and identify bottlenecks.

**Why this priority**: Analysis and presentation tool that enhances understanding but doesn't affect core optimization functionality.

**Independent Test**: Can be tested by generating any patrol mission and verifying that the visualization displays concurrent activities, time markers, and highlights conflicts or waiting periods.

**Acceptance Scenarios**:

1. **Given** a completed patrol route optimization, **When** coordinator requests timeline view, **Then** system displays Gantt-style chart showing each firefighter's activities over time
2. **Given** timeline visualization, **When** multiple agents operate in parallel, **Then** chart clearly shows overlapping corridor traversal and non-overlapping room inspections
3. **Given** room inspection conflicts, **When** displayed on timeline, **Then** waiting periods are highlighted with explanation of why agent must wait

---

### Edge Cases

- What happens when building has unreachable rooms (no valid path from entrance)?
- How does system handle single-agent scenarios (n=1)?
- What if all rooms are marked redundant (every room needs 2 inspections)?
- How does system optimize when one agent is significantly slower than others?
- What happens when clearance time for obstacles exceeds typical inspection time?
- How does system handle buildings where corridor capacity creates bottlenecks (though base scenario assumes parallel corridor traversal)?
- What if firefighters start from different entrance points?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST model buildings as graph structures with nodes (corridors, doors, exits) and edges (traversable paths with time costs)
- **FR-002**: System MUST accept building topology configuration including: room count, corridor layout, entrance/exit locations, and connectivity
- **FR-003**: System MUST accept firefighter configuration including: count, starting positions, movement speed, and equipment capabilities
- **FR-004**: System MUST accept time parameters including: base travel time per distance unit, obstacle clearance time, door entry time, room inspection time, and exit time
- **FR-005**: System MUST guarantee complete coverage: every room inspected at least once
- **FR-006**: System MUST support configurable redundancy: specified rooms inspected exactly twice by different firefighters
- **FR-007**: System MUST enforce room-level mutual exclusion: only one firefighter inspects a room at any given time
- **FR-008**: System MUST allow parallel corridor traversal: multiple firefighters can use corridors simultaneously
- **FR-009**: System MUST track clearance state: obstacles cleared once, then freely passable by all subsequent agents
- **FR-010**: System MUST calculate optimal task assignment to minimize makespan (maximum individual completion time)
- **FR-011**: System MUST generate complete patrol routes showing: ordered sequence of locations, actions at each location, and timestamps
- **FR-012**: System MUST calculate total mission time as the maximum of all individual firefighter completion times
- **FR-013**: System MUST support optional return-to-exit requirement: firefighters routed back to any exit point after completing inspections
- **FR-014**: System MUST output performance metrics including: total completion time, individual agent times, path lengths, redundancy coverage rate, and clearance efficiency
- **FR-015**: System MUST provide route output in structured format (e.g., JSON) showing complete path with node IDs and timestamps
- **FR-016**: System MUST validate input configurations and report errors for invalid topologies (unreachable rooms, disconnected graphs)
- **FR-017**: System MUST handle buildings with 1-20 rooms and 1-10 firefighters
- **FR-018**: System MUST detect and resolve temporal conflicts when multiple agents would inspect same room simultaneously
- **FR-019**: System MUST calculate shortest paths accounting for dynamic edge costs (clearance required on first use only)
- **FR-020**: System MUST balance workload across firefighters to prevent individual bottlenecks while minimizing total time

### Key Entities

- **Building**: Represents the structure to be inspected. Contains graph topology (nodes and edges), room definitions, entrance/exit locations, and corridor layout. Each building has geometric properties (coordinates) and connectivity rules.

- **Room**: Represents an inspection target within the building. Has unique identifier, door location (connection point to corridor), inspection verification time, and optional redundancy flag. Rooms are accessed through door nodes.

- **Firefighter/Agent**: Represents a patrol team member. Has unique identifier, starting position (entrance node), movement speed (distance per time unit), and equipment configuration. Each agent executes an assigned route.

- **Route/Path**: Represents the planned sequence of actions for one firefighter. Contains ordered list of nodes to visit, actions at each node (move, clear, enter, inspect, exit), timestamps for each action, and total completion time.

- **Node**: Represents a location in the building graph. Types include corridor positions, door entry points, and exit locations. Nodes have coordinates and connectivity to other nodes via edges.

- **Edge**: Represents a traversable connection between two nodes. Has base traversal time, optional first-use clearance time, current clearance state, and direction information (bidirectional or unidirectional).

- **Mission**: Represents the complete patrol operation. Contains building configuration, firefighter assignments, route plans for all agents, redundancy specifications, return-to-exit requirements, and calculated performance metrics.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: System generates complete patrol routes for the basic 6-room scenario in under 5 seconds
- **SC-002**: Generated routes guarantee 100% room coverage (every room inspected at least once)
- **SC-003**: For buildings with redundant rooms specified, system achieves 100% redundancy compliance (all marked rooms inspected exactly twice by different agents)
- **SC-004**: System-generated routes have completion times within 15% of theoretical optimal (compared to hand-calculated solutions for small test cases)
- **SC-005**: For balanced workload scenarios (equal-capability agents), individual agent completion times differ by no more than 20% from mean
- **SC-006**: System correctly handles edge cases: single agent (n=1), single room (m=1), all rooms redundant, without errors
- **SC-007**: Output includes all required metrics: makespan (T_max), individual times, path lengths, redundancy coverage %, and clearance efficiency
- **SC-008**: Generated routes respect temporal constraints with zero room-level conflicts (no simultaneous room inspections)
- **SC-009**: When return-to-exit is enabled, 100% of generated routes include valid return path to an exit
- **SC-010**: System successfully processes building configurations ranging from 1-20 rooms and 1-10 agents
- **SC-011**: Timeline visualization (when implemented) accurately reflects parallel operations showing corridor overlap and room exclusivity
- **SC-012**: Performance metrics match manual verification for at least 3 validation test cases

## Assumptions

- Building topology is provided as structured input (not derived from floor plans or images)
- All rooms are reachable from at least one entrance (connected graph)
- Corridors have unlimited capacity for parallel traversal in base scenario
- Firefighters have homogeneous capabilities unless specified otherwise
- Time parameters (movement speed, inspection duration, clearance duration) are deterministic and known upfront
- Communication between firefighters is assumed (no coordination failures)
- Obstacles requiring clearance are known in advance and static
- Room inspection is atomic (cannot be partially completed)
- Once cleared, obstacles remain cleared for mission duration
- Building is single-floor in basic scenario (vertical movement not required)
- Real-time repositioning or dynamic replanning not required (routes are pre-calculated)
- Firefighter safety constraints beyond room mutual exclusion are out of scope
- Environmental factors (smoke, heat, structural damage) are abstracted into time parameters
- Equipment failures or agent incapacitation are out of scope

## Out of Scope

- Multi-floor building support (reserved for future extension)
- Real-time dynamic replanning during mission execution
- Incomplete information scenarios (probabilistic room occupancy)
- Time-varying edge costs (spreading fire, structural collapse)
- Integration with building information systems (BIM) or live sensor data
- Mobile/tablet interface for field use
- Communication protocol design between firefighters
- Physical simulation of fire spread or structural integrity
- Detailed 3D building visualization
- Historical mission data analysis or machine learning optimization
- Integration with dispatch or emergency management systems
- Personnel scheduling or shift management
- Equipment inventory or maintenance tracking
