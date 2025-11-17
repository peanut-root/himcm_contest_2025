import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from dataclasses import dataclass
from typing import List, Tuple
import math

def sweep_time_gt(area, vis, p_halt, clutter, redundancy=False):
    r = 0.05 + 0.30 * vis
    base = area / r * clutter
    comm = 120 * p_halt
    overhead = 15 + 0.5 * (area**0.5) * (clutter - 1)
    t = base + comm + overhead
    if redundancy:
        t *= 1.30
    return t

@dataclass
class Room:
    name: str
    x: float
    y: float
    width: float
    height: float
    door_x: float
    door_y: float
    door_angle: float  # 门的朝向角度
    complexity: float
    
    @property
    def area(self):
        return self.width * self.height

@dataclass
class Person:
    id: int
    x: float
    y: float
    rooms: List[str]
    path: List[Tuple[float, float]]
    total_distance: float = 0.0
    total_time: float = 0.0

class ComplexBuildingInspection:
    def __init__(self):
        # 按参照图精确尺寸（mm→m，÷1000）
        self.rooms = [
            # 上层（y=17-20）
            Room("Storage Room", 0, 17, 10, 3, 5, 17.5, 270, 1.8),
            Room("Restroom Room", 10, 17, 10, 3, 15, 17.5, 270, 1.0),
            Room("Lift", 20, 17, 2, 3, 21, 17.5, 270, 1.0),
            Room("Stairwell", 22, 17, 3, 3, 23.5, 17.5, 270, 1.0),
            Room("Kitchen", 25, 17, 7, 3, 30.5, 17.5, 270, 1.8),
            
            # 中层（y=2-17）
            Room("Hall", 0, 2, 23, 15, 11.5, 8, 0, 1.0),
            Room("Cafeteria", 23, 8, 9, 9, 23.5, 12, 180, 1.5),
            
            # 下层（y=0-2）
            Room("Backstage Equipment Room", 0, 0, 23, 2, 11.5, 2, 90, 1.8),
            Room("Multipurpose Classroom", 23, 0, 4, 8, 23.5, 4, 180, 1.5),
            Room("Office", 27, 0, 5, 8, 27.5, 4, 180, 1.0)
        ]
        
        # ★ 走廊区域定义（参照图中的实际走廊）
        self.corridors_areas = [
            # 上走廊（y=20-21，贯穿全宽）
            {"name": "Upper Corridor", "x": 0, "y": 20, "width": 32, "height": 1},
            # 中部右侧走廊（连接Cafeteria上下）
            {"name": "Right Corridor", "x": 32, "y": 0, "width": 1, "height": 20},
        ]
        
        # 出入口
        self.exit1 = (0, 10)
        self.exit2 = (32, 20.5)
        
        self.exit_doors = [
            {"x": 0, "y": 10, "angle": 180},
            {"x": 32, "y": 20.5, "angle": 0}
        ]
        
        # ★ 关键走廊节点（不穿墙的路径必须通过这些点）
        self.waypoints = [
            # 左侧
            (0, 10),        # Exit1
            (0, 20),        # 左上角
            
            # 上走廊
            (11.5, 20),     # 上走廊中点
            (23, 20),       # 上走廊右端
            
            # 中部
            (23, 12),       # Hall-Cafeteria交界（中层）
            (23, 8),        # Cafeteria-下层交界
            
            # 下层
            (11.5, 2),      # Hall-Backstage交界
            (23, 2),        # 右下走廊
            
            # 右侧
            (32, 0),        # 右下角
            (32, 8),        # 右侧走廊
            (32, 20.5),     # Exit2
        ]
    
    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)
    
    def get_sweep_time(self, room):
        vis = random.uniform(0.0, 0.8)
        p_halt = random.uniform(0.05, 0.3)
        return sweep_time_gt(room.area, vis, p_halt, room.complexity)
    
    def greedy_assign(self):
        person1 = Person(1, self.exit1[0], self.exit1[1], [], [self.exit1])
        person2 = Person(2, self.exit2[0], self.exit2[1], [], [self.exit2])
        unassigned = list(range(len(self.rooms)))
        
        while unassigned:
            best_assignment = None
            best_cost = float('inf')
            
            for idx in unassigned:
                room = self.rooms[idx]
                door = (room.door_x, room.door_y)
                
                try:
                    dist1 = self.get_path_distance((person1.x, person1.y), door)
                    move_time1 = dist1 / 1.5
                    sweep_time1 = self.get_sweep_time(room)
                    total_time1 = person1.total_time + move_time1 + sweep_time1
                    
                    dist2 = self.get_path_distance((person2.x, person2.y), door)
                    move_time2 = dist2 / 1.5
                    sweep_time2 = self.get_sweep_time(room)
                    total_time2 = person2.total_time + move_time2 + sweep_time2
                    
                    # 分配给完成时间更早的人
                    if total_time1 <= total_time2:
                        if total_time1 < best_cost:
                            best_cost = total_time1
                            best_assignment = (1, idx, dist1, sweep_time1)
                    else:
                        if total_time2 < best_cost:
                            best_cost = total_time2
                            best_assignment = (2, idx, dist2, sweep_time2)
                except Exception as e:
                    print(f"警告：计算房间 {room.name} 的距离失败: {e}")
                    continue
            
            # ★ 检查是否找到有效的分配
            if best_assignment is None:
                print("错误：无法找到可行的房间分配")
                break
            
            person_id, room_idx, distance, sweep_time = best_assignment
            room = self.rooms[room_idx]
            
            if person_id == 1:
                person1.path.append((room.door_x, room.door_y))
                person1.x, person1.y = room.door_x, room.door_y
                person1.rooms.append(f"{room.name}({sweep_time:.0f}s)")
                person1.total_distance += distance
                person1.total_time += distance / 1.5 + sweep_time
            else:
                person2.path.append((room.door_x, room.door_y))
                person2.x, person2.y = room.door_x, room.door_y
                person2.rooms.append(f"{room.name}({sweep_time:.0f}s)")
                person2.total_distance += distance
                person2.total_time += distance / 1.5 + sweep_time
            
            unassigned.remove(room_idx)
        
        # 返回最近出口
        for person in [person1, person2]:
            try:
                dist1 = self.get_path_distance((person.x, person.y), self.exit1)
                dist2 = self.get_path_distance((person.x, person.y), self.exit2)
                nearest_exit = self.exit1 if dist1 <= dist2 else self.exit2
                exit_dist = dist1 if nearest_exit == self.exit1 else dist2
                
                person.path.append(nearest_exit)
                person.total_distance += exit_dist
                person.total_time += exit_dist / 1.5
            except Exception as e:
                print(f"警告：计算返回出口距离失败: {e}")
        
        return person1, person2
    
    def visualize(self, person1, person2):
        fig, ax = plt.subplots(1, 1, figsize=(18, 12))
        
        # 绘制走廊区域（浅灰色）
        for corridor in self.corridors_areas:
            rect = patches.Rectangle(
                (corridor["x"], corridor["y"]), 
                corridor["width"], corridor["height"],
                linewidth=1, edgecolor='gray', 
                facecolor='white', 
                alpha=0.2, linestyle='--'
            )
            ax.add_patch(rect)
        
        # 绘制房间（白色填充，黑色边框）
        for room in self.rooms:
            rect = patches.Rectangle(
                (room.x, room.y), room.width, room.height,
                linewidth=2, edgecolor='black', facecolor='white'
            )
            ax.add_patch(rect)
            
            # 房间名称和清扫时间（黑字）
            cx, cy = room.x + room.width/2, room.y + room.height/2
            sample_sweep_time = self.get_sweep_time(room)
            room_label = f"{room.name}\n({sample_sweep_time:.0f}s)"
            ax.text(cx, cy, room_label, ha='center', va='center', fontsize=9, color='black')
            
            # 门（灰色弧线）
            if room.door_angle == 270:
                door_start_angle = 0
            elif room.door_angle == 90:
                door_start_angle = 180
            elif room.door_angle == 180:
                door_start_angle = 270
            else:
                door_start_angle = 90
                
            door_arc = patches.Wedge((room.door_x, room.door_y), 0.8, 
                                   door_start_angle, door_start_angle + 90,
                                   facecolor='white', edgecolor='gray', linewidth=1, alpha=0.5)
            ax.add_patch(door_arc)
        
        # 绘制人员路径（红/蓝线条）
        if person1.path:
            path = np.array(person1.path)
            ax.plot(path[:, 0], path[:, 1], 'r-', linewidth=2, label=f'Person 1: {person1.total_time:.0f}s')
            ax.plot(person1.x, person1.y, 'ro', markersize=8)
        
        if person2.path:
            path = np.array(person2.path)
            ax.plot(path[:, 0], path[:, 1], 'b-', linewidth=2, label=f'Person 2: {person2.total_time:.0f}s')
            ax.plot(person2.x, person2.y, 'bs', markersize=8)
        
        # 标记出入口
        ax.plot(*self.exit1, 'go', markersize=10, label='Exit 1')
        ax.plot(*self.exit2, 'g^', markersize=10, label='Exit 2')
        
        ax.set_xlim(-3, 35)
        ax.set_ylim(-3, 22)
        ax.set_xlabel('X (meters)', fontsize=12)
        ax.set_ylabel('Y (meters)', fontsize=12)
        ax.set_aspect('equal')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # 调整布局以显示完整图例
        plt.subplots_adjust(right=0.75)
        plt.savefig('./output/complex_single_level_building_inspection.png', 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.show()
    
    def print_results(self, person1, person2):
        print("=" * 80)
        print("复杂单层建筑房间检查结果")
        print("=" * 80)
        print(f"人员1路径: {' → '.join(person1.rooms)} → 出口")
        print(f"  距离: {person1.total_distance:.1f}m, 时间: {person1.total_time:.0f}s ({person1.total_time/60:.1f}分钟)")
        print(f"人员2路径: {' → '.join(person2.rooms)} → 出口")
        print(f"  距离: {person2.total_distance:.1f}m, 时间: {person2.total_time:.0f}s ({person2.total_time/60:.1f}分钟)")
        print(f"总距离: {person1.total_distance + person2.total_distance:.1f}m")
        print(f"最大完成时间: {max(person1.total_time, person2.total_time):.0f}s ({max(person1.total_time, person2.total_time)/60:.1f}分钟)")
        print("=" * 80)
    
    def _line_intersects_room(self, x1, y1, x2, y2, room):
        """检查线段是否与房间相交"""
        room_left, room_right = room.x, room.x + room.width
        room_bottom, room_top = room.y, room.y + room.height
        
        p1_inside = room_left <= x1 <= room_right and room_bottom <= y1 <= room_top
        p2_inside = room_left <= x2 <= room_right and room_bottom <= y2 <= room_top
        
        if p1_inside != p2_inside:
            return True
        
        if not p1_inside and not p2_inside:
            if (x1 < room_left and x2 < room_left) or \
               (x1 > room_right and x2 > room_right) or \
               (y1 < room_bottom and y2 < room_bottom) or \
               (y1 > room_top and y2 > room_top):
                return False
            return True
        
        return False
    
    def get_path_distance(self, start, end):
        """使用Dijkstra算法找最短路径，不穿墙"""
        import heapq
        
        nodes = list(self.waypoints)
        
        for room in self.rooms:
            nodes.append((room.door_x, room.door_y))
        
        nodes.append(start)
        nodes.append(end)
        
        def can_move_directly(p1, p2):
            """检查两点间是否能直线移动"""
            x1, y1 = p1
            x2, y2 = p2
            
            for room in self.rooms:
                if self._line_intersects_room(x1, y1, x2, y2, room):
                    return False
            
            return True
        
        distances = {node: float('inf') for node in nodes}
        distances[start] = 0
        pq = [(0, start)]
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current == end:
                return current_dist
            
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
                        heapq.heappush(pq, (new_dist, next_node))
        
        return distances[end]

if __name__ == "__main__":
    building = ComplexBuildingInspection()
    p1, p2 = building.greedy_assign()
    building.print_results(p1, p2)
    building.visualize(p1, p2)