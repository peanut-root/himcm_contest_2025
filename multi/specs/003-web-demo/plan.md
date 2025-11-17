# Implementation Plan: Web Demonstration Application

**Branch**: `003-web-demo` | **Date**: 2025-11-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-web-demo/spec.md`

## Summary

Create a simple web demonstration application that visualizes pre-computed firefighter patrol routes from the existing CLI tool. The app displays the fixed 6-room office layout and animates agents moving along their routes with playback controls. This is a visualization-only application using vanilla JavaScript and HTML5 Canvas - no frameworks, no build tools, designed to run as a static site.

## Technical Context

**Language/Version**: JavaScript ES6+ (vanilla, no transpilation needed)
**Primary Dependencies**: None (vanilla HTML/CSS/JavaScript only)
**Storage**: Static JSON files (pre-computed results from CLI tool)
**Testing**: Manual browser testing (no automated test framework for simple demo)
**Target Platform**: Modern desktop browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
**Project Type**: Web (static site, single HTML page with embedded styles and scripts)
**Performance Goals**: 30 FPS animation, <100ms interaction response, <2 second initial load
**Constraints**: Static-only (no server), <5MB total size, works offline after load
**Scale/Scope**: Single-user demo, 1 HTML page, ~500 lines of JavaScript, 4 pre-computed scenarios

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The existing constitution focuses on the CLI firefighter patrol optimization system. This web demo is a separate visualization layer that does not modify the core optimization algorithms or data structures. Constitution compliance:

| Principle | Applicable? | Status | Notes |
|-----------|-------------|--------|-------|
| Graph-Based Building Representation | No | N/A | Web demo displays results, doesn't create graphs |
| Complete Coverage with Redundancy | No | N/A | Web demo shows pre-verified results from CLI |
| Makespan Optimization | No | N/A | Web demo visualizes existing optimization |
| Task Allocation and Pathfinding | No | N/A | Web demo animates pre-computed paths |
| Mathematical Rigor | No | N/A | No algorithms implemented in web demo |

**Result**: ✅ **PASS** - Web demonstration is orthogonal to core system. It's a pure visualization layer consuming validated CLI output. No constitution violations since no optimization logic is implemented.

## Project Structure

### Documentation (this feature)

```text
specs/003-web-demo/
├── plan.md              # This file
├── quickstart.md        # How to run the demo
└── checklists/
    └── requirements.md  # Specification validation
```

### Source Code (repository root)

```text
demo/                    # New directory for web demonstration
├── index.html           # Single-page application
├── styles/
│   └── main.css         # Styling for layout and controls
├── scripts/
│   ├── building.js      # Building layout rendering
│   ├── animation.js     # Agent animation controller
│   ├── controls.js      # Playback controls (play/pause/speed/scrub)
│   └── metrics.js       # Metrics panel display
├── data/
│   ├── building.json    # 6-room office layout
│   ├── results-basic.json         # Pre-computed: 2 agents, basic
│   ├── results-redundancy.json    # Pre-computed: 3 agents, redundant rooms
│   ├── results-return.json        # Pre-computed: 2 agents, return to exit
│   └── results-multi.json         # Pre-computed: 5 agents, 10 rooms
└── README.md            # Demo instructions

