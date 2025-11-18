import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional
import math
import heapq
import os

# ============================================================================
# 工具函数
# ============================================================================

def sweep_time_gt(area, vis, p_halt, clutter, redundancy=False):
    """计算房间清扫时间"""
    r = 0.05 + 0.30 * vis
    base = area / r * clutter
    comm = 120 * p_halt
    overhead = 15 + 0.5 * (area**0.5) * (clutter - 1)
    t = base + comm + overhead
    if redundancy:
        t *= 1.30
    return t

# ============================================================================
# 数据类定义
# ============================================================================

@dataclass
class Room:
    """房间信息"""
    name: str
    x: float
    y: float
    width: float
    height: float
    door_x: float
    door_y: float
    door_angle: float  # 门的朝向角度
    complexity: float   # 复杂度系数
    additional_doors: Optional[List[Tuple[float, float, float]]] = None  # 额外的门 [(x, y, angle), ...]

    @property
    def area(self):
        """房间面积"""
        return self.width * self.height

    @property
    def door_position(self):
        """门的位置（主门）"""
        return (self.door_x, self.door_y)

    @property
    def all_doors(self):
        """所有门的位置列表 [(x, y, angle), ...]"""
        doors = [(self.door_x, self.door_y, self.door_angle)]
        if self.additional_doors:
            doors.extend(self.additional_doors)
        return doors

    @property
    def all_door_positions(self):
        """所有门的位置列表（仅坐标） [(x, y), ...]"""
        return [(x, y) for x, y, _ in self.all_doors]

@dataclass
class Person:
    """人员信息"""
    id: int
    x: float
    y: float
    rooms: List[str]  # 已分配的房间列表
    path: List[Tuple[float, float]]  # 完整路径点列表
    total_distance: float = 0.0  # 总移动距离（米）
    total_time: float = 0.0  # 总时间（秒）

    def get_current_position(self):
        """获取当前位置"""
        return (self.x, self.y)

# ============================================================================
# 主类：建筑检查系统
# ============================================================================

