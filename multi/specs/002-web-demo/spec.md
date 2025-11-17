# Feature Specification: Web Demonstration Application

**Feature Branch**: `002-web-demo`
**Created**: 2025-11-12
**Status**: Draft
**Input**: User description: "create a web application for demonstrating the whole solution"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Interactive Building Configuration (Priority: P1)

Users want to visually design a building layout and see how the patrol optimization works without needing to manually edit JSON files.

**Why this priority**: This is the core value proposition - making the CLI tool accessible through a visual interface. Without this, the web app provides no advantage over the existing CLI.

**Independent Test**: Can be tested by creating a new building with nodes and edges in the web interface, then exporting it as JSON to verify it matches the expected schema format.

**Acceptance Scenarios**:

1. **Given** user opens the web application, **When** they click "New Building", **Then** they see an empty canvas with drawing tools
2. **Given** user has an empty canvas, **When** they add nodes (exits, corridors, doors) by clicking on the canvas, **Then** nodes appear at clicked positions with appropriate icons
3. **Given** user has placed multiple nodes, **When** they connect nodes by dragging between them, **Then** edges are created with default travel times
4. **Given** user has created edges, **When** they click an edge, **Then** they can edit base time and clearance time properties
5. **Given** user has created nodes, **When** they click a door node, **Then** they can assign it to a room and set inspection time
6. **Given** user has a complete building, **When** they click "Export", **Then** they get a valid JSON file matching the building schema

---

### User Story 2 - Visualize Optimization Results (Priority: P2)

Users want to see the optimization results visually on the building layout with animated agent movements, rather than reading text output or static timelines.

**Why this priority**: This adds significant value over the CLI by providing spatial understanding of agent movements and making the solution more engaging and easier to understand.

**Independent Test**: Can be tested by loading a pre-configured building and mission results, then verifying that agents are animated along their assigned routes with correct timing.

**Acceptance Scenarios**:

1. **Given** user has optimization results loaded, **When** they click "Play", **Then** animated agents move through the building following their assigned routes
2. **Given** animation is playing, **When** user hovers over an agent, **Then** they see agent ID, current action, and time elapsed
3. **Given** animation is playing, **When** user hovers over a room, **Then** they see inspection status (pending, in-progress, completed) and which agents have visited
4. **Given** results show conflicts, **When** user views the timeline, **Then** conflict points are highlighted in red with warning icons
5. **Given** animation completes, **When** user views summary panel, **Then** they see makespan, coverage percentage, and load balance metrics

---

### User Story 3 - Configure and Run Missions (Priority: P3)

Users want to configure mission parameters (agent count, redundancy, return-to-exit) through a form interface and trigger optimization from the web app.

**Why this priority**: This completes the end-to-end workflow but can be done after visualizing pre-computed results. Users can still manually run CLI commands if needed.

**Independent Test**: Can be tested by configuring a mission with specific parameters, running optimization, and verifying the returned results match the configuration.

**Acceptance Scenarios**:

1. **Given** user has a valid building, **When** they click "Configure Mission", **Then** they see a form with agent count, start location, and options
2. **Given** user is in mission configuration, **When** they select specific rooms as redundant, **Then** those rooms are highlighted in yellow on the canvas
3. **Given** user has configured mission parameters, **When** they click "Optimize Routes", **Then** the system runs the optimization and shows a progress indicator
4. **Given** optimization completes successfully, **When** results load, **Then** user automatically transitions to the visualization view
5. **Given** optimization fails, **When** error occurs, **Then** user sees clear error message with suggestions (e.g., "No path found from entrance to Room R3")

---

### User Story 4 - Load and Save Scenarios (Priority: P4)

Users want to save their building configurations and load example scenarios to quickly explore different situations.

**Why this priority**: Quality-of-life feature that improves usability but not essential for demonstrating the core solution.

**Independent Test**: Can be tested by saving a building configuration, reloading the page, and loading the saved scenario to verify data persistence.

**Acceptance Scenarios**:

1. **Given** user has created a building, **When** they click "Save Scenario", **Then** scenario is saved to browser storage with a user-provided name
2. **Given** user has saved scenarios, **When** they click "Load", **Then** they see a list of saved scenarios and example templates
3. **Given** user selects a saved scenario, **When** they click "Load", **Then** building and previous results (if any) are restored
4. **Given** user is viewing the scenario list, **When** they select an example template, **Then** they can load pre-configured scenarios (basic 6-room, redundancy, warehouse, multi-agent)

---

### Edge Cases