# Existing CLI tool (unchanged)
src/                     # CLI optimization implementation
examples/                # JSON building configurations
docs/                    # CLI documentation
```

**Structure Decision**: Create a separate `demo/` directory to isolate the web visualization from the CLI tool. This keeps the demo self-contained and doesn't interfere with the existing TypeScript CLI codebase. The demo is intentionally simple: one HTML file that loads external CSS, JavaScript modules, and JSON data files.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations detected. This section is not applicable.

## Phase 0: Technology Decisions

Since this is a simple visualization demo with no complex dependencies, minimal research is needed:

### Rendering Approach

**Decision**: HTML5 Canvas

**Rationale**:
- Native browser API (no dependencies)
- Excellent performance for 2D animation
- Simple rectangle/circle drawing API perfect for rooms and agents
- Smooth animation via `requestAnimationFrame()`
- Canvas size: 800x600px sufficient for 6-room layout

**Alternatives Considered**:
- SVG: More complex to animate, overkill for simple shapes
- WebGL: Far too complex for this use case
- DOM manipulation: Poor performance for smooth animation

### Animation Approach

**Decision**: `requestAnimationFrame()` with linear interpolation

**Rationale**:
- Native browser API for smooth 60 FPS
- Simple time-based animation (current_time / duration)
- Pause/resume by canceling/restarting animation frame
- Speed control by scaling time delta
- Timeline scrubbing by jumping to specific time offset

**Alternatives Considered**:
- CSS animations: Not suitable for path-based movement
- Animation libraries (GSAP, Anime.js): Unnecessary dependencies
- setInterval/setTimeout: Less smooth, not frame-synced

### File Structure

**Decision**: Single HTML file with embedded CSS and separate JS modules

**Rationale**:
- Easy to deploy (just copy demo/ directory)
- No build process required
- JavaScript modules (ES6 imports) for code organization
- Embedded CSS keeps it simple while maintaining readability
- Works with any static file server or file:// protocol

## Phase 1: Data Model

### BuildingLayout

Represents the fixed 6-room office layout:

```javascript
{
  "id": "office-6-room",
  "name": "Basic 6-Room Office",
  "nodes": [
    { "id": "exit-left", "type": "EXIT", "x": 50, "y": 300 },
    { "id": "exit-right", "type": "EXIT", "x": 750, "y": 300 },
    { "id": "hallway", "type": "CORRIDOR", "x": 400, "y": 300 },
    { "id": "door-R1", "type": "DOOR", "x": 200, "y": 150 },
    // ... more nodes
  ],
  "rooms": [
    { "id": "R1", "doorNode": "door-R1", "label": "Office 1" },
    // ... R2-R6
  ]
}
```

### PreComputedResults

JSON output from CLI tool (existing format):

```javascript
{
  "missionId": "office-6-room",
  "makespan": 195,
  "routes": [
    {
      "agentId": "A1",
      "actions": [
        { "type": "MOVE", "startTime": 0, "duration": 10, "location": "corridor-1" },
        { "type": "INSPECT", "startTime": 20, "duration": 30, "location": "R1" }
      ],
      "roomsInspected": ["R1", "R3", "R5"]
    }
  ],
  "metrics": { /* existing CLI metrics */ }
}
```

### AnimationState

Managed in JavaScript:

```javascript
class AnimationState {
  isPlaying: boolean;
  currentTime: number;      // milliseconds
  speed: number;            // 0.5x to 3.0x
  agents: {
    id: string;
    x: number;
    y: number;
    currentAction: object;
  }[];
}
```

## Phase 1: Component Design

### Building Renderer (`building.js`)

- **Responsibility**: Draw fixed 6-room layout on canvas
- **Methods**:
  - `drawBuilding(canvas, building)`: Render rooms, hallway, exits
  - `drawRoom(ctx, room, state)`: Draw room rectangle with label and color (yellow/blue/green)
  - `drawHallway(ctx)`: Draw central corridor
  - `drawExits(ctx)`: Draw exit markers

### Animation Controller (`animation.js`)

- **Responsibility**: Manage agent animation over time
- **Methods**:
  - `start()`: Begin animation loop with `requestAnimationFrame()`
  - `pause()`: Cancel animation frame
  - `setSpeed(multiplier)`: Scale time progression
  - `scrubTo(time)`: Jump to specific time
  - `updateAgents(currentTime)`: Calculate agent positions based on route actions

### Playback Controls (`controls.js`)

- **Responsibility**: UI controls for play/pause/speed/timeline
- **Elements**:
  - Play/Pause button
  - Speed slider (0.5x to 3x)
  - Timeline scrubber (0 to makespan)
  - Restart button

### Metrics Display (`metrics.js`)

- **Responsibility**: Show mission statistics
- **Elements**:
  - Makespan display
  - Agent completion times
  - Total path length
  - Coverage percentage

## Quickstart Preview

```markdown
# Web Demo Quickstart