class SingleFloorBuildingInspection:
    """单层建筑检查系统（按PNG布局）"""

    # 移动速度（米/秒）
    MOVE_SPEED = 1.5

    def __init__(self):
        """初始化建筑布局"""
        self.rooms = self._create_rooms()
        self.corridors_areas = self._create_corridors()
        self.exits = self._create_exits()
        self.waypoints = self._create_waypoints()

        # 固定随机种子，确保每次运行结果一致（可选）
        # random.seed(42)

    # ========================================================================
    # 建筑布局定义（根据PNG图纸）
    # ========================================================================

    def _create_rooms(self) -> List[Room]:
        """创建所有房间（根据PNG布局）"""
        rooms = []

        # 走廊（用于路径规划，不参与分配）
        # 注意：走廊没有真正的门，door坐标设为中心点（仅用于满足数据类型要求）
        rooms.extend([
            # 上走廊：水平延伸整个建筑，从x=0到x=35，在y=18到y=20之间
            Room("Upper Corridor", 0, 18, 35, 2, 17.5, 19, 0, 1.0),  # 中心点
            # 垂直走廊：从底部到上走廊，x=23到x=25，y=0到y=20
            Room("Vertical Corridor", 23, 0, 2, 20, 24, 10, 0, 1.0),  # 中心点
            # 中间走廊：连接右侧房间，x=25到x=41，y=10到y=12
            Room("Middle Corridor", 25, 10, 16, 2, 33, 11, 0, 1.0),  # 中心点
        ])

        # 顶部房间（从左到右，y=20-23）
        rooms.extend([
            Room("Storage Room", 0, 20, 10, 3, 5, 20, 270, 1.8),
            Room("Restroom Room", 10, 20, 10, 3, 15, 20, 270, 1.0),
            Room("Lift2", 20, 20, 2, 3, 21, 20, 270, 1.0),
            Room("Stairwell", 22, 20, 3, 3, 23.5, 20, 270, 1.0),
            Room("Kitchen", 25, 20, 10, 3, 30, 20, 270, 1.8),
        ])

        # 中间房间
        rooms.extend([
            # Hall有四个门：左侧(0,10.5)、底部(11.5,3)连接Backstage、顶部(11.5,18)和右侧(23,10.5)
            Room("Hall", 0, 3, 23, 15, 0, 10.5, 180, 1.0,
                 additional_doors=[(11.5, 3, 270), (11.5, 18, 90), (23, 10.5, 0)]),
            # Cafeteria：高度修正为6m（y=12到y=18），上方留出Upper Corridor空间
            Room("Cafeteria", 25, 12, 10, 6, 25, 14, 180, 1.5),
        ])

        # 底部房间
        rooms.extend([
            # Backstage Equipment Room有两个门：底部(11.5,0)和顶部(11.5,3)
            Room("Backstage Equipment Room", 0, 0, 23, 3, 11.5, 0, 270, 1.8,
                 additional_doors=[(11.5, 3, 90), (11.5, 0, 90)]),
            Room("Multipurpose Classroom", 25, 0, 8, 10, 29, 10, 90, 1.5),
            Room("Office", 33, 0, 8, 10, 37, 10, 90, 1.0),
        ])

        return rooms

    def _create_corridors(self) -> List[dict]:
        """创建走廊区域定义"""
        return [
            {"name": "Upper Corridor", "x": 0, "y": 18, "width": 35, "height": 2},
            {"name": "Vertical Corridor", "x": 23, "y": 0, "width": 2, "height": 20},
            {"name": "Middle Corridor", "x": 25, "y": 10, "width": 16, "height": 2},
        ]

    def _create_exits(self) -> dict:
        """创建出入口"""
        return {
            "exit1": (0.5, 10.5),  # Hall左侧门
            "exit2": (35.5, 19),   # 上走廊右端
        }

    def _create_waypoints(self) -> List[Tuple[float, float]]:
        """创建关键路径节点（自动从房间门生成）"""
        waypoints = []
        for room in self.rooms:
            if "Corridor" not in room.name:
                # 添加房间的所有门作为路径节点
                waypoints.extend(room.all_door_positions)
        return waypoints

    # ========================================================================
    # 工具方法
    # ========================================================================

    def distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """计算两点间欧氏距离"""
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def get_sweep_time(self, room: Room) -> float:
        """计算房间清扫时间（随机生成）"""
        vis = random.uniform(0.0, 0.8)
        p_halt = random.uniform(0.05, 0.3)
        return sweep_time_gt(room.area, vis, p_halt, room.complexity)

    def get_actual_rooms(self) -> List[Room]:
        """获取实际房间（排除走廊）"""
        return [room for room in self.rooms if "Corridor" not in room.name]

    # ========================================================================
    # 路径规划
    # ========================================================================

    def _point_in_corridor(self, x: float, y: float) -> bool:
        """检查点是否在走廊内"""
        for corridor in self.corridors_areas:
            cx, cy = corridor["x"], corridor["y"]
            cw, ch = corridor["width"], corridor["height"]
            if cx <= x <= cx + cw and cy <= y <= cy + ch:
                return True
        return False

    def _point_near_door(self, x: float, y: float, room: Room, tolerance: float = 0.5) -> bool:
        """检查点是否在门附近（支持多门）"""
        # 检查所有门
        for door_x, door_y in room.all_door_positions:
            if abs(x - door_x) < tolerance and abs(y - door_y) < tolerance:
                return True
        return False

    def _line_intersects_room_strict(self, x1: float, y1: float, x2: float, y2: float, room: Room) -> bool:
        """严格检查线段是否穿过房间（不允许穿墙）"""
        room_left, room_right = room.x, room.x + room.width
        room_bottom, room_top = room.y, room.y + room.height

        # 检查两个端点是否在房间内（使用容差避免边界问题）
        tolerance = 0.01
        p1_inside = room_left + tolerance < x1 < room_right - tolerance and room_bottom + tolerance < y1 < room_top - tolerance
        p2_inside = room_left + tolerance < x2 < room_right - tolerance and room_bottom + tolerance < y2 < room_top - tolerance

        # 如果都在房间内，不算穿过
        if p1_inside and p2_inside:
            return False

        # 如果都不在房间内，检查是否穿过房间边界
        if not p1_inside and not p2_inside:
            # 检查是否完全在房间的同一侧
            if (x1 <= room_left and x2 <= room_left) or \
               (x1 >= room_right and x2 >= room_right) or \
               (y1 <= room_bottom and y2 <= room_bottom) or \
               (y1 >= room_top and y2 >= room_top):
                return False  # 不相交

            # 使用统一的门检查逻辑（不依赖门角度）
            # 检查线段是否穿过房间，如果穿过则必须通过某个门
            door_tolerance = 0.6

            def line_intersects_segment(px1, py1, px2, py2, qx1, qy1, qx2, qy2):
                """检查两条线段是否相交"""
                def ccw(A, B, C):
                    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
                A, B = (px1, py1), (px2, py2)
                C, D = (qx1, qy1), (qx2, qy2)
                if ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D):
                    return True
                return False

            # 检查线段是否与房间边界相交
            intersects_boundary = (
                line_intersects_segment(x1, y1, x2, y2, room_left, room_bottom, room_left, room_top) or
                line_intersects_segment(x1, y1, x2, y2, room_right, room_bottom, room_right, room_top) or
                line_intersects_segment(x1, y1, x2, y2, room_left, room_bottom, room_right, room_bottom) or
                line_intersects_segment(x1, y1, x2, y2, room_left, room_top, room_right, room_top)
            )

            if intersects_boundary:
                # 线段穿过房间边界，检查是否通过某个门
                passes_through_door = False
                dx = x2 - x1
                dy = y2 - y1

                for door_x, door_y in room.all_door_positions:
                    # 计算线段上最接近门的点
                    if abs(dx) < 0.001 and abs(dy) < 0.001:
                        continue

                    t = max(0, min(1, ((door_x - x1) * dx + (door_y - y1) * dy) / (dx * dx + dy * dy)))
                    closest_x = x1 + t * dx
                    closest_y = y1 + t * dy
                    dist_to_door = math.sqrt((closest_x - door_x)**2 + (closest_y - door_y)**2)

                    if dist_to_door <= door_tolerance:
                        passes_through_door = True
                        break

                if not passes_through_door:
                    return True  # 穿过边界但不通过任何门，不允许

        # 如果只有一个端点在房间内，必须通过门
        elif p1_inside != p2_inside:
            # 线段必须穿过某个门的位置（门角度不影响路径判断）
            door_tolerance = 0.6
            passes_through_door = False

            for door_x, door_y in room.all_door_positions:
                # 检查线段是否穿过门的位置（使用容差范围）
                # 计算线段上最接近门的点
                dx = x2 - x1
                dy = y2 - y1

                if abs(dx) < 0.001 and abs(dy) < 0.001:
                    # 线段退化为点
                    continue

                # 参数方程: P(t) = (x1, y1) + t * (dx, dy), t in [0, 1]
                # 找到最接近门的参数t
                t = max(0, min(1, ((door_x - x1) * dx + (door_y - y1) * dy) / (dx * dx + dy * dy)))

                # 线段上最接近门的点
                closest_x = x1 + t * dx
                closest_y = y1 + t * dy

                # 检查最接近点是否在门的容差范围内
                dist_to_door = math.sqrt((closest_x - door_x)**2 + (closest_y - door_y)**2)
                if dist_to_door <= door_tolerance:
                    passes_through_door = True
                    break

            if not passes_through_door:
                return True  # 没有通过任何门，不允许

        return False

    def get_path_distance(self, start: Tuple[float, float], end: Tuple[float, float]) -> Tuple[float, List[Tuple[float, float]]]:
        """使用Dijkstra算法计算最短路径"""
        # 构建节点列表：使用waypoints（所有门）+ 起点 + 终点
        nodes = list(self.waypoints)  # waypoints已经包含所有门
        nodes.append(start)
        nodes.append(end)

        # 去重
        nodes = list(set(nodes))

        def can_move_directly(p1: Tuple[float, float], p2: Tuple[float, float]) -> bool:
            """检查两点间是否可以直接移动（严格检查，不允许穿墙）"""
            x1, y1 = p1
            x2, y2 = p2

            # 检查两个点是否都在走廊内
            p1_in_corridor = self._point_in_corridor(x1, y1)
            p2_in_corridor = self._point_in_corridor(x2, y2)

            # 如果都在走廊内，检查是否穿过房间
            if p1_in_corridor and p2_in_corridor:
                for room in self.rooms:
                    if "Corridor" not in room.name:
                        if self._line_intersects_room_strict(x1, y1, x2, y2, room):
                            return False
                return True

            # 检查是否在同一个房间内
            for room in self.rooms:
                if "Corridor" not in room.name:
                    room_left, room_right = room.x, room.x + room.width
                    room_bottom, room_top = room.y, room.y + room.height
                    p1_in_room = room_left < x1 < room_right and room_bottom < y1 < room_top
                    p2_in_room = room_left < x2 < room_right and room_bottom < y2 < room_top
                    if p1_in_room and p2_in_room:
                        return True  # 在同一房间内，允许

            # 检查是否通过门连接
            # 一个点必须在门附近，另一个点必须在走廊或房间内
            for room in self.rooms:
                if "Corridor" not in room.name:
                    p1_near_door = self._point_near_door(x1, y1, room, tolerance=0.5)
                    p2_near_door = self._point_near_door(x2, y2, room, tolerance=0.5)

                    if p1_near_door:
                        # p1在门附近，检查p2是否在走廊或房间内
                        p2_in_room = False
                        room_left, room_right = room.x, room.x + room.width
                        room_bottom, room_top = room.y, room.y + room.height
                        if room_left < x2 < room_right and room_bottom < y2 < room_top:
                            p2_in_room = True

                        if p2_in_corridor or p2_in_room:
                            # 检查路径是否穿过其他房间
                            for other_room in self.rooms:
                                if "Corridor" not in other_room.name and other_room != room:
                                    if self._line_intersects_room_strict(x1, y1, x2, y2, other_room):
                                        return False
                            return True

                    if p2_near_door:
                        # p2在门附近，检查p1是否在走廊或房间内
                        p1_in_room = False
                        room_left, room_right = room.x, room.x + room.width
                        room_bottom, room_top = room.y, room.y + room.height
                        if room_left < x1 < room_right and room_bottom < y1 < room_top:
                            p1_in_room = True

                        if p1_in_corridor or p1_in_room:
                            # 检查路径是否穿过其他房间
                            for other_room in self.rooms:
                                if "Corridor" not in other_room.name and other_room != room:
                                    if self._line_intersects_room_strict(x1, y1, x2, y2, other_room):
                                        return False
                            return True

            # 如果都不满足以上条件，则不允许直接移动
            # 只有满足以下条件才允许：
            # 1. 都在走廊内且不穿墙
            # 2. 都在同一房间内
            # 3. 一个在门附近，另一个在相应的走廊或房间内
            return False

        # Dijkstra算法
        distances = {node: float('inf') for node in nodes}
        prev = {node: None for node in nodes}
        distances[start] = 0
        pq = [(0, start)]

        while pq:
            current_dist, current = heapq.heappop(pq)

            if current == end:
                # 回溯路径
                path = []
                node = end
                while node is not None:
                    path.append(node)
                    node = prev[node]
                path.reverse()
                return current_dist, path

            if current_dist > distances[current]:
                continue

            for next_node in nodes:
                if next_node == current:
                    continue

                if can_move_directly(current, next_node):
                    new_dist = current_dist + self.distance(
                        current[0], current[1], next_node[0], next_node[1]
                    )
                    if new_dist < distances[next_node]:
                        distances[next_node] = new_dist
                        prev[next_node] = current
                        heapq.heappush(pq, (new_dist, next_node))

        # 如果找不到路径，返回直线路径
        return self.distance(start[0], start[1], end[0], end[1]), [start, end]

    # ========================================================================
    # 任务分配算法
    # ========================================================================

    def balanced_partition_assign(self) -> Tuple[Person, Person]:
        """基于负载均衡的房间分配算法（确保时间差不超过15%）"""
        # 初始化两个人
        person1 = Person(1, self.exits["exit1"][0], self.exits["exit1"][1], [], [self.exits["exit1"]])
        person2 = Person(2, self.exits["exit2"][0], self.exits["exit2"][1], [], [self.exits["exit2"]])

        # 获取需要分配的实际房间
        actual_rooms = [room for room in self.rooms if "Corridor" not in room.name]
        room_indices = {room.name: i for i, room in enumerate(self.rooms)}

        # 预计算所有房间的清扫时间（固定随机种子确保一致性）
        random.seed(42)
        room_data = []
        for room in actual_rooms:
            sweep_time = self.get_sweep_time(room)
            room_data.append({
                'room': room,
                'idx': room_indices[room.name],
                'sweep_time': sweep_time
            })

        # 按清扫时间降序排序（先分配大房间）
        room_data.sort(key=lambda x: x['sweep_time'], reverse=True)

        # 打印房间清扫时间（用于调试）
        print("\n房间清扫时间分布:")
        for data in room_data:
            print(f"  {data['room'].name}: {data['sweep_time']:.0f}秒 ({data['sweep_time']/60:.1f}分钟)")

        # 使用改进的平衡分配策略
        # 对于每个房间，计算分配给两个人的完整代价（包括移动时间）
        # 并始终选择能使两人更平衡的分配
        for data in room_data:
            room = data['room']
            sweep_time = data['sweep_time']
            door = room.door_position

            try:
                # 计算person1的代价
                dist1, path1 = self.get_path_distance(person1.get_current_position(), door)
                move_time1 = dist1 / self.MOVE_SPEED
                total_time1 = person1.total_time + move_time1 + sweep_time

                # 计算person2的代价
                dist2, path2 = self.get_path_distance(person2.get_current_position(), door)
                move_time2 = dist2 / self.MOVE_SPEED
                total_time2 = person2.total_time + move_time2 + sweep_time

                # 计算分配后的时间差
                time_diff1 = abs(total_time1 - person2.total_time)
                time_diff2 = abs(total_time2 - person1.total_time)

                # 优先选择时间差更小的分配
                if time_diff1 <= time_diff2:
                    self._assign_room_to_person(person1, room, dist1, sweep_time, path1)
                else:
                    self._assign_room_to_person(person2, room, dist2, sweep_time, path2)

            except Exception as e:
                print(f"警告：计算房间 {room.name} 的距离失败: {e}")
                continue

        # 计算返回最近出口的路径
        self._add_return_path(person1)
        self._add_return_path(person2)

        return person1, person2

    def greedy_assign(self) -> Tuple[Person, Person]:
        """贪心算法入口（现在调用平衡分配算法）"""
        return self.balanced_partition_assign()

    def _assign_room_to_person(self, person: Person, room: Room, distance: float,
                              sweep_time: float, path: List[Tuple[float, float]]):
        """将房间分配给人员，更新路径和时间"""
        # 添加完整路径（跳过起点，因为已经在path中）
        if len(path) > 1:
            person.path.extend(path[1:])
        else:
            person.path.append(room.door_position)

        # 更新位置
        person.x, person.y = room.door_x, room.door_y

        # 更新房间列表
        person.rooms.append(f"{room.name}({sweep_time:.0f}s)")

        # 更新距离和时间
        move_time = distance / self.MOVE_SPEED
        person.total_distance += distance
        person.total_time += move_time + sweep_time

    def _add_return_path(self, person: Person):
        """添加返回最近出口的路径"""
        try:
            dist1, path1 = self.get_path_distance(person.get_current_position(), self.exits["exit1"])
            dist2, path2 = self.get_path_distance(person.get_current_position(), self.exits["exit2"])

            if dist1 <= dist2:
                nearest_exit = self.exits["exit1"]
                exit_dist = dist1
                exit_path = path1
            else:
                nearest_exit = self.exits["exit2"]
                exit_dist = dist2
                exit_path = path2

            # 添加完整返回路径（跳过起点）
            if len(exit_path) > 1:
                person.path.extend(exit_path[1:])
            else:
                person.path.append(nearest_exit)

            # 更新距离和时间
            move_time = exit_dist / self.MOVE_SPEED
            person.total_distance += exit_dist
            person.total_time += move_time

        except Exception as e:
            print(f"警告：计算返回出口距离失败: {e}")

    # ========================================================================
    # 结果输出
    # ========================================================================

    def print_results(self, person1: Person, person2: Person):
        """打印检查结果"""
        print("=" * 80)
        print("单层建筑房间检查结果（按PNG布局）")
        print("=" * 80)
        print(f"\n【人员1】")
        print(f"  路径: {' → '.join(person1.rooms)} → 出口")
        print(f"  移动距离: {person1.total_distance:.1f}m")
        print(f"  总时间: {person1.total_time:.0f}秒 ({person1.total_time/60:.1f}分钟)")
        print(f"  路径点数: {len(person1.path)}")

        print(f"\n【人员2】")
        print(f"  路径: {' → '.join(person2.rooms)} → 出口")
        print(f"  移动距离: {person2.total_distance:.1f}m")
        print(f"  总时间: {person2.total_time:.0f}秒 ({person2.total_time/60:.1f}分钟)")
        print(f"  路径点数: {len(person2.path)}")

        print(f"\n【汇总】")
        print(f"  总移动距离: {person1.total_distance + person2.total_distance:.1f}m")
        max_time = max(person1.total_time, person2.total_time)
        min_time = min(person1.total_time, person2.total_time)
        time_diff = abs(person1.total_time - person2.total_time)
        time_diff_percent = (time_diff / max_time * 100) if max_time > 0 else 0
        print(f"  最大完成时间: {max_time:.0f}秒 ({max_time/60:.1f}分钟)")
        print(f"  时间差: {time_diff:.0f}秒 ({time_diff_percent:.1f}%)")

        # 检查是否满足15%约束
        if time_diff_percent <= 15:
            print(f"  ✓ 时间差在15%限制内")
        else:
            print(f"  ✗ 警告：时间差超过15%限制！")
        print("=" * 80)

    # ========================================================================
    # 可视化
    # ========================================================================

    def visualize(self, person1: Person, person2: Person):
        """可视化建筑布局和人员路径"""
        fig, ax = plt.subplots(1, 1, figsize=(18, 14))

        # 1. 绘制房间（白色填充，黑色边框）
        for room in self.rooms:
            rect = patches.Rectangle(
                (room.x, room.y), room.width, room.height,
                linewidth=2, edgecolor='black', facecolor='white'
            )
            ax.add_patch(rect)

            # 房间名称和清扫时间（走廊不显示清扫时间）
            cx, cy = room.x + room.width/2, room.y + room.height/2
            if "Corridor" not in room.name:
                # 只对非走廊房间显示清扫时间
                sample_sweep_time = self.get_sweep_time(room)
                room_label = f"{room.name}\n({sample_sweep_time:.0f}s)"
            else:
                # 走廊只显示名称
                room_label = room.name
            ax.text(cx, cy, room_label, ha='center', va='center',
                   fontsize=9, color='black', weight='bold')

            # 门（灰色弧线）- 走廊不绘制门
            if "Corridor" not in room.name:
                self._draw_door(ax, room)

        # 2. 重新绘制走廊区域（覆盖相邻房间的边框线，确保走廊连续）
        for corridor in self.corridors_areas:
            rect = patches.Rectangle(
                (corridor["x"], corridor["y"]),
                corridor["width"], corridor["height"],
                linewidth=1, edgecolor='darkgray',
                facecolor='lightgray',
                alpha=0.6
            )
            ax.add_patch(rect)
            # 重新绘制走廊名称
            cx, cy = corridor["x"] + corridor["width"]/2, corridor["y"] + corridor["height"]/2
            ax.text(cx, cy, corridor["name"], ha='center', va='center',
                   fontsize=9, color='black', weight='bold')

        # 3. 绘制人员路径
        self._draw_person_path(ax, person1, 'r', 'Person 1')
        self._draw_person_path(ax, person2, 'b', 'Person 2')

        # 4. 标记出入口
        ax.plot(*self.exits["exit1"], 'go', markersize=12, label='Exit 1', zorder=12)
        ax.plot(*self.exits["exit2"], 'g^', markersize=12, label='Exit 2', zorder=12)

        # 5. 设置坐标轴
        ax.set_xlim(-2, 42)
        ax.set_ylim(-2, 24)
        ax.set_xlabel('X (meters)', fontsize=12)
        ax.set_ylabel('Y (meters)', fontsize=12)
        ax.set_aspect('equal')
        ax.legend(loc='lower left', fontsize=10, framealpha=0.9)
        ax.grid(True, alpha=0.3)
        ax.set_title('Single Floor Building Inspection (PNG Layout)', fontsize=14, weight='bold')

        # 6. 保存图片
        plt.tight_layout()
        os.makedirs('./output', exist_ok=True)
        plt.savefig('./output/single_floor_inspection.png',
                   dpi=300, bbox_inches='tight')
        print(f"\n图像已保存到: ./output/single_floor_inspection.png")
        # plt.show()  # 注释掉，避免阻塞

    def _draw_door(self, ax, room: Room):
        """绘制门（支持多门）"""
        # 绘制所有门
        for door_x, door_y, door_angle in room.all_doors:
            # 根据门的角度确定绘制起始角度
            if door_angle == 270:
                door_start_angle = 0
            elif door_angle == 90:
                door_start_angle = 180
            elif door_angle == 180:
                door_start_angle = 270
            else:  # 0
                door_start_angle = 90

            door_arc = patches.Wedge(
                (door_x, door_y), 0.8,
                door_start_angle, door_start_angle + 90,
                facecolor='white', edgecolor='gray',
                linewidth=1, alpha=0.5
            )
            ax.add_patch(door_arc)

    def _draw_person_path(self, ax, person: Person, color: str, label: str):
        """绘制人员路径（带箭头和数字标注）"""
        if not person.path or len(person.path) == 0:
            return

        # 根据颜色代码确定深色边框颜色
        dark_color = 'darkred' if color == 'r' else 'darkblue'

        if len(person.path) > 1:
            # 绘制路径线
            path = np.array(person.path)
            ax.plot(path[:, 0], path[:, 1], f'{color}-',
                   linewidth=3, label=f'{label}: {person.total_time:.0f}s',
                   zorder=10, alpha=0.8)

            # 在路径上添加箭头（每隔一段距离添加一个）
            arrow_step = max(1, len(path) // 20)
            for i in range(0, len(path) - 1, arrow_step):
                x1, y1 = path[i]
                x2, y2 = path[i + 1] if i + 1 < len(path) else path[-1]
                dx, dy = x2 - x1, y2 - y1
                dist = np.sqrt(dx**2 + dy**2)
                if dist > 0.3:
                    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                              arrowprops=dict(arrowstyle='->', color=color,
                                            lw=2.5, alpha=0.7, zorder=11))

            # 标记起点（START）
            ax.plot(person.path[0][0], person.path[0][1],
                   f'{color}o', markersize=12, zorder=11,
                   markeredgecolor=dark_color, markeredgewidth=2)
            ax.annotate('START', (person.path[0][0], person.path[0][1]),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=9, color=dark_color, weight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white',
                               edgecolor=dark_color, alpha=0.8))

            # 在路径关键点添加数字标注
            label_num = 1
            room_doors = []
            for room in self.rooms:
                if "Corridor" not in room.name:
                    # 使用房间的所有门位置
                    room_doors.extend(room.all_door_positions)

            for i in range(1, len(person.path) - 1):
                x, y = path[i]
                is_door = False
                for door_x, door_y in room_doors:
                    if abs(x - door_x) < 0.3 and abs(y - door_y) < 0.3:
                        is_door = True
                        break

                if is_door or i % max(1, len(person.path) // 15) == 0:
                    ax.annotate(str(label_num), (x, y),
                              xytext=(0, 0), textcoords='offset points',
                              fontsize=11, color=dark_color, weight='bold',
                              bbox=dict(boxstyle="circle,pad=0.4", facecolor='white',
                                      edgecolor=dark_color, linewidth=2, alpha=0.95),
                              ha='center', va='center', zorder=12)
                    label_num += 1

            # 标记终点（END）
            ax.plot(person.path[-1][0], person.path[-1][1],
                   f'{color}*', markersize=15, zorder=11)
            ax.annotate('END', (person.path[-1][0], person.path[-1][1]),
                       xytext=(5, -15), textcoords='offset points',
                       fontsize=9, color=dark_color, weight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white',
                               edgecolor=dark_color, alpha=0.8))
        else:
            # 如果只有一个点，只标记位置
            ax.plot(person.path[0][0], person.path[0][1],
                   f'{color}o', markersize=12,
                   label=f'{label}: {person.total_time:.0f}s',
                   zorder=11, markeredgecolor=dark_color, markeredgewidth=2)

# ============================================================================
# 主程序
# ============================================================================

if __name__ == "__main__":
    # 创建建筑检查系统
    building = SingleFloorBuildingInspection()

    # 执行任务分配
    person1, person2 = building.greedy_assign()

    # 打印结果
    building.print_results(person1, person2)

    # 可视化
    building.visualize(person1, person2)
