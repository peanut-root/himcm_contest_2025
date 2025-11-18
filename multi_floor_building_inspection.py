import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
import math


# T008: sweep_time_gt function (copied from complex_single_level_building_inspection.py)
def sweep_time_gt(area, vis, p_halt, clutter, redundancy=False):
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
    overhead = 15 + 0.5 * (area**0.5) * (clutter - 1)
    t = base + comm + overhead
    if redundancy:
        t *= 1.30
    return t


# T009: distance helper function
def distance(x1, y1, x2, y2):
    """Calculate Euclidean distance between two points."""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


# T004: Room dataclass
@dataclass
class Room:
    """Represents an inspectable space within the building."""
    name: str
    floor: str  # "F1", "F2", "F3", "F4"
    x: float  # Top-left x position in meters
    y: float  # Top-left y position in meters
    width: float
    height: float
    door_x: float
    door_y: float
    door_angle: float  # 0/90/180/270 degrees
    complexity: float  # 1.0 (empty), 1.5 (furnished), 1.8 (equipment)
    additional_doors: List[Tuple[float, float, float]] = field(default_factory=list)  # [(x, y, angle), ...]

    @property
    def area(self) -> float:
        """Calculate room area in square meters."""
        return self.width * self.height

    @property
    def door_position(self) -> Tuple[float, float]:
        """Return door position as (x, y) tuple."""
        return (self.door_x, self.door_y)

    @property
    def all_doors(self) -> List[Tuple[float, float, float]]:
        """Return all doors including primary and additional ones."""
        return [(self.door_x, self.door_y, self.door_angle)] + self.additional_doors

    def get_wall_segments(self) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """Return wall segments as line segments, excluding door positions.
        Returns list of ((x1, y1), (x2, y2)) tuples representing walls.
        """
        walls = []
        door_width = 1.2  # Standard door width in meters

        # Get all door positions
        doors = self.all_doors

        # Bottom wall (y = room.y)
        bottom_doors = [(dx, dy, da) for dx, dy, da in doors if da == 270]
        if bottom_doors:
            # Split wall around doors
            sorted_doors = sorted(bottom_doors, key=lambda d: d[0])
            current_x = self.x
            for door_x, door_y, _ in sorted_doors:
                # Add wall segment before door
                if current_x < door_x - door_width/2:
                    walls.append(((current_x, self.y), (door_x - door_width/2, self.y)))
                current_x = door_x + door_width/2
            # Add remaining segment
            if current_x < self.x + self.width:
                walls.append(((current_x, self.y), (self.x + self.width, self.y)))
        else:
            walls.append(((self.x, self.y), (self.x + self.width, self.y)))

        # Top wall (y = room.y + room.height)
        top_doors = [(dx, dy, da) for dx, dy, da in doors if da == 90]
        if top_doors:
            sorted_doors = sorted(top_doors, key=lambda d: d[0])
            current_x = self.x
            for door_x, door_y, _ in sorted_doors:
                if current_x < door_x - door_width/2:
                    walls.append(((current_x, self.y + self.height), (door_x - door_width/2, self.y + self.height)))
                current_x = door_x + door_width/2
            if current_x < self.x + self.width:
                walls.append(((current_x, self.y + self.height), (self.x + self.width, self.y + self.height)))
        else:
            walls.append(((self.x, self.y + self.height), (self.x + self.width, self.y + self.height)))

        # Left wall (x = room.x)
        left_doors = [(dx, dy, da) for dx, dy, da in doors if da == 180]
        if left_doors:
            sorted_doors = sorted(left_doors, key=lambda d: d[1])
            current_y = self.y
            for door_x, door_y, _ in sorted_doors:
                if current_y < door_y - door_width/2:
                    walls.append(((self.x, current_y), (self.x, door_y - door_width/2)))
                current_y = door_y + door_width/2
            if current_y < self.y + self.height:
                walls.append(((self.x, current_y), (self.x, self.y + self.height)))
        else:
            walls.append(((self.x, self.y), (self.x, self.y + self.height)))

        # Right wall (x = room.x + room.width)
        right_doors = [(dx, dy, da) for dx, dy, da in doors if da == 0]
        if right_doors:
            sorted_doors = sorted(right_doors, key=lambda d: d[1])
            current_y = self.y
            for door_x, door_y, _ in sorted_doors:
                if current_y < door_y - door_width/2:
                    walls.append(((self.x + self.width, current_y), (self.x + self.width, door_y - door_width/2)))
                current_y = door_y + door_width/2
            if current_y < self.y + self.height:
                walls.append(((self.x + self.width, current_y), (self.x + self.width, self.y + self.height)))
        else:
            walls.append(((self.x + self.width, self.y), (self.x + self.width, self.y + self.height)))

        return walls


# T005: Floor dataclass
@dataclass
class Floor:
    """Represents a single level of the building."""
    name: str  # "F1", "F2", "F3", "F4"
    rooms: List[Room]
    corridors: List[Tuple[float, float]]
    exits: List[Tuple[float, float]]
    height_offset: float = 0.0  # Vertical offset from ground

    def get_room_by_name(self, name: str) -> Room:
        """Find room by name on this floor."""
        return next((r for r in self.rooms if r.name == name), None)

    def get_all_room_names(self) -> List[str]:
        """Return list of all room names on this floor."""
        return [r.name for r in self.rooms]


# T006: Stairwell dataclass
@dataclass
class Stairwell:
    """Represents vertical connection between floors."""
    name: str
    connected_floors: List[str]  # ["F1", "F2", "F3", "F4"]
    position_per_floor: Dict[str, Tuple[float, float]]
    floor_height: float = 3.0  # Vertical distance per floor (meters)

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


# T007: Person dataclass
@dataclass
class Person:
    """Represents an inspection team member."""
    id: int
    x: float
    y: float
    floor: str  # Current floor
    rooms: List[str] = field(default_factory=list)  # Assigned room names
    path: List[Tuple[float, float, str]] = field(default_factory=list)  # Waypoints: [(x, y, floor), ...]
    inspection_times: List[float] = field(default_factory=list)  # Inspection time per room
    total_distance: float = 0.0
    total_time: float = 0.0

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
        self.inspection_times.append(inspection_time)


