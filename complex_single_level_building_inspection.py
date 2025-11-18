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
    
    @property
    def area(self):
        """房间面积"""
        return self.width * self.height
    
    @property
    def door_position(self):
        """门的位置"""
        return (self.door_x, self.door_y)

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

class ComplexBuildingInspection:
    """复杂单层建筑检查系统"""
    
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
    # 建筑布局定义
    # ========================================================================
    
    def _create_rooms(self) -> List[Room]:
        """创建所有房间"""
        rooms = []
        
        # 走廊（用于路径规划，不参与分配）
        rooms.extend([
            Room("Upper Corridor", 0, 18, 35, 2, 17.5, 19, 0, 1.0),  # 宽度35m，延伸到Kitchen下方
            Room("Vertical Corridor", 23, 0, 2, 20, 24, 10, 0, 1.0),  # 从y=0到y=20，高度20m
            Room("Middle Corridor", 25, 10, 16, 2, 33, 11, 0, 1.0),  # (25,10) to (41,12)，高度2m
        ])
        
        # 顶部房间（从左到右，y=20-23）
        rooms.extend([
            Room("Storage Room", 0, 20, 10, 3, 5, 20, 270, 1.8),
            Room("Restroom Room", 10, 20, 10, 3, 15, 20, 270, 1.0),
            Room("Lift", 20, 20, 2, 3, 21, 20, 270, 1.0),
            Room("Stairwell", 22, 20, 3, 3, 23.5, 20, 270, 1.0),
            Room("Kitchen", 25, 20, 10, 3, 30, 20, 270, 1.8),  # 与其他顶部房间同一水平线
        ])
        
        # 中间房间
        rooms.extend([
            Room("Hall", 0, 3, 23, 15, 0, 10.5, 180, 1.0),  # Hall有两个门：左侧(0,10.5)和顶部(11.5,18)
            Room("Cafeteria", 25, 12, 7, 8, 25, 16, 180, 1.5),  # (25,12) to (32,20)
        ])
        
        # 底部房间
        rooms.extend([
            Room("Backstage Equipment Room", 0, 0, 23, 3, 11.5, 3, 90, 1.8),  # (0,0) to (23,3)
            Room("Multipurpose Classroom", 25, 0, 8, 10, 25, 5, 180, 1.5),  # (25,0) to (33,10)
            Room("Office", 33, 0, 8, 10, 33, 5, 180, 1.0),  # (33,0) to (41,10)
        ])
        
        return rooms
    
    def _create_corridors(self) -> List[dict]:
        """创建走廊区域定义"""
        return [
            {"name": "Upper Corridor", "x": 0, "y": 18, "width": 35, "height": 2},  # 延伸到Kitchen下方
            {"name": "Vertical Corridor", "x": 23, "y": 0, "width": 2, "height": 20},  # 从底部到顶部
            {"name": "Middle Corridor", "x": 25, "y": 10, "width": 16, "height": 2},  # 在Multipurpose/Office上方
        ]
    
    def _create_exits(self) -> dict:
        """创建出入口"""
        return {
            "exit1": (0.5, 10.5),  # Hall左侧门（Left Corridor中心）
            "exit2": (35.5, 19),   # 上走廊右端（Upper Corridor右端）
        }
    
    def _create_waypoints(self) -> List[Tuple[float, float]]:
        """创建关键路径节点"""
        return [
            # Hall左侧（Left Corridor）
            (0.5, 3), (0.5, 10.5), (0.5, 18), (0.5, 20),
            # 上走廊（Upper Corridor）
            (5, 19), (15, 19), (21, 19), (23.5, 19), (30, 19), (35, 19), (35.5, 19),
            # Vertical Corridor
            (24, 0), (24, 3), (24, 10), (24, 18), (24, 20),
            # Middle Corridor
            (25, 11), (29, 11), (33, 11), (41, 11),
            # Hall边界和门
            (23, 3), (23, 10.5), (23, 18),
            (0, 10.5),  # Hall左门
            (11.5, 18),  # Hall上部门（顶部中间）
            # 房间门
            (25, 16),  # Cafeteria门
            (25, 5),   # Multipurpose Classroom门
            (33, 5),   # Office门
            # Backstage门
            (11.5, 3),
        ]
    
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
        """检查点是否在门附近"""
        # Hall有两个门，需要特殊处理
        if room.name == "Hall":
            # Hall左门 (0, 10.5)
            if abs(x - 0) < tolerance and abs(y - 10.5) < tolerance:
                return True
            # Hall上部门 (11.5, 18)
            if abs(x - 11.5) < tolerance and abs(y - 18) < tolerance:
                return True
            return False
        
        # 其他房间的门
        door_x, door_y = room.door_x, room.door_y
        return abs(x - door_x) < tolerance and abs(y - door_y) < tolerance
    
    def _line_intersects_room_strict(self, x1: float, y1: float, x2: float, y2: float, room: Room) -> bool:
        """严格检查线段是否穿过房间（不允许穿墙）"""
        room_left, room_right = room.x, room.x + room.width
        room_bottom, room_top = room.y, room.y + room.height
        
        # 检查两个端点是否在房间内
        p1_inside = room_left < x1 < room_right and room_bottom < y1 < room_top
        p2_inside = room_left < x2 < room_right and room_bottom < y2 < room_top
        
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
            
            # 检查是否与房间边界相交（排除门）
            door_width = 1.2  # 门的宽度（米）
            
            def line_intersects_segment(px1, py1, px2, py2, qx1, qy1, qx2, qy2):
                """检查两条线段是否相交"""
                def ccw(A, B, C):
                    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
                A, B = (px1, py1), (px2, py2)
                C, D = (qx1, qy1), (qx2, qy2)
                return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)
            
            # Hall有两个门，需要特殊处理
            if room.name == "Hall":
                hall_doors = [(0, 10.5, 180), (11.5, 18, 90)]  # (x, y, angle)
                
                # 检查与左边界相交（排除Hall左门）
                if line_intersects_segment(x1, y1, x2, y2, room_left, room_bottom, room_left, room_top):
                    # 检查是否通过Hall左门
                    door_y = 10.5
                    door_y_min = door_y - door_width/2
                    door_y_max = door_y + door_width/2
                    if not (door_y_min <= min(y1, y2) <= door_y_max and door_y_min <= max(y1, y2) <= door_y_max):
                        return True
                
                # 检查与顶边界相交（排除Hall上部门）
                if line_intersects_segment(x1, y1, x2, y2, room_left, room_top, room_right, room_top):
                    # 检查是否通过Hall上部门
                    door_x = 11.5
                    door_x_min = door_x - door_width/2
                    door_x_max = door_x + door_width/2
                    if not (door_x_min <= min(x1, x2) <= door_x_max and door_x_min <= max(x1, x2) <= door_x_max):
                        return True
                
                # 检查与右边界和底边界（Hall没有门在这些边界上）
                if line_intersects_segment(x1, y1, x2, y2, room_right, room_bottom, room_right, room_top):
                    return True
                if line_intersects_segment(x1, y1, x2, y2, room_left, room_bottom, room_right, room_bottom):
                    return True
            else:
                # 其他房间只有一个门
                door_x, door_y = room.door_x, room.door_y
                
                # 检查与左边界相交（排除门）
                if room.door_angle == 180:  # 门在左侧
                    door_y_min = door_y - door_width/2
                    door_y_max = door_y + door_width/2
                    if not (door_y_min <= min(y1, y2) <= door_y_max and door_y_min <= max(y1, y2) <= door_y_max):
                        if line_intersects_segment(x1, y1, x2, y2, room_left, room_bottom, room_left, room_top):
                            return True
                else:
                    if line_intersects_segment(x1, y1, x2, y2, room_left, room_bottom, room_left, room_top):
                        return True
                
                # 检查与右边界相交（排除门）
                if room.door_angle == 0:  # 门在右侧
                    door_y_min = door_y - door_width/2
                    door_y_max = door_y + door_width/2
                    if not (door_y_min <= min(y1, y2) <= door_y_max and door_y_min <= max(y1, y2) <= door_y_max):
                        if line_intersects_segment(x1, y1, x2, y2, room_right, room_bottom, room_right, room_top):
                            return True
                else:
                    if line_intersects_segment(x1, y1, x2, y2, room_right, room_bottom, room_right, room_top):
                        return True
                
                # 检查与底边界相交（排除门）
                if room.door_angle == 270:  # 门在底部
                    door_x_min = door_x - door_width/2
                    door_x_max = door_x + door_width/2
                    if not (door_x_min <= min(x1, x2) <= door_x_max and door_x_min <= max(x1, x2) <= door_x_max):
                        if line_intersects_segment(x1, y1, x2, y2, room_left, room_bottom, room_right, room_bottom):
                            return True
                else:
                    if line_intersects_segment(x1, y1, x2, y2, room_left, room_bottom, room_right, room_bottom):
                        return True
                
                # 检查与顶边界相交（排除门）
                if room.door_angle == 90:  # 门在顶部
                    door_x_min = door_x - door_width/2
                    door_x_max = door_x + door_width/2
                    if not (door_x_min <= min(x1, x2) <= door_x_max and door_x_min <= max(x1, x2) <= door_x_max):
                        if line_intersects_segment(x1, y1, x2, y2, room_left, room_top, room_right, room_top):
                            return True
                else:
                    if line_intersects_segment(x1, y1, x2, y2, room_left, room_top, room_right, room_top):
                        return True
        
        # 如果只有一个端点在房间内，必须通过门
        elif p1_inside != p2_inside:
            door_tolerance = 0.6
            
            # Hall有两个门，需要特殊处理
            if room.name == "Hall":
                hall_doors = [(0, 10.5), (11.5, 18)]  # Hall的两个门
                if p1_inside:
                    # p1在房间内，p2必须在任一门附近
                    near_any_door = any(abs(x2 - dx) < door_tolerance and abs(y2 - dy) < door_tolerance 
                                      for dx, dy in hall_doors)
                    if not near_any_door:
                        return True  # 没有通过门，不允许
                else:
                    # p2在房间内，p1必须在任一门附近
                    near_any_door = any(abs(x1 - dx) < door_tolerance and abs(y1 - dy) < door_tolerance 
                                      for dx, dy in hall_doors)
                    if not near_any_door:
                        return True  # 没有通过门，不允许
            else:
                # 其他房间只有一个门
                door_x, door_y = room.door_x, room.door_y
                if p1_inside:
                    # p1在房间内，p2必须在门附近
                    if not (abs(x2 - door_x) < door_tolerance and abs(y2 - door_y) < door_tolerance):
                        return True  # 没有通过门，不允许
                else:
                    # p2在房间内，p1必须在门附近
                    if not (abs(x1 - door_x) < door_tolerance and abs(y1 - door_y) < door_tolerance):
                        return True  # 没有通过门，不允许
        
        return False
    
    def _line_intersects_room(self, x1: float, y1: float, x2: float, y2: float, room: Room) -> bool:
        """检查线段是否与房间相交（严格检查，不允许穿墙）"""
        room_left, room_right = room.x, room.x + room.width
        room_bottom, room_top = room.y, room.y + room.height
        
        # 检查两个端点是否在房间内
        p1_inside = room_left < x1 < room_right and room_bottom < y1 < room_top
        p2_inside = room_left < x2 < room_right and room_bottom < y2 < room_top
        
        # 如果两个端点都在房间内，允许（这是进入房间的情况）
        if p1_inside and p2_inside:
            return False  # 在房间内移动，允许
        
        # 如果两个端点都不在房间内，检查是否穿过房间
        if not p1_inside and not p2_inside:
            # 检查是否通过门（允许通过门）
            door_tolerance = 0.3  # 门的容差范围（米）
            door_x, door_y = room.door_x, room.door_y
            
            # 检查起点或终点是否在门附近
            p1_near_door = abs(x1 - door_x) < door_tolerance and abs(y1 - door_y) < door_tolerance
            p2_near_door = abs(x2 - door_x) < door_tolerance and abs(y2 - door_y) < door_tolerance
            
            # 如果路径通过门，允许
            if p1_near_door or p2_near_door:
                return False  # 通过门，允许
            
            # 检查线段是否完全在房间的同一侧（不相交）
            if (x1 <= room_left and x2 <= room_left) or \
               (x1 >= room_right and x2 >= room_right) or \
               (y1 <= room_bottom and y2 <= room_bottom) or \
               (y1 >= room_top and y2 >= room_top):
                return False  # 不相交
            
            # 检查线段是否与矩形边界相交
            def line_intersects_segment(px1, py1, px2, py2, qx1, qy1, qx2, qy2):
                """检查两条线段是否相交"""
                def ccw(A, B, C):
                    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
                
                A, B = (px1, py1), (px2, py2)
                C, D = (qx1, qy1), (qx2, qy2)
                return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)
            
            # 检查与四条边是否相交（排除门的位置）
            door_width = 1.0  # 门的宽度（米）
            
            # 检查与左边界相交（排除门）
            if room.door_angle == 180:  # 门在左侧
                if not (abs(door_y - min(y1, y2)) < door_width/2 and abs(door_y - max(y1, y2)) < door_width/2):
                    if line_intersects_segment(x1, y1, x2, y2, room_left, room_bottom, room_left, room_top):
                        return True
            else:
                if line_intersects_segment(x1, y1, x2, y2, room_left, room_bottom, room_left, room_top):
                    return True
            
            # 检查与右边界相交（排除门）
            if room.door_angle == 0:  # 门在右侧
                if not (abs(door_y - min(y1, y2)) < door_width/2 and abs(door_y - max(y1, y2)) < door_width/2):
                    if line_intersects_segment(x1, y1, x2, y2, room_right, room_bottom, room_right, room_top):
                        return True
            else:
                if line_intersects_segment(x1, y1, x2, y2, room_right, room_bottom, room_right, room_top):
                    return True
            
            # 检查与底边界相交（排除门）
            if room.door_angle == 270:  # 门在底部
                if not (abs(door_x - min(x1, x2)) < door_width/2 and abs(door_x - max(x1, x2)) < door_width/2):
                    if line_intersects_segment(x1, y1, x2, y2, room_left, room_bottom, room_right, room_bottom):
                        return True
            else:
                if line_intersects_segment(x1, y1, x2, y2, room_left, room_bottom, room_right, room_bottom):
                    return True
            
            # 检查与顶边界相交（排除门）
            if room.door_angle == 90:  # 门在顶部
                if not (abs(door_x - min(x1, x2)) < door_width/2 and abs(door_x - max(x1, x2)) < door_width/2):
                    if line_intersects_segment(x1, y1, x2, y2, room_left, room_top, room_right, room_top):
                        return True
            else:
                if line_intersects_segment(x1, y1, x2, y2, room_left, room_top, room_right, room_top):
                    return True
        
        # 如果只有一个端点在房间内，需要检查是否通过门
        elif p1_inside != p2_inside:
            # 如果进入房间，必须通过门
            door_tolerance = 0.5
            door_x, door_y = room.door_x, room.door_y
            
            # 检查不在房间内的点是否在门附近
            if p1_inside:
                p2_near_door = abs(x2 - door_x) < door_tolerance and abs(y2 - door_y) < door_tolerance
                if not p2_near_door:
                    return True  # 没有通过门，不允许
            else:
                p1_near_door = abs(x1 - door_x) < door_tolerance and abs(y1 - door_y) < door_tolerance
                if not p1_near_door:
                    return True  # 没有通过门，不允许
        
        return False
    
    def get_path_distance(self, start: Tuple[float, float], end: Tuple[float, float]) -> Tuple[float, List[Tuple[float, float]]]:
        """使用A*算法计算最短路径"""
        # 构建节点列表
        nodes = list(self.waypoints)
        for room in self.rooms:
            nodes.append(room.door_position)
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
            
            # 如果都不满足，检查是否穿过任何房间
            for room in self.rooms:
                if "Corridor" not in room.name:
                    if self._line_intersects_room_strict(x1, y1, x2, y2, room):
                        return False
            
            return True
        
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
    
    def greedy_assign(self) -> Tuple[Person, Person]:
        """贪心算法分配房间给两个人"""
        # 初始化两个人
        person1 = Person(1, self.exits["exit1"][0], self.exits["exit1"][1], [], [self.exits["exit1"]])
        person2 = Person(2, self.exits["exit2"][0], self.exits["exit2"][1], [], [self.exits["exit2"]])
        
        # 获取需要分配的实际房间
        unassigned = [i for i, room in enumerate(self.rooms) if "Corridor" not in room.name]
        
        # 贪心分配
        while unassigned:
            best_assignment = None
            best_cost = float('inf')
            
            # 对每个未分配的房间，计算分配给谁更优
            for idx in unassigned:
                room = self.rooms[idx]
                door = room.door_position
                
                try:
                    # 计算person1的代价
                    dist1, path1 = self.get_path_distance(person1.get_current_position(), door)
                    move_time1 = dist1 / self.MOVE_SPEED
                    sweep_time1 = self.get_sweep_time(room)


                    total_time1 = person1.total_time + move_time1 + sweep_time1
                
                    # 计算person2的代价
                    dist2, path2 = self.get_path_distance(person2.get_current_position(), door)
                    move_time2 = dist2 / self.MOVE_SPEED
                    sweep_time2 = self.get_sweep_time(room)
                    total_time2 = person2.total_time + move_time2 + sweep_time2
                
                    # 平衡策略：选择使得两个人完成时间更接近的分配
                    # 计算时间差
                    time_diff1 = abs(total_time1 - person2.total_time)  # person1做这个任务后的时间差
                    time_diff2 = abs(total_time2 - person1.total_time)  # person2做这个任务后的时间差
                    
                    # 同时考虑最大完成时间和时间差
                    max_time1 = max(total_time1, person2.total_time)
                    max_time2 = max(total_time2, person1.total_time)
                    
                    # 选择使得最大完成时间最小，如果相同则选择时间差更小的
                    if max_time1 < max_time2:
                        cost = max_time1 + 0.1 * time_diff1  # 稍微惩罚时间差
                        if cost < best_cost:
                            best_cost = cost
                            best_assignment = (1, idx, dist1, sweep_time1, path1)
                    elif max_time2 < max_time1:
                        cost = max_time2 + 0.1 * time_diff2
                        if cost < best_cost:
                            best_cost = cost
                            best_assignment = (2, idx, dist2, sweep_time2, path2)
                    else:
                        # 最大时间相同，选择时间差更小的
                        if time_diff1 < time_diff2:
                            cost = max_time1 + 0.1 * time_diff1
                            if cost < best_cost:
                                best_cost = cost
                                best_assignment = (1, idx, dist1, sweep_time1, path1)
                        else:
                            cost = max_time2 + 0.1 * time_diff2
                            if cost < best_cost:
                                best_cost = cost
                                best_assignment = (2, idx, dist2, sweep_time2, path2)
                            
                except Exception as e:
                    print(f"警告：计算房间 {room.name} 的距离失败: {e}")
                    continue
            
            # 检查是否找到有效分配
            if best_assignment is None:
                print("错误：无法找到可行的房间分配")
                break
            
            # 执行分配
            person_id, room_idx, distance, sweep_time, path = best_assignment
            room = self.rooms[room_idx]
            
            if person_id == 1:
                self._assign_room_to_person(person1, room, distance, sweep_time, path)
            else:
                self._assign_room_to_person(person2, room, distance, sweep_time, path)
            
            unassigned.remove(room_idx)
        
        # 计算返回最近出口的路径
        self._add_return_path(person1)
        self._add_return_path(person2)
        
        return person1, person2
    
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
        print("复杂单层建筑房间检查结果")
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
        print(f"  最大完成时间: {max_time:.0f}秒 ({max_time/60:.1f}分钟)")
        print("=" * 80)
    
    # ========================================================================
    # 可视化
    # ========================================================================
    
    def visualize(self, person1: Person, person2: Person):
        """可视化建筑布局和人员路径"""
        fig, ax = plt.subplots(1, 1, figsize=(18, 14))
        
        # 1. 绘制走廊区域（灰色填充）
        for corridor in self.corridors_areas:
            rect = patches.Rectangle(
                (corridor["x"], corridor["y"]), 
                corridor["width"], corridor["height"],
                linewidth=1, edgecolor='darkgray', 
                facecolor='lightgray', 
                alpha=0.6
            )
            ax.add_patch(rect)
        
        # 2. 绘制房间（白色填充，黑色边框）
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
            
            # 门（灰色弧线）
            self._draw_door(ax, room)
        
        # 3. 绘制人员路径
        self._draw_person_path(ax, person1, 'r', 'Person 1')
        self._draw_person_path(ax, person2, 'b', 'Person 2')
        
        # 4. 标记出入口
        ax.plot(*self.exits["exit1"], 'go', markersize=12, label='Exit 1', zorder=12)
        ax.plot(*self.exits["exit2"], 'g^', markersize=12, label='Exit 2', zorder=12)
        
        # 5. 设置坐标轴
        ax.set_xlim(-2, 38)
        ax.set_ylim(-2, 24)
        ax.set_xlabel('X (meters)', fontsize=12)
        ax.set_ylabel('Y (meters)', fontsize=12)
        ax.set_aspect('equal')
        # 将图例放在左下角，避免遮挡房间标签
        ax.legend(loc='lower left', fontsize=10, framealpha=0.9)
        ax.grid(True, alpha=0.3)
        ax.set_title('Building Inspection Paths', fontsize=14, weight='bold')
        
        # 6. 保存图片（不需要调整布局，因为图例在左下角）
        plt.tight_layout()
        os.makedirs('./output', exist_ok=True)
        plt.savefig('./output/complex_single_level_building_inspection.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def _draw_door(self, ax, room: Room):
        """绘制门"""
        # Hall有两个门，需要特殊处理
        if room.name == "Hall":
            # Hall左门
            door_arc1 = patches.Wedge(
                (0, 10.5), 0.8, 
                270, 360,
                facecolor='white', edgecolor='gray', 
                linewidth=1, alpha=0.5
            )
            ax.add_patch(door_arc1)
            # Hall上部门（顶部中间）
            door_arc2 = patches.Wedge(
                (11.5, 18), 0.8, 
                180, 270,
                facecolor='white', edgecolor='gray', 
                linewidth=1, alpha=0.5
            )
            ax.add_patch(door_arc2)
            return
        
        # 其他房间的门
        if room.door_angle == 270:
            door_start_angle = 0
        elif room.door_angle == 90:
            door_start_angle = 180
        elif room.door_angle == 180:
            door_start_angle = 270
        else:
            door_start_angle = 90
        
        door_arc = patches.Wedge(
            (room.door_x, room.door_y), 0.8, 
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
            arrow_step = max(1, len(path) // 20)  # 每隔几个点添加一个箭头，避免太密集
            for i in range(0, len(path) - 1, arrow_step):
                x1, y1 = path[i]
                x2, y2 = path[i + 1] if i + 1 < len(path) else path[-1]
                dx, dy = x2 - x1, y2 - y1
                dist = np.sqrt(dx**2 + dy**2)
                if dist > 0.3:  # 只在距离足够时添加箭头
                    # 在路径上添加箭头
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
            
            # 在路径关键点添加数字标注（1,2,3,4,5,6...）
            # 标注每个路径点（跳过起点和终点）
            label_num = 1
            # 找到房间门的位置进行标注
            room_doors = []
            for room in self.rooms:
                if "Corridor" not in room.name:
                    if room.name == "Hall":
                        # Hall有两个门
                        room_doors.append((0, 10.5))
                        room_doors.append((11.5, 18))
                    else:
                        room_doors.append((room.door_x, room.door_y))
            
            # 在路径上标注数字（标注房间门的位置）
            for i in range(1, len(person.path) - 1):
                x, y = path[i]
                # 检查是否是房间门的位置
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
    building = ComplexBuildingInspection()
    
    # 执行任务分配
    person1, person2 = building.greedy_assign()
    
    # 打印结果
    building.print_results(person1, person2)
    
    # 可视化
    building.visualize(person1, person2)
