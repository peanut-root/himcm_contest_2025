# Simulation Interface Contract

**Feature**: 001-multi-floor-inspection
**Date**: 2025-11-17
**Type**: Python Function Contracts

## Overview

This document defines the public interface for the Multi-Floor Building Inspection Simulation. Since this is a research simulation (not an API), the "contract" consists of the main class methods and their expected inputs/outputs.

---

## MultiFloorBuildingInspection Class

### Constructor

```python
def __init__(self) -> None:
    """
    Initialize the 3-floor building with rooms from F1, F3, F4 PDFs.

    Post-conditions:
        - self.floors contains 3 Floor instances (F1, F3, F4)
        - self.stairwell connects all 3 floors
        - self.rooms contains all rooms across all floors
        - Room data matches PDF floor plans (manual transcription)
    """
```

**Contract**:
- **Input**: None
- **Output**: Initialized MultiFloorBuildingInspection instance
- **Side Effects**: None
- **Guarantees**:
  - All rooms from PDFs are instantiated
  - Stairwell positions match PDF locations (~5000mm from left)
  - Complexity factors assigned per room type (1.0/1.5/1.8)

---

### greedy_assign

```python
def greedy_assign(
    self,
    start1: Tuple[float, float, str] = (0, 10, "F1"),
    start2: Tuple[float, float, str] = (0, 10, "F1"),
    corridor_speed: float = 1.5,
    stairwell_speed_factor: float = 0.5
) -> Tuple[Person, Person]:
    """
    Assign all rooms to 2 personnel using greedy nearest-neighbor algorithm.

    Args:
        start1: Person 1 starting position (x, y, floor)
        start2: Person 2 starting position (x, y, floor)
        corridor_speed: Horizontal movement speed (m/s)
        stairwell_speed_factor: Vertical speed multiplier (0.0-1.0)

    Returns:
        Tuple of (person1, person2) with complete paths and assignments

    Contract:
        - All rooms assigned exactly once (no duplicates, no misses)
        - Paths include stairwell transitions when floor changes
        - Total time = sum(movement_time + inspection_time)
        - Personnel end at nearest exit
    """
```

**Contract Details**:

**Preconditions**:
- `start1, start2`: Valid (x, y, floor) within building bounds
- `corridor_speed`: Positive float (typical: 1.5 m/s)
- `stairwell_speed_factor`: Float in range [0.0, 1.0] (typical: 0.5)

**Postconditions**:
- `person1.rooms + person2.rooms` contains all building rooms (no overlap)
- `person1.path, person2.path` are continuous (no gaps)
- `person1.total_time == sum(movement_times) + sum(inspection_times)` (±5% for rounding)
- Final positions are at exit locations

**Invariants**:
- Room assignment count: `len(person1.rooms) + len(person2.rooms) == total_rooms`
- Path continuity: Each path segment's `end_pos` == next segment's `start_pos`
- Floor consistency: If `path[i].floor != path[i+1].floor`, then `path[i+1].segment_type == "stairwell"`

**Error Handling**:
- `stairwell_speed_factor == 0`: Raise ValueError ("Stairwell speed cannot be zero")
- `start1/start2` on non-existent floor: Raise ValueError ("Invalid floor")

---

### get_sweep_time

```python
def get_sweep_time(self, room: Room) -> float:
    """
    Calculate inspection time for a room using sweep_time_gt formula.

    Args:
        room: Room instance with area and complexity

    Returns:
        Inspection time in seconds

    Contract:
        - Uses randomized visibility (0.0-0.8) and halt probability (0.05-0.3)
        - Time varies between runs for same room (randomization)
        - Follows USAR ground truth model
    """
```

**Contract**:
- **Input**: Room with valid `area` and `complexity`
- **Output**: Float (inspection time in seconds)
- **Guarantees**:
  - Time > 0 for all rooms (area > 0, complexity >= 1.0)
  - Higher complexity → longer time
  - Larger area → longer time
  - Randomization: multiple calls may return different values

---

### visualize

```python
def visualize(self, person1: Person, person2: Person) -> None:
    """
    Generate 3-floor visualization with personnel paths.

    Args:
        person1: First personnel with complete path
        person2: Second personnel with complete path

    Side Effects:
        - Creates ./output/ directory if not exists
        - Writes PNG file: ./output/multi_floor_building_inspection.png

    Contract:
        - All 3 floors rendered in vertical stack
        - Room names from PDFs displayed with inspection times
        - Personnel paths color-coded (red, blue)
        - Stairwell transitions marked with dashed lines
        - 300 DPI resolution
    """
```

