# Research: Multi-Floor Building Inspection Simulation

**Feature**: 001-multi-floor-inspection
**Date**: 2025-11-17
**Phase**: 0 - Research and Technical Discovery

## Research Questions Resolved

### Q1: How to model 3D spatial pathfinding with floor transitions?

**Decision**: Use 2D pathfinding per floor + explicit stairwell transitions

**Rationale**:
- Each floor has its own 2D coordinate system (x, y in meters)
- Stairwells act as "portals" between floor coordinate systems
- Path segments tagged with floor identifier and segment type (corridor vs. stairwell)
- Distance calculations:
  - **Horizontal (same floor)**: Euclidean distance via corridor waypoints
  - **Vertical (between floors)**: Stairwell distance + floor height penalty

**Alternatives considered**:
- **Full 3D coordinates (x, y, z)**: Rejected - overly complex for discrete floor levels, harder to visualize
- **Graph-based pathfinding (Dijkstra/A*)**: Rejected - overkill for small building (20 rooms), greedy heuristic sufficient per existing single-level sim

**Implementation approach**:
```python
@dataclass
class PathSegment:
    start_pos: Tuple[float, float]  # (x, y)
    end_pos: Tuple[float, float]
    start_floor: str  # "F1", "F3", "F4"
    end_floor: str
    segment_type: str  # "corridor" or "stairwell"
    distance: float
    time: float  # distance / speed
```

---

### Q2: How to visualize 3 floors on a single output image?

**Decision**: Vertical stacking with floor labels and inter-floor connection indicators

**Rationale**:
- Matplotlib supports multiple subplots (fig, axes = plt.subplots(3, 1))
- Each subplot represents one floor's 2D layout
- Stairwell positions aligned vertically across subplots
- Visual connectors (dashed lines or arrows) between aligned stairwells
- Alternative: side-by-side layout rejected due to horizontal space constraints

**Best practices**:
- **Figure size**: (18, 24) for 3 floors stacked (6:8 aspect per floor)
- **DPI**: 300 for publication quality
- **Color coding**:
  - Floor backgrounds: white
  - Rooms: pastel colors (plt.cm.Set3) with transparency
  - Person 1 path: red
  - Person 2 path: blue
  - Stairwells: gray with hatch pattern
  - Stairwell transitions: dashed purple lines connecting subplots

**Example structure**:
```python
fig, (ax_f1, ax_f3, ax_f4) = plt.subplots(3, 1, figsize=(18, 24))
# Draw F1 on ax_f1, F3 on ax_f3, F4 on ax_f4
# Add vertical alignment guides for stairwells
```

---

### Q3: How to extract room data from PDFs without automated parsing?

**Decision**: Manual transcription into Python dataclass initialization

**Rationale**:
- Only 3 PDFs with ~20 total rooms - manual transcription is feasible
- PDFs show room names, dimensions (mm), door positions visually
- Automated PDF parsing (PyPDF2, pdfplumber) requires:
  - OCR for text recognition (unreliable for Chinese characters)
  - Computer vision for extracting geometric data (complex setup)
  - Not justified for one-time 3-floor dataset

**Transcription process**:
1. Open F1.pdf, F3.pdf, F4.pdf
2. For each room, record:
   - Name (as shown in PDF, Chinese acceptable)
   - x, y position (top-left corner in mm, convert to meters)
   - width, height (in mm, convert to meters)
   - door x, y position (in mm, convert to meters)
   - door angle (0°/90°/180°/270° based on visual orientation)
   - Complexity factor (1.0/1.5/1.8 based on room type from spec)
3. Create Room instances in Python

**Example from F1.pdf**:
```python
# F1 (Floor 1) - from F1.pdf
Room("Toilet", floor="F1", x=4, y=17, width=4, height=5,
     door_x=6, door_y=17, door_angle=270, complexity=1.0)
Room("Coffee", floor="F1", x=4, y=12, width=16, height=5,
     door_x=12, door_y=17, door_angle=270, complexity=1.8)
# ... (transcribe all rooms from PDF)
```

---

### Q4: How to handle stairwell connectivity between non-consecutive floors?

**Decision**: Explicit Stairwell entity with connected_floors list

**Rationale**:
- Building has F1, F3, F4 (no F2) - cannot assume sequential floor numbering
- Stairwell connects F1↔F3 and F3↔F4 (two segments)
- Each stairwell segment is a bidirectional connection

