# Data Model: Multi-Floor Building Inspection Simulation

**Feature**: 001-multi-floor-inspection
**Date**: 2025-11-17
**Phase**: 1 - Design and Data Modeling

## Entity Overview

This simulation uses Python `@dataclass` entities to model the building structure, personnel, and pathfinding results. All entities use type hints for clarity and validation.

---

## Core Entities

### 1. Room

Represents an inspectable space within the building.

```python
from dataclasses import dataclass

@dataclass
class Room:
    name: str                 # Room name from PDF (e.g., "Coffee", "Toilet", "Meeting")
    floor: str                # Floor identifier ("F1", "F3", "F4")
    x: float                  # Top-left x position in meters
    y: float                  # Top-left y position in meters
    width: float              # Room width in meters
    height: float             # Room height in meters
    door_x: float             # Door x position in meters
    door_y: float             # Door y position in meters
    door_angle: float         # Door orientation (0/90/180/270 degrees)
    complexity: float         # USAR complexity factor (1.0/1.5/1.8)

    @property
    def area(self) -> float:
        """Calculate room area in square meters."""
        return self.width * self.height

    @property
    def door_position(self) -> Tuple[float, float]:
        """Return door position as (x, y) tuple."""
        return (self.door_x, self.door_y)
```

**Validation Rules**:
- `name`: Non-empty string, Chinese characters acceptable
- `floor`: Must be one of "F1", "F3", "F4"
- `x, y, width, height`: Positive floats
- `door_x, door_y`: Must be on room perimeter
- `door_angle`: Must be 0, 90, 180, or 270
- `complexity`: Must be 1.0 (empty), 1.5 (furnished), or 1.8 (equipment)

**Relationships**:
- Belongs to one Floor (via `floor` field)
- Visited by one Person during inspection (tracked in Person.rooms)

---

### 2. Floor

Represents a single level of the building.

```python
from typing import List, Tuple

@dataclass
class Floor:
    name: str                                # Floor identifier ("F1", "F3", "F4")
    rooms: List[Room]                        # All rooms on this floor
    corridors: List[Tuple[float, float]]     # Corridor waypoints for pathfinding
    exits: List[Tuple[float, float]]         # Exit positions on this floor
    height_offset: float = 0.0               # Vertical offset from ground (meters)

    def get_room_by_name(self, name: str) -> Room:
        """Find room by name on this floor."""
        return next((r for r in self.rooms if r.name == name), None)

    def get_all_room_names(self) -> List[str]:
        """Return list of all room names on this floor."""
        return [r.name for r in self.rooms]
```

**Validation Rules**:
- `name`: Must match one of the 3 floor identifiers
- `rooms`: List of Room instances, all with `floor` == this Floor's `name`
- `corridors`: List of (x, y) waypoints for valid paths
- `exits`: At least one exit position
- `height_offset`: Non-negative, typically 0 (F1), 3 (F3), 6 (F4) for 3m floor height

**Relationships**:
- Contains multiple Rooms
- Connected to other Floors via Stairwell
- Personnel navigate through this Floor's corridors

---

### 3. Stairwell

Represents vertical connection between floors.

```python
from typing import Dict

@dataclass
class Stairwell:
    name: str                                          # Stairwell identifier (e.g., "Main Stairwell")
    connected_floors: List[str]                        # Floors connected (["F1", "F3", "F4"])
    position_per_floor: Dict[str, Tuple[float, float]] # {"F1": (5, 10), "F3": (5, 10), ...}
    floor_height: float = 3.0                          # Vertical distance per floor (meters)

    def get_vertical_distance(self, from_floor: str, to_floor: str) -> float:
        """Calculate vertical distance between two floors."""
        floor_indices = {f: i for i, f in enumerate(self.connected_floors)}
        floors_crossed = abs(floor_indices[to_floor] - floor_indices[from_floor])
        return floors_crossed * self.floor_height

    def get_transition_time(self, from_floor: str, to_floor: str, stair_speed: float) -> float:
        """Calculate time to move between floors via this stairwell."""
        vertical_distance = self.get_vertical_distance(from_floor, to_floor)
        return vertical_distance / stair_speed

    def get_position_on_floor(self, floor: str) -> Tuple[float, float]:
        """Get stairwell entrance position on specified floor."""
        return self.position_per_floor.get(floor)
```