class MultiFloorBuildingInspection:
    """Main simulation class for multi-floor building inspection."""

    def __init__(self):
        """Initialize 4-floor building with rooms from F1, F2, F3, F4 floor plans."""
        # T010: Transcribe F1 rooms from F1.pdf (CORRECTED from actual PDF layout)
        # Floor 1 dimensions: 20000mm x 18000mm = 20m x 18m
        # Converting mm to meters by dividing by 1000
        # Coordinate system: origin at bottom-left
        f1_rooms = [
            Room("Toilet", "F1", 0, 13, 4, 5, 2, 13, 270, 1.0),  # Top-left, door on BOTTOM wall
            Room("Coffee", "F1", 4, 13, 16, 5, 12, 13, 270, 1.8),  # Top-right, door on BOTTOM wall
            Room("Public Activity Area", "F1", 9, 5, 11, 6, 14.5, 11, 90, 1.5),  # Middle-right, door on TOP wall
            Room("Entrance", "F1", 0, 4, 5, 7, 5, 7.5, 0, 1.0, [(2.5, 11, 90)]),  # Middle-left, primary door on RIGHT wall, second door on TOP wall
            Room("Stairwell", "F1", 0, 0, 5, 4, 5, 2, 0, 1.0),  # Bottom-left, door on right
            Room("self-service", "F1", 9, 0, 7, 4, 12.5, 4, 90, 1.8),  # Bottom-middle, door on top
            Room("Equipment", "F1", 16, 0, 4, 4, 18, 4, 90, 1.8),  # Bottom-right, door on top (height=4m to match hallway)
        ]

        # T011: Transcribe F2 rooms from F2.png (CORRECTED layout)
        # Floor 2 dimensions: 20000mm x 20000mm = 20m x 20m
        # Coordinate system: origin at bottom-left
        # Horizontal sections: 4m + 8m + 8m = 20m width (Toilet | Reading Room | Reference at top)
        # Bottom sections: 5m + 10m + 2m + 3m = 20m (Stairwell | Exhibition | hallway | Computer/Power)
        # Vertical: 4m (bottom) + 1m (hallway) + 2m (Power) + 7m (Computer) + 1m (hallway) + 5m (top) = 20m
        f2_rooms = [
            Room("Toilet", "F2", 0, 15, 4, 5, 2, 15, 270, 1.0),  # Top row: y=15-20m (5m tall), door at bottom
            Room("Reading Room", "F2", 4, 15, 8, 5, 8, 15, 270, 1.5),  # Top row: y=15-20m (5m tall), door at bottom
            Room("Reference", "F2", 12, 15, 8, 5, 16, 15, 270, 1.5),  # Top row: y=15-20m (5m tall), door at bottom
            Room("Reading Room", "F2", 0, 7, 15, 7, 7.5, 14, 90, 1.5, [(7.5, 7, 270)]),  # Middle: y=7-14m (7m tall), width=15m, door at TOP, second door at BOTTOM
            Room("Computer Room", "F2", 17, 7, 3, 7, 17, 11, 180, 1.8),  # Right side: x=17-20m, y=7-14m (7m tall), width=3m, door on left wall, top wall aligned with Reading Room
            Room("Power Supply", "F2", 17, 5, 3, 2, 17, 6, 180, 1.8),  # Right side: x=17-20m, y=5-7m (2m tall), directly below Computer Room, door on left wall
            Room("Stairwell", "F2", 0, 0, 5, 4, 2.5, 4, 90, 1.0),  # Bottom-left: y=0-4m, door on top
            Room("Public Exhibition Hall", "F2", 5, 0, 10, 4, 10, 4, 90, 1.5),  # Bottom-middle: y=0-4m, width=10m, door on top
        ]

        # T012: Transcribe F3 rooms from F3.pdf (CORRECTED from actual PDF layout)
        # Floor 3 dimensions: 20000mm x 18000mm = 20m x 18m (same as F1)
        # Coordinate system: origin at bottom-left
        # Vertical sections: 4m (bottom) + 2m (corridor) + 7m (middle) + 2m (corridor) + 3m (top) = 18m total
        f3_rooms = [
            Room("Multi-media", "F3", 0, 15, 4, 3, 2, 15, 270, 1.8),  # Top row: y=15-18m (3m tall), door at bottom
            Room("Specialty Museum", "F3", 4, 15, 12, 3, 10, 15, 270, 1.5),  # Top row: y=15-18m (3m tall), door at bottom
            Room("Erotic reading materials", "F3", 16, 15, 4, 3, 18, 15, 270, 1.8),  # Top row: y=15-18m (3m tall), door at bottom
            Room("Children's Exhibition Room", "F3", 0, 6, 15, 7, 7.5, 6, 270, 1.5, [(7.5, 13, 90)]),  # Middle: y=6-13m (7m tall), width=15m, door at BOTTOM, second door at TOP
            Room("parent-child interaction", "F3", 17, 0, 3, 13, 17, 6.5, 180, 1.5),  # Right side: y=0-13m (13m tall), width=3m, 2m hallway at x=15-17m
            Room("Stairwell", "F3", 0, 0, 5, 4, 2.5, 4, 90, 1.0),  # Bottom row: y=0-4m, door on top
            Room("Toilet", "F3", 5, 0, 5, 4, 7.5, 4, 90, 1.0),  # Bottom row: y=0-4m, door on top
        ]

        # T013: Transcribe F4 rooms from F4.pdf (CORRECTED from actual PDF layout)
        # Floor 4 dimensions: 20000mm x 18000mm = 20m x 18m (same as F1 and F3)
        # Coordinate system: origin at bottom-left
        # Vertical sections: 4m (bottom) + 2m (corridor) + 7m (middle) + 2m (corridor) + 3m (top) = 18m total
        f4_rooms = [
            Room("Office", "F4", 0, 15, 4, 3, 2, 15, 270, 1.0),  # Top row: y=15-18m (3m tall), door at bottom
            Room("Meeting", "F4", 4, 15, 8, 3, 8, 15, 270, 1.5),  # Top row: y=15-18m (3m tall), door at bottom
            Room("Meeting", "F4", 12, 15, 8, 3, 16, 15, 270, 1.5),  # Top row: y=15-18m (3m tall), door at bottom
            Room("Professional bookstore", "F4", 0, 6, 15, 7, 7.5, 13, 90, 1.5, [(7.5, 6, 270)]),  # Middle: y=6-13m (7m tall), width=15m, door at top, second door at bottom
            Room("Office", "F4", 17, 0, 3, 13, 17, 6.5, 180, 1.0),  # Right side: y=0-13m (13m tall), width=3m, 2m hallway at x=15-17m
            Room("Stairwell", "F4", 0, 0, 5, 4, 2.5, 4, 90, 1.0),  # Bottom row: y=0-4m, door on top
            Room("Toilet", "F4", 5, 0, 5, 4, 7.5, 4, 90, 1.0),  # Bottom row: y=0-4m, door on top
        ]

        # T014: Create 4 Floor instances (UPDATED: F1, F2, F3, F4)
        self.floors = [
            Floor("F1", f1_rooms, [(5, 9), (9, 9), (5, 5), (9, 5)], [(1, 4)], 0.0),  # Ground floor, exit at Entrance
            Floor("F2", f2_rooms, [(8.5, 5), (8.5, 14), (5, 2)], [(2.5, 2)], 3.0),  # 3m above F1
            Floor("F3", f3_rooms, [(8.5, 5), (8.5, 14), (5, 2)], [(2.5, 2)], 6.0),  # 6m above F1
            Floor("F4", f4_rooms, [(8.5, 5), (8.5, 14), (5, 2)], [(2.5, 2)], 9.0),  # 9m above F1
        ]

        # Collect all rooms
        self.rooms = f1_rooms + f2_rooms + f3_rooms + f4_rooms

        # T015: Create Stairwell connecting F1↔F2↔F3↔F4 (4 floors)
        self.stairwell = Stairwell(
            "Main Stairwell",
            ["F1", "F2", "F3", "F4"],
            {
                "F1": (2.5, 2),   # Stairwell door position on F1 (center of stairwell)
                "F2": (2.5, 2),   # Stairwell door position on F2 (vertically aligned)
                "F3": (2.5, 2),   # Stairwell door position on F3 (vertically aligned)
                "F4": (2.5, 2),   # Stairwell door position on F4 (vertically aligned)
            },
            3.0  # 3 meters per floor
        )

        # Exit positions (main exits for return-to-exit logic)
        self.exit1 = (1, 4)  # F1 Entrance door
        self.exit2 = (2.5, 2)  # F2/F4 Stairwell (to go down to F1 exit)

        # Define hallway networks for each floor
        self._build_hallway_networks()

        # Enhance hallway graphs with door connections (after rooms are defined)
        for floor_name in ["F1", "F2", "F3", "F4"]:
            self._enhance_hallway_graph_with_doors(floor_name)

    # ========================================================================
    # Geometric Helper Methods (transplanted from single-level building)
    # ========================================================================

    def _line_intersects_segment(self, px1, py1, px2, py2, qx1, qy1, qx2, qy2):
        """Check if two line segments intersect using CCW algorithm."""
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

        A, B = (px1, py1), (px2, py2)
        C, D = (qx1, qy1), (qx2, qy2)
        return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

    def _point_near_door(self, x, y, room, tolerance=0.5):
        """Check if a point is near any door of a room."""
        for door_x, door_y, _ in room.all_doors:
            if abs(x - door_x) < tolerance and abs(y - door_y) < tolerance:
                return True
        return False

    def _line_crosses_wall(self, x1, y1, x2, y2, room):
        """Check if a line segment crosses any wall of a room (excluding doors)."""
        wall_segments = room.get_wall_segments()

        for (wx1, wy1), (wx2, wy2) in wall_segments:
            if self._line_intersects_segment(x1, y1, x2, y2, wx1, wy1, wx2, wy2):
                return True
        return False

    def _point_in_room(self, x, y, room):
        """Check if a point is inside a room."""
        return (room.x <= x <= room.x + room.width and
                room.y <= y <= room.y + room.height)

    def _can_move_directly(self, pos1, pos2, floor_name):
        """Check if two positions can be connected directly without crossing walls.

        This is the core wall-respect validation method.
        """
        x1, y1 = pos1
        x2, y2 = pos2

        # Get all rooms on this floor
        floor = next((f for f in self.floors if f.name == floor_name), None)
        if not floor:
            return True

        # Check each room for wall collisions
        for room in floor.rooms:
            # Check if both points are in the same room (allow internal movement)
            p1_in_room = self._point_in_room(x1, y1, room)
            p2_in_room = self._point_in_room(x2, y2, room)

            if p1_in_room and p2_in_room:
                # Both in same room - allow
                continue

            # Check if line crosses any wall
            if self._line_crosses_wall(x1, y1, x2, y2, room):
                # Wall crossing detected - only allow if through a door
                p1_near_door = self._point_near_door(x1, y1, room, tolerance=0.6)
                p2_near_door = self._point_near_door(x2, y2, room, tolerance=0.6)

                # Allow if entering/exiting through door
                if not (p1_near_door or p2_near_door):
                    return False

        return True

    def _build_hallway_networks(self):
        """Build hallway graph for each floor based on actual corridor layout."""
        self.hallway_graphs = {}

        # F1 Hallway Network - H-shaped corridors
        # Vertical corridor at x=5 (between Entrance/Stairwell and activity areas)
        # Horizontal corridors at y=4, y=11, y=13
        f1_hallways = [
            # Exit and stairwell connections
            ((1, 4), (5, 4)),   # Exit to main corridor
            ((2.5, 2), (5, 2)), # Stairwell to vertical corridor
            # Main vertical corridor (x=5)
            ((5, 2), (5, 4)),   # Stairwell to lower horizontal
            ((5, 4), (5, 11)),  # Lower to upper horizontal
            ((5, 11), (5, 13)), # Upper horizontal to top
            # Lower horizontal corridor (y=4)
            ((5, 4), (9, 4)),   # Vertical to self-service
            ((9, 4), (12.5, 4)), # To self-service door
            ((12.5, 4), (18, 4)), # To Equipment door
            # Middle horizontal corridor (y=11)
            ((2.5, 11), (5, 11)), # Entrance top door to vertical (ADDED: connects to Entrance's additional door)
            ((5, 11), (9, 11)),   # Vertical to Public Activity
            ((9, 11), (14.5, 11)), # To Public Activity door
            # Top horizontal corridor (y=13)
            ((2, 13), (5, 13)),   # Toilet to Coffee
            ((5, 13), (12, 13)),  # Coffee door area
        ]
        self.hallway_graphs["F1"] = self._build_graph_from_segments(f1_hallways)

        # F2 Hallway Network - vertical hallway at x=15-17, horizontal at y=4-5, y=14-15
        f2_hallways = [
            # Stairwell connection
            ((2.5, 2), (2.5, 4)), # Stairwell to corridor
            # Bottom horizontal corridor (y=4-5)
            ((2.5, 4), (5, 4)),   # Stairwell to corridor
            ((5, 4), (7.5, 4)),   # To Reading Room bottom door area (ADDED: waypoint for Reading Room's additional door)
            ((7.5, 4), (10, 4)),  # Continue to Public Exhibition Hall door
            ((10, 4), (16, 4)),   # Corridor extends to vertical hallway (FIXED: connect to x=16)
            ((16, 4), (16, 5)),   # Short vertical to connect to Power Supply level (FIXED: start at x=16)
            # Vertical hallway (x=16, from y=5 to y=14) - corridor along left wall
            ((16, 5), (16, 6)),   # Power Supply door access
            ((16, 6), (16, 7)),   # Continue up
            ((16, 7), (16, 11)),  # Computer Room door access (left wall of hallway)
            ((16, 11), (16, 14)), # Continue to horizontal hallway at y=14-15
            # Lower vertical access for Reading Room bottom door (ADDED: connects (7.5, 4) to (7.5, 7))
            ((7.5, 4), (7.5, 7)), # Vertical to Reading Room bottom door
            # Middle vertical corridor connecting Reading Room's top door (7.5, 14) to upper corridor
            ((7.5, 7), (7.5, 14)), # Vertical from Reading Room bottom door to top door (FIXED: connect top door)
            ((7.5, 14), (7.5, 15)), # Reading Room top door to upper corridor
            # Middle horizontal corridor (y=14-15) - between Computer Room/Reading Room top and Reference
            ((7.5, 14), (16, 14)), # Connect Reading Room top area to Computer Room area (FIXED: add horizontal connection)
            ((16, 14), (18, 14)), # Hallway above Computer Room (aligned with Reading Room top)
            ((18, 14), (18, 15)), # Corner connection to top hallway
            # Upper horizontal corridor (y=15)
            ((2, 15), (4, 15)),     # Toilet door area
            ((4, 15), (8, 15)),     # Reading Room door
            ((8, 15), (12, 15)),    # Continue
            ((12, 15), (16, 15)),   # Reference door area
            ((16, 15), (18, 15)),   # Connect to Computer Room area
        ]
        self.hallway_graphs["F2"] = self._build_graph_from_segments(f2_hallways)

        # F3 Hallway Network - similar structure to F4
        f3_hallways = [
            # Stairwell connection
            ((2.5, 2), (2.5, 4)), # Stairwell to corridor
            # Bottom horizontal corridor (y=4-5)
            ((2.5, 4), (5, 4)),   # Stairwell to Toilet
            ((5, 4), (7.5, 4)),   # Toilet to main corridor
            ((7.5, 4), (10, 4)),  # Corridor extends
            # Lower vertical access
            ((7.5, 4), (7.5, 6)),  # To Children's Exhibition bottom door
            ((10, 4), (10, 6)),    # Vertical segment
            # Middle vertical corridor for Children's Exhibition Room (ADDED: connects bottom and top doors)
            ((7.5, 6), (7.5, 13)), # Vertical corridor from bottom door to top door of Children's Exhibition Room
            # Upper horizontal corridor (y=13-15)
            ((7.5, 13), (7.5, 15)), # Children's Exhibition top door to upper corridor (ADDED: waypoint for top door)
            ((7.5, 13), (15, 13)), # Horizontal corridor at y=13 connecting to side corridor (FIXED: connect to (15, 13))
            ((2, 15), (7.5, 15)),   # Multi-media door area
            ((7.5, 15), (10, 15)),  # Specialty Museum door
            ((10, 15), (15, 15)),   # Continue towards side corridor
            ((15, 15), (18, 15)),   # To Erotic reading materials door
            # Side corridor (x=17) for parent-child interaction
            ((15, 13), (17, 13)),   # Connect from main corridor to side corridor
            ((17, 2), (17, 6.5)),   # Access to parent-child room
            ((17, 6.5), (17, 13)),  # Continues along side
        ]
        self.hallway_graphs["F3"] = self._build_graph_from_segments(f3_hallways)

        # F4 Hallway Network - same structure as F3
        f4_hallways = [
            # Stairwell connection
            ((2.5, 2), (2.5, 4)), # Stairwell to corridor
            # Bottom horizontal corridor (y=4-5)
            ((2.5, 4), (5, 4)),
            ((5, 4), (7.5, 4)),
            ((7.5, 4), (10, 4)),
            # Lower vertical access
            ((7.5, 4), (7.5, 6)),  # To Professional Bookstore bottom door (ADDED: waypoint for bottom door)
            ((10, 4), (10, 6)),
            # Middle vertical corridor for Professional Bookstore (ADDED: connects bottom and top doors)
            ((7.5, 6), (7.5, 13)), # Vertical corridor from bottom door to top door of Professional Bookstore
            # Upper horizontal corridor (y=13-15)
            ((7.5, 13), (7.5, 15)), # Professional Bookstore top door to upper corridor (ADDED: waypoint for top door)
            ((7.5, 13), (15, 13)), # Horizontal corridor at y=13 connecting to side corridor (FIXED: connect to (15, 13))
            ((2, 15), (7.5, 15)),
            ((7.5, 15), (8, 15)),
            ((8, 15), (15, 15)),
            ((15, 15), (16, 15)),
            # Side corridor (x=17)
            ((15, 13), (17, 13)),   # Connect from main corridor to side corridor
            ((17, 2), (17, 6.5)),
            ((17, 6.5), (17, 13)),
        ]
        self.hallway_graphs["F4"] = self._build_graph_from_segments(f4_hallways)

    def _build_graph_from_segments(self, segments):
        """Build adjacency list graph from hallway segments."""
        from collections import defaultdict
        graph = defaultdict(list)
        for (x1, y1), (x2, y2) in segments:
            graph[(x1, y1)].append((x2, y2))
            graph[(x2, y2)].append((x1, y1))
        return dict(graph)

    def _enhance_hallway_graph_with_doors(self, floor_name):
        """Add door positions to hallway graph and connect them to nearest hallway points."""
        graph = self.hallway_graphs.get(floor_name, {})
        floor = next((f for f in self.floors if f.name == floor_name), None)
        if not floor:
            return

        from collections import defaultdict
        enhanced_graph = defaultdict(list, graph)

        # Add all door positions and connect to nearest hallway nodes
        for room in floor.rooms:
            for door_x, door_y, _ in room.all_doors:
                door_pos = (door_x, door_y)

                # Find nearest hallway point
                min_dist = float('inf')
                nearest_hall_point = None
                for hall_point in graph.keys():
                    d = abs(hall_point[0] - door_x) + abs(hall_point[1] - door_y)
                    if d < min_dist and d < 5.0:  # Only connect if within 5 meters
                        # Validate that connection doesn't cross walls
                        if self._can_move_directly(door_pos, hall_point, floor_name):
                            min_dist = d
                            nearest_hall_point = hall_point

                # Add bidirectional connection
                if nearest_hall_point:
                    if nearest_hall_point not in enhanced_graph[door_pos]:
                        enhanced_graph[door_pos].append(nearest_hall_point)
                    if door_pos not in enhanced_graph[nearest_hall_point]:
                        enhanced_graph[nearest_hall_point].append(door_pos)

        self.hallway_graphs[floor_name] = dict(enhanced_graph)

    def _find_nearest_hallway_point(self, pos, floor_name):
        """Find the nearest hallway junction to a given position."""
        graph = self.hallway_graphs.get(floor_name, {})
        if not graph:
            return pos  # Fallback to original position

        min_dist = float('inf')
        nearest = pos
        for point in graph.keys():
            d = abs(point[0] - pos[0]) + abs(point[1] - pos[1])
            if d < min_dist:
                min_dist = d
                nearest = point
        return nearest

    def _hallway_distance_bfs(self, start, end, floor_name):
        """Calculate shortest path distance through hallways using BFS with wall validation."""
        from collections import deque

        graph = self.hallway_graphs.get(floor_name, {})
        if not graph:
            # Fallback to Euclidean distance
            return distance(start[0], start[1], end[0], end[1])

        # Find nearest hallway points
        start_hall = self._find_nearest_hallway_point(start, floor_name)
        end_hall = self._find_nearest_hallway_point(end, floor_name)

        # Validate connection from start to start_hall
        if not self._can_move_directly(start, start_hall, floor_name):
            # Try direct path if hallway connection is blocked
            if self._can_move_directly(start, end, floor_name):
                return distance(start[0], start[1], end[0], end[1])
            # Otherwise use hallway distance as approximation
            pass

        # BFS to find shortest path with wall validation
        queue = deque([(start_hall, 0)])
        visited = {start_hall}

        while queue:
            current, dist = queue.popleft()

            if current == end_hall:
                # Validate end connection
                if self._can_move_directly(end_hall, end, floor_name):
                    # Add distances from actual positions to hallway points
                    start_offset = distance(start[0], start[1], start_hall[0], start_hall[1])
                    end_offset = distance(end[0], end[1], end_hall[0], end_hall[1])
                    return dist + start_offset + end_offset
                else:
                    # Use approximation
                    return dist + abs(start[0] - start_hall[0]) + abs(start[1] - start_hall[1]) + \
                           abs(end[0] - end_hall[0]) + abs(end[1] - end_hall[1])

            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    # Validate edge with wall collision detection
                    if self._can_move_directly(current, neighbor, floor_name):
                        visited.add(neighbor)
                        edge_dist = distance(neighbor[0], neighbor[1], current[0], current[1])
                        queue.append((neighbor, dist + edge_dist))

        # If no path found, try direct path
        if self._can_move_directly(start, end, floor_name):
            return distance(start[0], start[1], end[0], end[1])

        # Fallback to Manhattan distance
        return abs(end[0] - start[0]) + abs(end[1] - start[1])

    # T015: get_path_distance for same-floor corridor distance via hallways
    def get_path_distance(self, start, end, floor_name=None):
        """Calculate corridor distance between two points on the same floor via hallways."""
        if floor_name:
            return self._hallway_distance_bfs(start, end, floor_name)
        else:
            # Fallback to Manhattan distance if floor not specified
            return abs(end[0] - start[0]) + abs(end[1] - start[1])

    # T016: get_path_distance_3d for multi-floor distance via stairwell
    def get_path_distance_3d(self, person_pos, person_floor, room_door, room_floor):
        """Calculate total distance including stairwell transition if needed."""
        if person_floor == room_floor:
            # Same floor: direct corridor distance via hallways
            return self.get_path_distance(person_pos, room_door, person_floor)
        else:
            # Different floor: to stairwell + vertical + from stairwell
            stair_pos_from = self.stairwell.get_position_on_floor(person_floor)
            stair_pos_to = self.stairwell.get_position_on_floor(room_floor)

            to_stair = self.get_path_distance(person_pos, stair_pos_from, person_floor)
            vertical = self.stairwell.get_vertical_distance(person_floor, room_floor)
            from_stair = self.get_path_distance(stair_pos_to, room_door, room_floor)

            return to_stair + vertical + from_stair

    def get_sweep_time(self, room):
        """Calculate inspection time for a room."""
        vis = random.uniform(0.0, 0.8)
        p_halt = random.uniform(0.05, 0.3)
        return sweep_time_gt(room.area, vis, p_halt, room.complexity)

    def _add_waypoint_path(self, person, target_pos, target_floor):
        """Add a complete waypoint sequence from person's current position to target.

        This ensures all paths are strictly constrained to waypoints in the hallway graph.
        """
        current_pos = (person.x, person.y)
        current_floor = person.floor

        if current_floor == target_floor:
            # Same floor: get waypoint sequence through hallways
            waypoint_path = self._get_hallway_path(current_pos, target_pos, current_floor)

            # Add all waypoints (skip duplicates)
            for waypoint in waypoint_path:
                # Only add if it's different from current position
                if len(person.path) == 0 or person.path[-1][:2] != waypoint:
                    person.add_waypoint(waypoint[0], waypoint[1], current_floor)

            # Update person's position to target
            person.x, person.y = waypoint_path[-1][0], waypoint_path[-1][1]

        else:
            # Different floors: need stairwell transition
            stair_pos_from = self.stairwell.get_position_on_floor(current_floor)
            stair_pos_to = self.stairwell.get_position_on_floor(target_floor)

            # 1. Path to stairwell on current floor
            path_to_stair = self._get_hallway_path(current_pos, stair_pos_from, current_floor)
            for waypoint in path_to_stair:
                if len(person.path) == 0 or person.path[-1][:2] != waypoint:
                    person.add_waypoint(waypoint[0], waypoint[1], current_floor)

            # 2. Stairwell transition (just add waypoint on new floor)
            person.floor = target_floor
            if len(person.path) == 0 or person.path[-1][:2] != stair_pos_to:
                person.add_waypoint(stair_pos_to[0], stair_pos_to[1], target_floor)

            # 3. Path from stairwell to target on new floor
            path_from_stair = self._get_hallway_path(stair_pos_to, target_pos, target_floor)
            for waypoint in path_from_stair:
                if len(person.path) == 0 or person.path[-1][:2] != waypoint:
                    person.add_waypoint(waypoint[0], waypoint[1], target_floor)

            # Update person's position to target
            person.x, person.y = path_from_stair[-1][0], path_from_stair[-1][1]

    # T019: find_nearest_exit
    def find_nearest_exit(self, person):
        """Find nearest exit for a person."""
        # Check F1 exit
        if person.floor == "F1":
            dist1 = self.get_path_distance((person.x, person.y), self.exit1, "F1")
            return self.exit1, "F1", dist1

        # For other floors, compare going to F1 exit vs staying on floor
        stair_pos = self.stairwell.get_position_on_floor(person.floor)
        to_stair = self.get_path_distance((person.x, person.y), stair_pos, person.floor)

        # Go down to F1 exit
        vertical = self.stairwell.get_vertical_distance(person.floor, "F1")
        from_stair = self.get_path_distance(self.stairwell.get_position_on_floor("F1"), self.exit1, "F1")
        dist_to_f1 = to_stair + vertical + from_stair

        return self.exit1, "F1", dist_to_f1

    # T017-T018-T020: greedy_assign with 3D distance heuristic and stairwell logic
    def greedy_assign(self, start1=(1, 4, "F1"), start2=(1, 4, "F1")):
        """Assign rooms to 2 personnel using greedy nearest-neighbor algorithm."""
        # Initialize personnel
        person1 = Person(1, start1[0], start1[1], start1[2])
        person2 = Person(2, start2[0], start2[1], start2[2])
        person1.add_waypoint(start1[0], start1[1], start1[2])
        person2.add_waypoint(start2[0], start2[1], start2[2])

        unassigned = list(self.rooms)

        while unassigned:
            best_assignment = None
            best_cost = float('inf')

            # For each unassigned room, calculate cost for both personnel
            for room in unassigned:
                door = room.door_position

                # Cost for person1
                dist1 = self.get_path_distance_3d(
                    (person1.x, person1.y), person1.floor,
                    door, room.floor
                )
                move_time1 = dist1 / 1.5  # 1.5 m/s corridor speed
                if person1.floor != room.floor:
                    # Add stairwell time
                    stair_time = self.stairwell.get_transition_time(
                        person1.floor, room.floor, 0.75  # 0.75 m/s stair speed
                    )
                    move_time1 = (dist1 - self.stairwell.get_vertical_distance(person1.floor, room.floor)) / 1.5 + stair_time

                sweep_time1 = self.get_sweep_time(room)
                total_time1_after = person1.total_time + move_time1 + sweep_time1

                # Cost for person2
                dist2 = self.get_path_distance_3d(
                    (person2.x, person2.y), person2.floor,
                    door, room.floor
                )
                move_time2 = dist2 / 1.5
                if person2.floor != room.floor:
                    stair_time = self.stairwell.get_transition_time(
                        person2.floor, room.floor, 0.75
                    )
                    move_time2 = (dist2 - self.stairwell.get_vertical_distance(person2.floor, room.floor)) / 1.5 + stair_time

                sweep_time2 = self.get_sweep_time(room)
                total_time2_after = person2.total_time + move_time2 + sweep_time2

                # Choose person with lowest total time after assignment
                if total_time1_after <= total_time2_after:
                    cost = total_time1_after
                    assignment = (1, room, dist1, move_time1, sweep_time1)
                else:
                    cost = total_time2_after
                    assignment = (2, room, dist2, move_time2, sweep_time2)

                if cost < best_cost:
                    best_cost = cost
                    best_assignment = assignment

            # Execute best assignment
            person_id, room, dist, move_time, sweep_time = best_assignment
            person = person1 if person_id == 1 else person2

            # Add waypoint sequence to room door (handles same-floor and cross-floor paths)
            self._add_waypoint_path(person, room.door_position, room.floor)

            # Update person's distance and time
            person.total_distance += dist
            person.total_time += move_time

            # Record room assignment
            person.assign_room(room, sweep_time)
            person.total_time += sweep_time

            unassigned.remove(room)

        # T020: Return to nearest exit
        for person in [person1, person2]:
            exit_pos, exit_floor, exit_dist = self.find_nearest_exit(person)
            current_floor = person.floor  # Save current floor before it changes

            # Calculate exit time
            if person.floor != exit_floor:
                exit_time = exit_dist / 1.5 + self.stairwell.get_transition_time(current_floor, exit_floor, 0.75)
            else:
                exit_time = exit_dist / 1.5

            # Add waypoint sequence to exit
            self._add_waypoint_path(person, exit_pos, exit_floor)

            # Update distance and time
            person.total_distance += exit_dist
            person.total_time += exit_time

        return person1, person2

    # T029-T030: print_results method
    def print_results(self, person1, person2):
        """Display personnel paths, distances, times."""
        print("=" * 80)
        print("复杂多层建筑房间检查结果")
        print("=" * 80)
        print(f"人员1路径: {' → '.join(person1.rooms)} → 出口")
        print(f"  距离: {person1.total_distance:.1f}m, 时间: {person1.total_time:.0f}s ({person1.total_time/60:.1f}分钟)")
        print(f"人员2路径: {' → '.join(person2.rooms)} → 出口")
        print(f"  距离: {person2.total_distance:.1f}m, 时间: {person2.total_time:.0f}s ({person2.total_time/60:.1f}分钟)")
        print(f"总距离: {person1.total_distance + person2.total_distance:.1f}m")
        print(f"最大完成时间: {max(person1.total_time, person2.total_time):.0f}s ({max(person1.total_time, person2.total_time)/60:.1f}分钟)")
        print("=" * 80)

    # T022: _draw_floor_layout helper
    def _draw_floor_layout(self, ax, floor, person1, person2):
        """Render room rectangles with pastel colors and labels."""
        import matplotlib.patches as patches

        # Color palette for rooms (pastel colors)
        colors = ['#FFE4E1', '#E0FFE0', '#E0E0FF', '#FFFFE0', '#FFE0FF', '#E0FFFF', '#FFEFD5']
        color_idx = 0

        for room in floor.rooms:
            # T022: Draw room rectangle with pastel color
            color = colors[color_idx % len(colors)]
            rect = patches.Rectangle(
                (room.x, room.y), room.width, room.height,
                linewidth=1, edgecolor='black', facecolor=color
            )
            ax.add_patch(rect)

            # T026: Add room inspection time labels
            inspection_time = None
            for person in [person1, person2]:
                # Check if room name appears in any of the person's room assignments
                for idx, room_str in enumerate(person.rooms):
                    if room.name in room_str:
                        if idx < len(person.inspection_times):
                            inspection_time = person.inspection_times[idx]
                        break
                if inspection_time is not None:
                    break

            # Room label with inspection time
            label_text = room.name
            if inspection_time is not None:
                label_text += f"\n({inspection_time:.0f}s)"

            ax.text(
                room.x + room.width / 2, room.y + room.height / 2,
                label_text,
                ha='center', va='center', fontsize=8, wrap=True
            )

            # T023: Draw door wedges with correct angles (including additional doors)
            door_radius = 0.5  # 0.5 meters
            for door_x, door_y, door_angle in room.all_doors:
                wedge = patches.Wedge(
                    (door_x, door_y), door_radius,
                    door_angle, door_angle + 90,
                    linewidth=1, edgecolor='brown', facecolor='white', alpha=0.7
                )
                ax.add_patch(wedge)

            color_idx += 1

        # Draw corridors (as lighter regions)
        for corridor in floor.corridors:
            ax.plot(corridor[0], corridor[1], 'go', markersize=3, alpha=0.3)

        # Draw exits (marked with green)
        for exit_pos in floor.exits:
            ax.plot(exit_pos[0], exit_pos[1], 'gs', markersize=10, label='Exit' if exit_pos == floor.exits[0] else '')

        # Set axis properties (F1,F4 are 20m×18m, F2 is 20m×20m)
        ax.set_xlim(-1, 21)  # All floors are 20m wide
        if floor.name == "F2":
            ax.set_ylim(-1, 21)  # F2 is 20m tall
        else:
            ax.set_ylim(-1, 19)  # F1 and F4 are 18m tall
        ax.set_aspect('equal')
        ax.set_title(f'{floor.name} (Height: {floor.height_offset:.1f}m)', fontsize=12, fontweight='bold')
        ax.set_xlabel('X (meters)')
        ax.set_ylabel('Y (meters)')
        ax.grid(True, alpha=0.3)

    def _get_hallway_path(self, start, end, floor_name):
        """Get the actual path through hallways as a sequence of waypoints only.

        Returns:
            List of waypoint tuples (x, y) that form a valid path through the hallway network.
            All returned points are guaranteed to be in the hallway graph (waypoints only).
        """
        from collections import deque

        graph = self.hallway_graphs.get(floor_name, {})
        if not graph:
            return [start, end]

        # Check if start and end are already in the graph
        start_in_graph = start in graph
        end_in_graph = end in graph

        # Use start/end directly if they're in the graph, otherwise find nearest
        start_hall = start if start_in_graph else self._find_nearest_hallway_point(start, floor_name)
        end_hall = end if end_in_graph else self._find_nearest_hallway_point(end, floor_name)

        # If start and end are the same waypoint, return single point
        if start_hall == end_hall:
            return [start_hall]

        # BFS to find shortest path through waypoints (NO WALL VALIDATION - graph already validated)
        queue = deque([(start_hall, [start_hall])])
        visited = {start_hall}

        while queue:
            current, path = queue.popleft()

            if current == end_hall:
                # Return path as sequence of waypoints (no intermediate points)
                return path

            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        # CRITICAL: If no path found, this means the graph is disconnected!
        # Try to find ANY path to end_hall from any visited node
        print(f"WARNING: No direct path from {start_hall} to {end_hall} on {floor_name}")
        print(f"  Visited {len(visited)} nodes, graph has {len(graph)} nodes")

        # Return single-point path to avoid disconnected segments
        return [start_hall]

    # T024: _draw_paths_on_floor helper
    def _draw_paths_on_floor(self, ax, floor, person, color, person_id):
        """Trace personnel path on a specific floor as strict waypoint-to-waypoint segments."""
        # Filter waypoints for this floor with their global indices
        floor_waypoints_with_indices = [(i, wp[0], wp[1]) for i, wp in enumerate(person.path) if wp[2] == floor.name]

        if not floor_waypoints_with_indices:
            return

        # Draw path segments ONLY between consecutive waypoints (strict constraint)
        for i in range(len(floor_waypoints_with_indices) - 1):
            idx1, x1, y1 = floor_waypoints_with_indices[i]
            idx2, x2, y2 = floor_waypoints_with_indices[i + 1]

            # Draw direct line between waypoints (no intermediate interpolation)
            ax.plot([x1, x2], [y1, y2], color=color, linewidth=2.5, alpha=0.8, linestyle='-', zorder=5)

            # Add arrow to show direction
            dx, dy = x2 - x1, y2 - y1
            dist = (dx**2 + dy**2)**0.5
            if dist > 0.5:  # Only add arrow if segment is long enough
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                ax.annotate('', xy=(x2, y2), xytext=(mid_x, mid_y),
                          arrowprops=dict(arrowstyle='->', color=color, lw=2, alpha=0.7), zorder=6)

        # Mark waypoints with order numbers
        for i, (global_idx, x, y) in enumerate(floor_waypoints_with_indices):
            # Draw small dot at waypoint
            ax.plot(x, y, 'o', color=color, markersize=6, alpha=0.8,
                   markeredgecolor='white', markeredgewidth=1, zorder=8)

            # Add order number (global index + 1 for 1-based numbering)
            order_num = global_idx + 1
            ax.text(x, y, str(order_num), fontsize=7, color='white',
                   fontweight='bold', ha='center', va='center', zorder=9,
                   bbox=dict(boxstyle='circle,pad=0.25', facecolor=color,
                           edgecolor='white', linewidth=1, alpha=0.9))

        # T027: Add START marker at first waypoint
        if floor_waypoints_with_indices:
            start_idx, start_x, start_y = floor_waypoints_with_indices[0]
            ax.plot(start_x, start_y, marker='o', color=color, markersize=14,
                   markeredgecolor='black', markeredgewidth=2.5, zorder=10)
            ax.text(start_x, start_y - 1.0, f'START {person_id}', fontsize=10,
                   color=color, fontweight='bold', ha='center',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                           edgecolor=color, linewidth=2, alpha=0.95), zorder=11)

            # T027: Add END marker at last waypoint
            end_idx, end_x, end_y = floor_waypoints_with_indices[-1]
            ax.plot(end_x, end_y, marker='s', color=color, markersize=14,
                   markeredgecolor='black', markeredgewidth=2.5, zorder=10)
            ax.text(end_x, end_y - 1.0, f'END {person_id}', fontsize=10,
                   color=color, fontweight='bold', ha='center',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                           edgecolor=color, linewidth=2, alpha=0.95), zorder=11)

    # T021, T025, T028: Main visualize method
    def visualize(self, person1, person2):
        """Generate 4-floor visualization with personnel paths."""
        import matplotlib.pyplot as plt
        import os

        # T021: Create figure with 4-floor vertical stacking
        fig, axes = plt.subplots(4, 1, figsize=(18, 32))
        fig.suptitle('Multi-Floor Building Inspection Simulation', fontsize=16, fontweight='bold')

        # Draw each floor
        for idx, floor in enumerate(self.floors):
            ax = axes[idx]

            # T022, T023, T026: Draw floor layout with rooms and doors
            self._draw_floor_layout(ax, floor, person1, person2)

            # T024, T027: Draw personnel paths (red for Person 1, blue for Person 2)
            self._draw_paths_on_floor(ax, floor, person1, 'red', 1)
            self._draw_paths_on_floor(ax, floor, person2, 'blue', 2)

        # T025: Add stairwell transition visual markers (dashed purple lines between subplots)
        # Analyze stairwell transitions for each person
        for person, color in [(person1, 'red'), (person2, 'blue')]:
            for i in range(len(person.path) - 1):
                x1, y1, floor1 = person.path[i]
                x2, y2, floor2 = person.path[i + 1]

                if floor1 != floor2:
                    # Floor transition detected - draw connector
                    floor1_idx = [f.name for f in self.floors].index(floor1)
                    floor2_idx = [f.name for f in self.floors].index(floor2)

                    # Draw annotation on both floors
                    axes[floor1_idx].annotate(
                        f'→ {floor2}', xy=(x1, y1), xytext=(x1 + 1, y1 + 1),
                        fontsize=8, color='purple', fontweight='bold',
                        arrowprops=dict(arrowstyle='->', color='purple', linestyle='--', linewidth=2)
                    )
                    axes[floor2_idx].annotate(
                        f'← {floor1}', xy=(x2, y2), xytext=(x2 + 1, y2 + 1),
                        fontsize=8, color='purple', fontweight='bold',
                        arrowprops=dict(arrowstyle='->', color='purple', linestyle='--', linewidth=2)
                    )

        plt.tight_layout(rect=[0, 0, 1, 0.98])

        # T028: Save visualization to ./output/multi_floor_building_inspection.png at 300 DPI
        os.makedirs('./output', exist_ok=True)
        output_path = './output/multi_floor_building_inspection.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n可视化已保存到: {output_path}")
        plt.close()


# T031-T034: Main execution
def main():
    """Main execution function."""
    building = MultiFloorBuildingInspection()
    p1, p2 = building.greedy_assign()
    building.print_results(p1, p2)
    building.visualize(p1, p2)


if __name__ == "__main__":
    main()