**Data model**:
```python
@dataclass
class Stairwell:
    name: str  # "Main Stairwell"
    floors: List[str]  # ["F1", "F3", "F4"]
    position_per_floor: Dict[str, Tuple[float, float]]  # {"F1": (5, 10), "F3": (5, 10), "F4": (5, 10)}
    floor_height: float  # Vertical distance per floor (assume 3m typical)

    def get_transition_time(self, from_floor: str, to_floor: str, speed_factor: float) -> float:
        # Calculate number of floor transitions
        floor_index = {f: i for i, f in enumerate(self.floors)}
        floors_crossed = abs(floor_index[to_floor] - floor_index[from_floor])
        vertical_distance = floors_crossed * self.floor_height
        # speed_factor = 0.5 for stairs (slower than corridors)
        stair_speed = 1.5 * speed_factor  # 1.5 m/s base * 0.5 = 0.75 m/s
        return vertical_distance / stair_speed
```

**Path logic**:
- When assigning room on different floor, check if personnel must use stairwell
- Add stairwell waypoint to path
- Calculate stairwell time based on floors crossed (F1→F4 crosses 2 floors, double time vs F1→F3)

---

### Q5: How to adapt greedy assignment algorithm for 3 floors?

**Decision**: 3D distance heuristic via stairwell penalty

**Rationale**:
- Existing greedy: assign nearest unassigned room based on 2D corridor distance
- Multi-floor: add stairwell penalty to distance for rooms on different floors

**Distance calculation**:
```python
def get_path_distance_3d(person_pos, person_floor, room_door, room_floor, stairwell):
    if person_floor == room_floor:
        # Same floor: 2D corridor distance
        return corridor_distance_2d(person_pos, room_door)
    else:
        # Different floor: to stairwell + vertical + from stairwell
        to_stair = corridor_distance_2d(person_pos, stairwell.position_per_floor[person_floor])
        vertical = stairwell.get_vertical_distance(person_floor, room_floor)
        from_stair = corridor_distance_2d(stairwell.position_per_floor[room_floor], room_door)
        return to_stair + vertical + from_stair
```

**Greedy assignment adapted**:
1. For each unassigned room, calculate 3D distance for both personnel
2. Assign to personnel with lowest (current_time + move_time + inspection_time)
3. Update personnel position to room door (and floor if changed)
4. Repeat until all rooms assigned

---

## Technology Stack Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Language | Python 3.9+ | Matches existing simulation, good for mathematical modeling |
| Dataclasses | @dataclass | Clean entity modeling, type hints, immutability support |
| Visualization | matplotlib 3.x | Powerful 2D plotting, existing codebase uses it, supports patches for room shapes |
| Numerical | numpy | Array operations for path coordinates, efficient calculations |
| Floor plans | Manual transcription | Only 3 PDFs, ~20 rooms, automated parsing not justified |
| Output | PNG files (300 DPI) | Standard format, high resolution for publication |

---

## Implementation Patterns

### Pattern 1: Floor-based organization
Each floor is a collection of rooms + corridor waypoints + exits. Floor class encapsulates floor-specific data.

```python
@dataclass
class Floor:
    name: str  # "F1", "F3", "F4"
    rooms: List[Room]
    corridors: List[Tuple[float, float]]  # Waypoints for pathfinding
    exits: List[Tuple[float, float]]

    def get_room_by_name(self, name: str) -> Room:
        return next((r for r in self.rooms if r.name == name), None)
```

### Pattern 2: Path segment tracking
Personnel paths are sequences of segments, each with floor + type metadata for visualization.

```python
@dataclass
class Person:
    path_segments: List[PathSegment]  # Complete journey
    current_floor: str

    def add_corridor_move(self, from_pos, to_pos, floor):
        segment = PathSegment(from_pos, to_pos, floor, floor, "corridor", ...)
        self.path_segments.append(segment)

    def add_stairwell_move(self, from_floor, to_floor, stairwell):
        segment = PathSegment(..., segment_type="stairwell", ...)
        self.path_segments.append(segment)
        self.current_floor = to_floor
```

### Pattern 3: Visualization layering
Each floor rendered independently, then combine with inter-floor connection overlays.

```python
def visualize(self, person1, person2):
    fig, axes = plt.subplots(3, 1, figsize=(18, 24))

    for floor, ax in zip(self.floors, axes):
        self._draw_floor_layout(floor, ax)
        self._draw_paths_on_floor(floor, person1, person2, ax)

    # Add stairwell connection lines between axes
    self._draw_stairwell_connectors(axes)

    plt.savefig('./output/multi_floor_building_inspection.png', dpi=300)
```

---

## Open Questions (None - all resolved)

All technical unknowns from plan.md have been researched and resolved. Ready to proceed to Phase 1 (Design & Contracts).