**Contract**:
- **Inputs**: Two Person instances with populated paths
- **Output**: None (writes to file)
- **Side Effects**: File I/O (creates PNG)
- **Guarantees**:
  - Floor layouts match PDF dimensions (mm → m conversion)
  - All rooms visible with labels
  - All path segments rendered
  - Stairwell positions aligned across floors

---

### print_results

```python
def print_results(self, person1: Person, person2: Person) -> None:
    """
    Print simulation results to stdout.

    Args:
        person1: First personnel with complete path
        person2: Second personnel with complete path

    Output Format:
        - Personnel 1 path: Room1(30s) → Room2(45s) → ... → Exit
        - Personnel 1 stats: Distance (m), Time (s), Room count
        - Personnel 2 path: ...
        - Total distance: (m)
        - Max completion time: (s)

    Contract:
        - Chinese room names preserved
        - Times rounded to nearest second
        - Distances rounded to 1 decimal place
    """
```

**Contract**:
- **Inputs**: Two Person instances
- **Output**: None (prints to stdout)
- **Guarantees**:
  - Text format matches existing single-level simulation
  - All assigned rooms listed in visit order
  - Inspection times shown per room
  - Summary statistics accurate

---

## Usage Example

```python
# Initialize simulation
building = MultiFloorBuildingInspection()

# Run greedy assignment (both start at F1 entrance)
p1, p2 = building.greedy_assign(
    start1=(0, 10, "F1"),
    start2=(0, 10, "F1"),
    corridor_speed=1.5,      # 1.5 m/s
    stairwell_speed_factor=0.5  # 0.75 m/s on stairs
)

# Display results
building.print_results(p1, p2)

# Generate visualization
building.visualize(p1, p2)
```

**Expected Output**:
- Console text summary (room assignments, times, distances)
- PNG file at `./output/multi_floor_building_inspection.png`

---

## Contract Validation

### Automated Checks (in code)

```python
# Sanity check: all rooms assigned exactly once
all_assigned_rooms = set(p1.rooms + p2.rooms)
all_building_rooms = set(r.name for r in building.rooms)
assert all_assigned_rooms == all_building_rooms, "Room assignment mismatch"

# Path continuity check
for i in range(len(p1.path) - 1):
    assert p1.path[i] is connected to p1.path[i+1], "Path gap detected"

# Time consistency check (within 5% tolerance)
manual_time = sum(movement_times) + sum(inspection_times)
assert abs(p1.total_time - manual_time) / manual_time < 0.05, "Time calculation error"
```

### Visual Validation

- Inspect generated PNG for:
  - [ ] All room names match PDFs
  - [ ] Stairwell positions aligned vertically
  - [ ] Personnel paths have no gaps
  - [ ] Stairwell transitions shown with different styling
  - [ ] Room count matches expected (F1: 7, F3: 5, F4: 5 = 17 total)

---

## Non-Functional Requirements

| Requirement | Contract |
|-------------|----------|
| **Performance** | Execution < 5 seconds for 3-floor, 20-room building |
| **Scalability** | Supports up to 10 floors, 50 rooms (< 30 seconds) |
| **Memory** | < 100MB for typical 3-floor scenario |
| **Output Quality** | 300 DPI PNG, readable room labels |
| **Accuracy** | Time calculations within 5% of manual verification |
| **Correctness** | 100% room coverage (no misses/duplicates) |

---

## Error Handling Contracts

| Error Condition | Expected Behavior |
|-----------------|-------------------|
| Stairwell speed factor = 0 | Raise ValueError with descriptive message |
| Invalid floor in start position | Raise ValueError listing valid floors |
| Room with area = 0 | Raise ValueError during Room initialization |
| No rooms on a floor | Warning logged, floor skipped in visualization |
| Personnel start on non-existent floor | Raise ValueError before assignment starts |

---

## Version Compatibility

- **Python Version**: 3.9+ (uses `@dataclass`, type hints)
- **Dependencies**: numpy, matplotlib (versions per existing requirements)
- **Backward Compatibility**: Maintains interface compatibility with single-level simulation (can coexist in same codebase)