## Running the Demo

### Option 1: Local File
1. Navigate to the `demo/` directory
2. Open `index.html` in a modern browser
3. Note: Some browsers block local file access for security. Use Option 2 if issues occur.

### Option 2: Local Server
```bash
cd demo
python3 -m http.server 8000
# Open http://localhost:8000 in browser
```

### Option 3: Live Server (VS Code)
1. Install "Live Server" extension
2. Right-click `demo/index.html`
3. Select "Open with Live Server"

## Using the Demo

1. **Load Scenario**: Select from dropdown (Basic, Redundancy, Return to Exit, Multi-Agent)
2. **Play Animation**: Click "Play" to start agent movement
3. **Control Speed**: Adjust slider (0.5x to 3x)
4. **Scrub Timeline**: Drag timeline slider to jump to any point
5. **View Metrics**: See makespan, path lengths, coverage in side panel

## File Structure

- `index.html` - Main application page
- `styles/main.css` - Styling
- `scripts/` - JavaScript modules
- `data/` - Pre-computed results from CLI tool
```

## Implementation Phases

### Phase 1: Basic Visualization (User Story 1 - P1)
**Goal**: Display building and animate agents along routes

**Tasks**:
1. Create `demo/index.html` with canvas and basic layout
2. Implement `building.js` to render 6-room office layout
3. Load `results-basic.json` from CLI tool
4. Implement `animation.js` to move agents along paths
5. Add room color changes (pending → in-progress → completed)
6. Implement `metrics.js` to display makespan and statistics

**Deliverable**: Working demo that loads and animates the basic scenario

### Phase 2: Playback Controls (User Story 2 - P2)
**Goal**: Add play/pause/speed/scrub controls

**Tasks**:
1. Implement `controls.js` with UI buttons and sliders
2. Add play/pause functionality to animation controller
3. Implement speed multiplier (0.5x to 3.0x)
4. Add timeline scrubber for jumping to any time
5. Implement restart button

**Deliverable**: Full playback control over animation

### Phase 3: Scenario Switching (User Story 3 - P3)
**Goal**: Load and switch between different scenarios

**Tasks**:
1. Copy all pre-computed results from CLI tool to `demo/data/`
2. Add scenario dropdown menu
3. Implement scenario loading logic
4. Update display when scenario changes
5. Test all 4 scenarios

**Deliverable**: Complete demo with 4 switchable scenarios

## Post-Design Constitution Check

**Re-validation Against Constitution**:

Since the web demo is purely a visualization layer consuming pre-computed CLI output, there are no algorithmic concerns to validate against the constitution. The demo:

- ✅ Does not implement graph algorithms (displays only)
- ✅ Does not calculate routes (loads pre-computed)
- ✅ Does not validate coverage (shows CLI-validated results)
- ✅ Uses the same JSON schema as CLI tool

**Result**: ✅ **PASS** - No constitution violations. Demo is a presentation layer only.

## Deployment

The demo is a static site that can be deployed to:

1. **GitHub Pages**: Push `demo/` directory to gh-pages branch
2. **Netlify**: Drag and drop `demo/` folder
3. **Vercel**: Deploy `demo/` as static site
4. **Local**: Run any static file server in `demo/` directory

No server-side code, no build step, no dependencies. Just copy files and serve.

## Estimated Timeline

- **Phase 1** (P1 - Basic Visualization): 2-3 days
- **Phase 2** (P2 - Playback Controls): 1-2 days
- **Phase 3** (P3 - Scenario Switching): 0.5-1 day

**Total**: 3.5-6 days for complete demo with all 3 user stories.

**MVP** (Phase 1 only): 2-3 days for a working animated visualization.