- What happens when user creates a disconnected graph (rooms unreachable from entrances)? System should validate connectivity and show error.
- How does system handle very large buildings (50+ rooms)? Canvas should support zoom and pan for navigation.
- What if optimization takes longer than 10 seconds? Show animated progress with estimated time remaining.
- How does the app handle mobile/tablet users? Provide touch-friendly controls or display a "desktop recommended" message.
- What if browser doesn't support required features (Canvas API, LocalStorage)? Show compatibility warning with browser recommendations.
- What happens if user navigates away during optimization? Cancel the ongoing operation and show warning about unsaved progress.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an interactive canvas for building design where users can add nodes (exits, corridors, doors) by clicking
- **FR-002**: System MUST allow users to connect nodes by drawing edges between them and set edge properties (base time, clearance time)
- **FR-003**: System MUST support creating rooms by associating door nodes with room properties (ID, inspection time, redundancy flag)
- **FR-004**: System MUST validate building topology using the same validator as the CLI tool (connectivity, unique IDs, valid references)
- **FR-005**: System MUST export building configurations as JSON files matching the existing building schema
- **FR-006**: System MUST import existing JSON building configurations and render them on the canvas
- **FR-007**: System MUST allow users to configure mission parameters through a form (agent count, start location, redundant rooms, return-to-exit option)
- **FR-008**: System MUST trigger route optimization by calling the existing CLI planner functionality
- **FR-009**: System MUST display optimization results with animated agent movements on the building layout
- **FR-010**: System MUST show agent status during animation (current location, current action type, elapsed time)
- **FR-011**: System MUST visualize room inspection states (pending, in-progress, completed) with color coding
- **FR-012**: System MUST highlight conflicts when multiple agents inspect the same room simultaneously
- **FR-013**: System MUST display performance metrics panel showing makespan, coverage rate, redundancy rate, and load balance
- **FR-014**: System MUST provide playback controls (play, pause, speed adjustment, timeline scrubbing)
- **FR-015**: System MUST save building configurations to browser LocalStorage with user-provided names
- **FR-016**: System MUST include 4 pre-loaded example scenarios (basic, redundancy, return-to-exit, multi-agent)
- **FR-017**: System MUST provide tooltips and help text explaining each feature and control
- **FR-018**: System MUST show clear error messages with actionable suggestions when validation or optimization fails
- **FR-019**: System MUST support keyboard shortcuts for common actions (delete node: Delete key, undo: Ctrl+Z)
- **FR-020**: System MUST be responsive and work on desktop browsers with minimum 1024px width

### Key Entities

- **BuildingCanvas**: Represents the visual building layout with nodes, edges, and rooms rendered on a 2D canvas. Contains zoom/pan state and drawing mode.
- **Node**: Represents a location in the building (exit, corridor, or door). Has position (x, y), type, unique ID, and optional label.
- **Edge**: Represents a connection between two nodes. Has source node, target node, base time, optional clearance time, and bidirectional flag.
- **Room**: Represents an inspection target. Has unique ID, associated door node, inspection time, redundancy flag, and optional label.
- **Mission**: Represents the optimization configuration. Contains agent count, start location, redundant room list, return-to-exit flag, and time parameters.
- **AnimatedAgent**: Represents a firefighter during playback. Has agent ID, current route, current action index, elapsed time, and position on canvas.
- **OptimizationResults**: Contains the mission output including routes, makespan, validation status, and performance metrics.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a valid 6-room building configuration in under 5 minutes using the visual canvas
- **SC-002**: Users can understand optimization results within 30 seconds of viewing the animated playback
- **SC-003**: 90% of users successfully run their first optimization without errors using the guided interface
- **SC-004**: System loads and displays existing CLI-generated results without modification (100% compatibility)
- **SC-005**: Users can export web-created buildings and use them directly with the CLI tool (bi-directional compatibility)
- **SC-006**: Animation playback runs smoothly at 30 FPS for buildings with up to 20 rooms and 10 agents
- **SC-007**: Users can identify room inspection conflicts within 10 seconds using the visual conflict indicators
- **SC-008**: System responds to user interactions (clicks, drags) within 100ms for immediate feedback
- **SC-009**: 80% of target users prefer the web interface over CLI for demonstrating the solution
- **SC-010**: Users can learn all core features within 10 minutes using only in-app tooltips and examples

## Assumptions

- Users have access to a modern desktop browser (Chrome, Firefox, Safari, Edge) with JavaScript enabled
- Users have basic computer skills (mouse/keyboard usage, understanding of drag-and-drop)
- The existing TypeScript CLI codebase can be adapted or called from the web application
- Users are primarily demonstrating to technical audiences (e.g., competition judges, colleagues) rather than general public
- Internet connection is available for initial app loading, but optimization runs locally (no server required)
- Users understand basic fire safety concepts (rooms, inspection, patrol routes)
- Building layouts are 2D floor plans; multi-floor buildings are out of scope
- The web app is for demonstration and experimentation, not production mission planning
- Users accept browser LocalStorage for saving scenarios (no account/cloud sync required)
- The web app will be delivered as a static site that can be hosted anywhere or run locally

## Out of Scope

- Real-time collaboration features (multiple users editing same building)
- 3D building visualization or multi-floor support
- Mobile/tablet optimization (desktop-first approach)
- User authentication or cloud-based storage
- Integration with building information systems (BIM) or CAD file import
- Automatic building layout generation from images or floor plans
- Real-time sensor data integration
- Historical mission data tracking or analytics dashboard
- Sharing scenarios via URLs or social media
- Printing or exporting reports (users can screenshot or use CLI export)
- Advanced animation features (camera following agents, cinematic transitions)
- Accessibility features beyond standard browser support
- Internationalization (English only)
- Voice commands or assistive technologies integration
