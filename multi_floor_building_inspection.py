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
    floor: str  # "F1", "F3", "F4"
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


# T005: Floor dataclass
@dataclass
class Floor:
    """Represents a single level of the building."""
    name: str  # "F1", "F3", "F4"
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
    connected_floors: List[str]  # ["F1", "F3", "F4"]
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
        """Initialize 3-floor building with rooms from F1, F3, F4 PDFs."""
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

        # T011: Transcribe F3 rooms from F3.pdf (CORRECTED from actual PDF layout)
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

        # T012: Transcribe F4 rooms from F4.pdf (CORRECTED from actual PDF layout)
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

        # T013: Create 3 Floor instances (CORRECTED to match actual PDF layouts)
        self.floors = [
            Floor("F1", f1_rooms, [(5, 9), (9, 9), (5, 5), (9, 5)], [(1, 4)], 0.0),  # Ground floor, exit at Entrance
            Floor("F3", f3_rooms, [(8.5, 5), (8.5, 14), (5, 2)], [(2.5, 2)], 3.0),  # 3m above F1, corridors at y=5 and y=14
            Floor("F4", f4_rooms, [(8.5, 5), (8.5, 14), (5, 2)], [(2.5, 2)], 6.0),  # 6m above F1, corridors at y=5 and y=14
        ]

        # Collect all rooms
        self.rooms = f1_rooms + f3_rooms + f4_rooms

        # T014: Create Stairwell connecting F1↔F3↔F4 (CORRECTED to match PDF positions)
        self.stairwell = Stairwell(
            "Main Stairwell",
            ["F1", "F3", "F4"],
            {
                "F1": (2.5, 2),   # Stairwell door position on F1 (center of stairwell)
                "F3": (2.5, 2),   # Stairwell door position on F3 (vertically aligned)
                "F4": (2.5, 2),   # Stairwell door position on F4 (vertically aligned)
            },
            3.0  # 3 meters per floor
        )

        # Exit positions (main exits for return-to-exit logic)
        self.exit1 = (1, 4)  # F1 Entrance door
        self.exit2 = (2.5, 2)  # F3/F4 Stairwell (to go down to F1 exit)

        # Define hallway networks for each floor
        self._build_hallway_networks()

    def _build_hallway_networks(self):
        """Build hallway graph for each floor based on actual corridor layout."""
        self.hallway_graphs = {}

        # F1 Hallway Network - H-shaped corridors
        # Vertical corridor at x=5 (between Entrance/Stairwell and activity areas)
        # Horizontal corridors at y=4, y=11, y=13
        f1_hallways = [
            # Main vertical corridor (x=5)
            ((5, 2), (5, 4)),   # Stairwell to lower horizontal
            ((5, 4), (5, 11)),  # Lower to upper horizontal
            ((5, 11), (5, 13)), # Upper horizontal to top
            # Lower horizontal corridor (y=4)
            ((5, 4), (9, 4)),   # Vertical to self-service
            ((9, 4), (12.5, 4)), # To self-service door
            ((12.5, 4), (18, 4)), # To Equipment door
            # Middle horizontal corridor (y=11)
            ((2.5, 11), (5, 11)), # Entrance door to vertical
            ((5, 11), (9, 11)),   # Vertical to Public Activity
            ((9, 11), (14.5, 11)), # To Public Activity door
            # Top horizontal corridor (y=13)
            ((2, 13), (5, 13)),   # Toilet to Coffee
            ((5, 13), (12, 13)),  # Coffee door area
        ]
        self.hallway_graphs["F1"] = self._build_graph_from_segments(f1_hallways)

        # F3 Hallway Network - corridors at y=4-6, y=13-15
        f3_hallways = [
            # Bottom horizontal corridor (y=4-5)
            ((2.5, 4), (5, 4)),   # Stairwell to corridor
            ((5, 4), (7.5, 4)),   # To Toilet door
            ((7.5, 4), (10, 4)),  # Corridor continues
            # Lower vertical access (around y=6)
            ((7.5, 4), (7.5, 6)), # Vertical to Children's Exhibition bottom door
            ((10, 4), (10, 6)),   # Side corridor access
            # Upper horizontal corridor (y=13-14)
            ((7.5, 13), (7.5, 15)), # Children's Exhibition top door to upper corridor
            ((2, 15), (7.5, 15)),   # Multi-media door area
            ((7.5, 15), (10, 15)),  # Specialty Museum door area
            ((10, 15), (18, 15)),   # To Erotic reading materials door
            # Side corridor (x=17)
            ((17, 2), (17, 6.5)),   # parent-child interaction door access
            ((17, 6.5), (17, 13)),  # Extends vertically
        ]
        self.hallway_graphs["F3"] = self._build_graph_from_segments(f3_hallways)

        # F4 Hallway Network - same structure as F3
        f4_hallways = [
            # Bottom horizontal corridor (y=4-5)
            ((2.5, 4), (5, 4)),
            ((5, 4), (7.5, 4)),
            ((7.5, 4), (10, 4)),
            # Lower vertical access
            ((7.5, 4), (7.5, 6)),
            ((10, 4), (10, 6)),
            # Upper horizontal corridor (y=13-14)
            ((7.5, 13), (7.5, 15)),
            ((2, 15), (7.5, 15)),
            ((7.5, 15), (8, 15)),
            ((8, 15), (16, 15)),
            # Side corridor (x=17)
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
        """Calculate shortest path distance through hallways using BFS."""
        from collections import deque

        graph = self.hallway_graphs.get(floor_name, {})
        if not graph:
            # Fallback to Manhattan distance
            return abs(end[0] - start[0]) + abs(end[1] - start[1])

        # Find nearest hallway points
        start_hall = self._find_nearest_hallway_point(start, floor_name)
        end_hall = self._find_nearest_hallway_point(end, floor_name)

        # BFS to find shortest path
        queue = deque([(start_hall, 0)])
        visited = {start_hall}

        while queue:
            current, dist = queue.popleft()

            if current == end_hall:
                # Add distances from actual positions to hallway points
                start_offset = abs(start[0] - start_hall[0]) + abs(start[1] - start_hall[1])
                end_offset = abs(end[0] - end_hall[0]) + abs(end[1] - end_hall[1])
                return dist + start_offset + end_offset

            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    edge_dist = abs(neighbor[0] - current[0]) + abs(neighbor[1] - current[1])
                    queue.append((neighbor, dist + edge_dist))

        # If no path found, use Manhattan distance as fallback
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

            # T018: Handle stairwell transition
            if person.floor != room.floor:
                # Move to stairwell
                stair_pos = self.stairwell.get_position_on_floor(person.floor)
                person.add_waypoint(stair_pos[0], stair_pos[1], person.floor)
                # Transition to new floor via stairwell
                stair_pos_new = self.stairwell.get_position_on_floor(room.floor)
                person.floor = room.floor
                person.add_waypoint(stair_pos_new[0], stair_pos_new[1], room.floor)

            # Move to room
            person.move_to(room.door_x, room.door_y, room.floor, dist, move_time)
            person.assign_room(room, sweep_time)
            person.total_time += sweep_time

            unassigned.remove(room)

        # T020: Return to nearest exit
        for person in [person1, person2]:
            exit_pos, exit_floor, exit_dist = self.find_nearest_exit(person)
            current_floor = person.floor  # Save current floor before it changes
            if person.floor != exit_floor:
                # Go to stairwell
                stair_pos = self.stairwell.get_position_on_floor(person.floor)
                stair_dist = self.get_path_distance((person.x, person.y), stair_pos, current_floor)
                person.add_waypoint(stair_pos[0], stair_pos[1], person.floor)
                person.floor = exit_floor
                # Move down floors
                stair_pos_exit = self.stairwell.get_position_on_floor(exit_floor)
                person.add_waypoint(stair_pos_exit[0], stair_pos_exit[1], exit_floor)
                exit_time = exit_dist / 1.5 + self.stairwell.get_transition_time(person.floor, exit_floor, 0.75)
            else:
                exit_time = exit_dist / 1.5

            person.move_to(exit_pos[0], exit_pos[1], exit_floor, exit_dist, exit_time)

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

        # Set axis properties (all floors are 20m × 18m)
        ax.set_xlim(-1, 21)  # All floors are 20m wide
        ax.set_ylim(-1, 19)  # All floors are 18m tall
        ax.set_aspect('equal')
        ax.set_title(f'{floor.name} (Height: {floor.height_offset:.1f}m)', fontsize=12, fontweight='bold')
        ax.set_xlabel('X (meters)')
        ax.set_ylabel('Y (meters)')
        ax.grid(True, alpha=0.3)

    def _get_hallway_path(self, start, end, floor_name):
        """Get the actual path through hallways using BFS."""
        from collections import deque

        graph = self.hallway_graphs.get(floor_name, {})
        if not graph:
            return [start, end]

        # Find nearest hallway points
        start_hall = self._find_nearest_hallway_point(start, floor_name)
        end_hall = self._find_nearest_hallway_point(end, floor_name)

        # BFS to find shortest path and reconstruct it
        queue = deque([(start_hall, [start_hall])])
        visited = {start_hall}

        while queue:
            current, path = queue.popleft()

            if current == end_hall:
                # Reconstruct full path: start -> start_hall -> ... -> end_hall -> end
                full_path = []
                if start != start_hall:
                    full_path.append(start)
                full_path.extend(path)
                if end != end_hall:
                    full_path.append(end)
                return full_path

            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        # Fallback if no path found
        return [start, end]

    # T024: _draw_paths_on_floor helper
    def _draw_paths_on_floor(self, ax, floor, person, color, person_id):
        """Trace personnel path on a specific floor through hallway centerlines."""
        # Filter waypoints for this floor
        floor_waypoints = [(wp[0], wp[1]) for wp in person.path if wp[2] == floor.name]

        if not floor_waypoints:
            return

        # Draw path segments through actual hallways
        for i in range(len(floor_waypoints) - 1):
            start_pos = floor_waypoints[i]
            end_pos = floor_waypoints[i + 1]

            # Get hallway path between waypoints
            hallway_path = self._get_hallway_path(start_pos, end_pos, floor.name)

            # Draw the path along hallway centerlines
            for j in range(len(hallway_path) - 1):
                x1, y1 = hallway_path[j]
                x2, y2 = hallway_path[j + 1]
                ax.plot([x1, x2], [y1, y2], color=color, linewidth=2.5, alpha=0.8, linestyle='-')

            # Add sequence numbers at waypoints (door positions)
            ax.text(start_pos[0], start_pos[1], str(i + 1), fontsize=8, color=color,
                   bbox=dict(boxstyle='circle', facecolor='white', alpha=0.8))

        # T027: Add START marker at first waypoint
        if floor_waypoints:
            start_x, start_y = floor_waypoints[0]
            ax.plot(start_x, start_y, marker='o', color=color, markersize=12,
                   markeredgecolor='black', markeredgewidth=2)
            ax.text(start_x, start_y - 0.8, f'START {person_id}', fontsize=9,
                   color=color, fontweight='bold', ha='center',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

            # T027: Add END marker at last waypoint
            end_x, end_y = floor_waypoints[-1]
            ax.plot(end_x, end_y, marker='s', color=color, markersize=12,
                   markeredgecolor='black', markeredgewidth=2)
            ax.text(end_x, end_y - 0.8, f'END {person_id}', fontsize=9,
                   color=color, fontweight='bold', ha='center',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    # T021, T025, T028: Main visualize method
    def visualize(self, person1, person2):
        """Generate 3-floor visualization with personnel paths."""
        import matplotlib.pyplot as plt
        import os

        # T021: Create figure with 3-floor vertical stacking
        fig, axes = plt.subplots(3, 1, figsize=(18, 24))
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