**Validation Rules**:
- `name`: Non-empty string
- `connected_floors`: List of 2+ floor identifiers in vertical order
- `position_per_floor`: Keys must match all floors in `connected_floors`
- `floor_height`: Positive float (typical: 3.0 meters)

**Relationships**:
- Connects multiple Floors
- Used by Person to transition between floors in path

---

### 4. Person

Represents an inspection team member.

```python
from typing import List, Tuple

@dataclass
class Person:
    id: int                                 # Personnel identifier (1, 2, ...)
    x: float                                # Current x position in meters
    y: float                                # Current y position in meters
    floor: str                              # Current floor ("F1", "F3", "F4")
    rooms: List[str]                        # Assigned room names (in visit order)
    path: List[Tuple[float, float, str]]    # Path waypoints: [(x, y, floor), ...]
    total_distance: float = 0.0             # Total distance traveled (meters)
    total_time: float = 0.0                 # Total time elapsed (seconds)

    def add_waypoint(self, x: float, y: float, floor: str):
        """Add waypoint to path."""
        self.path.append((x, y, floor))

    def move_to(self, x: float, y: float, floor: str, distance: float, time: float):
        """Move personnel to new position and update totals."""
        self.add_waypoint(x, y, floor)
        self.x, self.y, self.floor = x, y, floor
        self.total_distance += distance
        self.total_time += time

    def assign_room(self, room: Room, inspection_time: float):
        """Assign room to this person and record inspection."""
        self.rooms.append(f"{room.name}({inspection_time:.0f}s)")
```

**Validation Rules**:
- `id`: Positive integer
- `x, y`: Valid coordinates within building bounds
- `floor`: Must be one of "F1", "F3", "F4"
- `rooms`: Room names with optional time annotations
- `path`: List of (x, y, floor) tuples, must be continuous (no gaps)
- `total_distance, total_time`: Non-negative floats

**State Transitions**:
1. **Initial**: Person at starting position (typically entrance on F1)
2. **Moving**: Person traveling to next room (updates `x, y, floor, path`)
3. **Inspecting**: Person at room door (adds room to `rooms`, increments `total_time`)
4. **Transitioning**: Person using stairwell (changes `floor`, adds stairwell waypoint)
5. **Completed**: Person returned to exit (final position in `path`)

---

### 5. PathSegment

Represents a portion of personnel movement (used for detailed visualization).

```python
from typing import Tuple

@dataclass
class PathSegment:
    start_pos: Tuple[float, float]     # Start (x, y)
    end_pos: Tuple[float, float]       # End (x, y)
    start_floor: str                   # Starting floor
    end_floor: str                     # Ending floor
    segment_type: str                  # "corridor" or "stairwell"
    distance: float                    # Segment distance (meters)
    time: float                        # Segment time (seconds)

    @property
    def is_stairwell(self) -> bool:
        """Check if this segment is a stairwell transition."""
        return self.segment_type == "stairwell" or self.start_floor != self.end_floor
```

**Validation Rules**:
- `start_pos, end_pos`: Valid (x, y) coordinates
- `start_floor, end_floor`: Must be "F1", "F3", or "F4"
- `segment_type`: Must be "corridor" or "stairwell"
- `distance, time`: Non-negative floats
- **Consistency**: If `start_floor != end_floor`, then `segment_type` must be "stairwell"

**Relationships**:
- Part of Person's complete path
- Used for visualization to distinguish corridor vs stairwell movement

---

## Derived Data

### Inspection Time Calculation

Inspection time is calculated using the existing `sweep_time_gt` formula:

```python
def sweep_time_gt(area: float, vis: float, p_halt: float, clutter: float, redundancy: bool = False) -> float:
    """
    Calculate room inspection time using USAR ground truth model.

    Args:
        area: Room area in square meters
        vis: Visibility factor (0.0 - 1.0)
        p_halt: Probability of halt/obstacle (0.0 - 1.0)
        clutter: Room complexity factor (1.0/1.5/1.8)
        redundancy: If True, apply 1.3x time multiplier

    Returns:
        Inspection time in seconds
    """
    r = 0.05 + 0.30 * vis
    base = area / r * clutter
    comm = 120 * p_halt
    overhead = 15 + 0.5 * (area ** 0.5) * (clutter - 1)
    t = base + comm + overhead
    if redundancy:
        t *= 1.30
    return t
```

**Usage**: For each Room, call `sweep_time_gt(room.area, random(0.0, 0.8), random(0.05, 0.3), room.complexity)` to get inspection time.

---

### Distance Calculations

#### Same-floor corridor distance:
```python
def corridor_distance_2d(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Euclidean distance between two points on same floor."""
    return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)
```

#### Multi-floor distance (via stairwell):
```python
def multi_floor_distance(
    person_pos: Tuple[float, float],
    person_floor: str,
    room_door: Tuple[float, float],
    room_floor: str,
    stairwell: Stairwell
) -> float:
    """Calculate total distance including stairwell transition."""
    if person_floor == room_floor:
        return corridor_distance_2d(person_pos, room_door)

    # Route: person → stairwell → vertical → stairwell → room
    to_stair = corridor_distance_2d(person_pos, stairwell.get_position_on_floor(person_floor))
    vertical = stairwell.get_vertical_distance(person_floor, room_floor)
    from_stair = corridor_distance_2d(stairwell.get_position_on_floor(room_floor), room_door)

    return to_stair + vertical + from_stair
```

---

## Entity Relationships Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Building (implicit - not a separate class)                  │
│                                                              │
│  ┌─────────────┐   contains    ┌──────────────┐             │
│  │   Floor     │───────────────>│    Room      │             │
│  │             │   1:N          │              │             │
│  │ - name      │                │ - name       │             │
│  │ - rooms     │                │ - floor      │             │
│  │ - corridors │                │ - x, y, w, h │             │
│  │ - exits     │                │ - complexity │             │
│  └─────────────┘                └──────────────┘             │
│        │                                                     │
│        │ connected by                                        │
│        ▼                                                     │
│  ┌─────────────┐                                            │
│  │  Stairwell  │                                            │
│  │             │                                            │
│  │ - floors    │                                            │
│  │ - positions │                                            │
│  └─────────────┘                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
         │
         │ navigated by
         ▼
   ┌─────────────┐   visits    ┌──────────────┐
   │   Person    │─────────────>│    Room      │
   │             │   N:M        │              │
   │ - id        │              │ (via rooms   │
   │ - position  │              │  list)       │
   │ - floor     │              └──────────────┘
   │ - path      │
   │ - rooms     │
   └─────────────┘
         │
         │ composed of
         ▼
   ┌─────────────┐
   │PathSegment  │
   │             │
   │ - type      │
   │ - floors    │
   │ - distance  │
   └─────────────┘
```

---

## Data Flow Summary

1. **Initialization**: Create Floor instances with Room collections from PDF transcriptions
2. **Stairwell Setup**: Define Stairwell connecting F1↔F3↔F4
3. **Personnel Creation**: Initialize Person instances at entry points
4. **Greedy Assignment**: For each unassigned room:
   - Calculate 3D distance for all personnel
   - Assign to person with lowest total time
   - Update person position and floor
   - Add path segments (corridor and/or stairwell)
5. **Return to Exit**: Navigate each person to nearest exit
6. **Visualization**: Render each floor with paths, highlight stairwell transitions

All entities are immutable after creation except for Person (which accumulates path and time during simulation).
