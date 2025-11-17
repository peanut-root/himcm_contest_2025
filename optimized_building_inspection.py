import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from dataclasses import dataclass
from typing import List, Tuple
import math
from itertools import permutations

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
    door_angle: float
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

class OptimizedBuildingInspection:
    def __init__(self):
        # 房间定义（按USAR标准设置复杂度）
        self.rooms = [
            Room("Storage Room", 0, 17, 10, 3, 5, 17, 270, 1.8),
            Room("Restroom Room", 10, 17, 10, 3, 15, 17, 270, 1.0),
            Room("Lift", 20, 17, 2, 3, 21, 17, 270, 1.0),
            Room("Stairwell", 22, 17, 3, 3, 23.5, 17, 270, 1.0),
            Room("Kitchen", 25, 17, 10, 3, 30, 17, 270, 1.8),
            Room("Hall", 0, 8, 23, 8, 11.5, 8, 90, 1.0),
            Room("Cafeteria", 25, 8, 10, 8, 25, 12, 180, 1.5),
            Room("Backstage Equipment Room", 0, 0, 23, 3, 11.5, 3, 90, 1.8),
            Room("Multipurpose Classroom", 25, 0, 8, 6, 25, 3, 180, 1.5),
            Room("Office", 33, 0, 8, 6, 33, 3, 180, 1.0)
        ]
        
        self.corridors_areas = [
            {"name": "Upper Corridor", "x": 0, "y": 16, "width": 35, "height": 1}
        ]
        
        self.exit1 = (0, 10)
        self.exit2 = (35, 16.5)
        
        self.exit_doors = [
            {"x": 0, "y": 10, "angle": 0},
            {"x": 35, "y": 16.5, "angle": 0}
        ]
    
    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)
    
    def get_corridor_path_distance(self, start, end):
        """计算通过走廊的实际距离（不能穿墙）"""
        # 主要走廊节点
        corridors = [
            (0, 10),      # Exit1附近
            (11.5, 8),    # Hall入口
            (11.5, 3),    # 下走廊中心
            (17.5, 16.5), # 上走廊中心
            (25, 12),     # 右侧走廊
            (25, 3),      # 右下走廊
            (35, 16.5)    # Exit2附近
        ]
        
        # 找到最近的走廊节点
        min_total_dist = float('inf')
        
        for corridor in corridors:
            # 起点到走廊 + 走廊到终点
            dist1 = self.distance(start[0], start[1], corridor[0], corridor[1])
            dist2 = self.distance(corridor[0], corridor[1], end[0], end[1])
            total_dist = dist1 + dist2
            
            if total_dist < min_total_dist:
                min_total_dist = total_dist
        
        # 与直线距离比较，取较大值（考虑墙壁阻挡）
        direct_dist = self.distance(start[0], start[1], end[0], end[1])
        return max(direct_dist * 1.2, min_total_dist)  # 加戁20%的绕行成本
    
    def get_sweep_time(self, room):
        vis = np.random.uniform(0.0, 0.8)
        p_halt = np.random.uniform(0.05, 0.3)
        return sweep_time_gt(room.area, vis, p_halt, room.complexity)
    
    def calculate_tour_cost(self, start_pos, room_indices, exit_pos):
        """计算一个完整巡检路径的总成本"""
        total_distance = 0
        total_time = 0
        current_pos = start_pos
        
        for idx in room_indices:
            room = self.rooms[idx]
            door_pos = (room.door_x, room.door_y)
            
            # 移动距离和时间（不能穿墙）
            move_dist = self.get_corridor_path_distance(current_pos, door_pos)
            move_time = move_dist / 1.5
            
            # 检查时间
            sweep_time = self.get_sweep_time(room)
            
            total_distance += move_dist
            total_time += move_time + sweep_time
            current_pos = door_pos
        
        # 返回出口
        exit_dist = self.distance(current_pos[0], current_pos[1], exit_pos[0], exit_pos[1])
        total_distance += exit_dist
        total_time += exit_dist / 1.5
        
        return total_distance, total_time
    
    def find_optimal_assignment(self):
        """找到最优的房间分配方案"""
        n_rooms = len(self.rooms)
        best_assignment = None
        best_max_time = float('inf')
        
        # 尝试不同的房间分配组合
        for split_point in range(1, n_rooms):
            for room_perm in permutations(range(n_rooms)):
                # 分配房间给两个人
                rooms1 = list(room_perm[:split_point])
                rooms2 = list(room_perm[split_point:])
                
                # 计算每个人的最优路径
                dist1, time1 = self.calculate_tour_cost(self.exit1, rooms1, self.exit1)
                dist2, time2 = self.calculate_tour_cost(self.exit2, rooms2, self.exit2)
                
                max_time = max(time1, time2)
                
                if max_time < best_max_time:
                    best_max_time = max_time
                    best_assignment = (rooms1, rooms2, dist1, time1, dist2, time2)
                
                # 限制搜索空间，避免过长计算
                if len(list(permutations(range(n_rooms)))) > 1000:
                    break
            if len(list(permutations(range(n_rooms)))) > 1000:
                break
        
        return best_assignment
    
    def execute_assignment(self, assignment):
        """执行最优分配方案"""
        rooms1, rooms2, dist1, time1, dist2, time2 = assignment
        
        # 创建人员对象
        person1 = Person(1, self.exit1[0], self.exit1[1], [], [self.exit1])
        person2 = Person(2, self.exit2[0], self.exit2[1], [], [self.exit2])
        
        # 执行person1的路径
        current_pos = self.exit1
        for room_idx in rooms1:
            room = self.rooms[room_idx]
            door_pos = (room.door_x, room.door_y)
            person1.path.append(door_pos)
            person1.rooms.append(f"{room.name}({self.get_sweep_time(room):.0f}s)")
            current_pos = door_pos
        person1.path.append(self.exit1)
        person1.total_distance = dist1
        person1.total_time = time1
        
        # 执行person2的路径
        current_pos = self.exit2
        for room_idx in rooms2:
            room = self.rooms[room_idx]
            door_pos = (room.door_x, room.door_y)
            person2.path.append(door_pos)
            person2.rooms.append(f"{room.name}({self.get_sweep_time(room):.0f}s)")
            current_pos = door_pos
        person2.path.append(self.exit2)
        person2.total_distance = dist2
        person2.total_time = time2
        
        return person1, person2
    
    def optimize_assignment(self):
        """优化分配 - 真正的最近邻居算法"""
        person1 = Person(1, self.exit1[0], self.exit1[1], [], [self.exit1])
        person2 = Person(2, self.exit2[0], self.exit2[1], [], [self.exit2])
        unassigned = list(range(len(self.rooms)))
        
        print(f"Person1 起点: {self.exit1}, Person2 起点: {self.exit2}")
        
        while unassigned:
            min_dist1 = min_dist2 = float('inf')
            best_room1 = best_room2 = -1
            
            # 为每个人找最近的房间
            for room_idx in unassigned:
                room = self.rooms[room_idx]
                door_pos = (room.door_x, room.door_y)
                
                # Person1到该房间的距离
                current_pos1 = person1.path[-1]
                dist1 = self.get_corridor_path_distance(current_pos1, door_pos)
                
                # Person2到该房间的距离
                current_pos2 = person2.path[-1]
                dist2 = self.get_corridor_path_distance(current_pos2, door_pos)
                
                if dist1 < min_dist1:
                    min_dist1, best_room1 = dist1, room_idx
                if dist2 < min_dist2:
                    min_dist2, best_room2 = dist2, room_idx
            
            # 计算分配后的总时间（平衡策略）
            room1 = self.rooms[best_room1]
            room2 = self.rooms[best_room2]
            
            # 计算分配给person1后的时间
            sweep_time1 = self.get_sweep_time(room1)
            time1_after = person1.total_time + min_dist1/1.5 + sweep_time1
            
            # 计算分配给person2后的时间
            sweep_time2 = self.get_sweep_time(room2)
            time2_after = person2.total_time + min_dist2/1.5 + sweep_time2
            
            # 选择分配后总时间更少的人（平衡策略）
            if time1_after <= time2_after:
                print(f"Person1 选择 {room1.name} (距离: {min_dist1:.1f}m, 时间后: {time1_after:.0f}s)")
                self._assign_room_optimized(person1, best_room1)
                unassigned.remove(best_room1)
            else:
                print(f"Person2 选择 {room2.name} (距离: {min_dist2:.1f}m, 时间后: {time2_after:.0f}s)")
                self._assign_room_optimized(person2, best_room2)
                unassigned.remove(best_room2)
        
        # 返回最近的出口
        exit1_dist = self.get_corridor_path_distance(person1.path[-1], self.exit1)
        exit2_dist = self.get_corridor_path_distance(person1.path[-1], self.exit2)
        if exit1_dist <= exit2_dist:
            person1.path.append(self.exit1)
            person1.total_distance += exit1_dist
            person1.total_time += exit1_dist / 1.5
        else:
            person1.path.append(self.exit2)
            person1.total_distance += exit2_dist
            person1.total_time += exit2_dist / 1.5
        
        exit1_dist = self.get_corridor_path_distance(person2.path[-1], self.exit1)
        exit2_dist = self.get_corridor_path_distance(person2.path[-1], self.exit2)
        if exit1_dist <= exit2_dist:
            person2.path.append(self.exit1)
            person2.total_distance += exit1_dist
            person2.total_time += exit1_dist / 1.5
        else:
            person2.path.append(self.exit2)
            person2.total_distance += exit2_dist
            person2.total_time += exit2_dist / 1.5
        
        return person1, person2
    
    def _assign_room_optimized(self, person, room_idx):
        room = self.rooms[room_idx]
        door_pos = (room.door_x, room.door_y)
        
        # 计算移动距离（不能穿墙）
        current_pos = person.path[-1]
        move_dist = self.get_corridor_path_distance(current_pos, door_pos)
        move_time = move_dist / 1.5
        sweep_time = self.get_sweep_time(room)
        
        print(f"  {room.name}: 面积={room.area:.1f}m², 复杂度c={room.complexity}, 检查时间={sweep_time:.0f}s")
        
        person.path.append(door_pos)
        person.rooms.append(f"{room.name}({sweep_time:.0f}s)")
        person.total_distance += move_dist
        person.total_time += move_time + sweep_time
    
    def visualize(self, person1, person2):
        fig, ax = plt.subplots(1, 1, figsize=(18, 12))
        
        # 绘制走廊
        for corridor in self.corridors_areas:
            rect = patches.Rectangle(
                (corridor["x"], corridor["y"]), corridor["width"], corridor["height"],
                linewidth=2, edgecolor='black', facecolor='white', alpha=0.8
            )
            ax.add_patch(rect)
        
        # 绘制房间
        colors = plt.cm.Set3(np.linspace(0, 1, len(self.rooms)))
        for i, room in enumerate(self.rooms):
            rect = patches.Rectangle(
                (room.x, room.y), room.width, room.height,
                linewidth=2, edgecolor='black', facecolor=colors[i], alpha=0.4
            )
            ax.add_patch(rect)
            
            cx, cy = room.x + room.width/2, room.y + room.height/2
            sample_sweep_time = self.get_sweep_time(room)
            room_label = f"{room.name}\n({sample_sweep_time:.0f}s)"
            ax.text(cx, cy, room_label, ha='center', va='center', fontsize=8, weight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9))
            
            # 门
            if room.door_angle == 270:
                door_start_angle = 0
            elif room.door_angle == 90:
                door_start_angle = 180
            elif room.door_angle == 180:
                door_start_angle = 270
            else:
                door_start_angle = 90
                
            door_arc = patches.Wedge((room.door_x, room.door_y), 1.0, 
                                   door_start_angle, door_start_angle + 90,
                                   facecolor='lightgray', edgecolor='black', linewidth=1.5, alpha=0.7)
            ax.add_patch(door_arc)
        
        # 出入口
        for i, door in enumerate(self.exit_doors, 1):
            door_arc = patches.Wedge((door["x"], door["y"]), 1.0, 
                                   door["angle"], door["angle"] + 90,
                                   facecolor='lightgreen', edgecolor='darkgreen', linewidth=2, alpha=0.8)
            ax.add_patch(door_arc)
            
        ax.plot(self.exit1[0], self.exit1[1], 'gs', markersize=15, label='Exit 1')
        ax.plot(self.exit2[0], self.exit2[1], 'gs', markersize=15, label='Exit 2')
        ax.text(self.exit1[0]-2, self.exit1[1]-2, 'EXIT 1', ha='center', fontsize=10, weight='bold', color='green')
        ax.text(self.exit2[0]+1, self.exit2[1]+1, 'EXIT 2', ha='center', fontsize=10, weight='bold', color='green')
        
        # 路径
        if len(person1.path) > 1:
            path1 = np.array(person1.path)
            ax.plot(path1[:, 0], path1[:, 1], 'ro-', linewidth=3, markersize=8, 
                   label=f'Person 1: {len(person1.rooms)} rooms, {person1.total_distance:.1f}m, {person1.total_time:.0f}s')
            
            ax.annotate('START 1', person1.path[0], xytext=(-15, 10), textcoords='offset points', 
                       fontsize=9, color='red', weight='bold', 
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='red'))
            ax.annotate('END 1', person1.path[-1], xytext=(10, 10), textcoords='offset points', 
                       fontsize=9, color='red', weight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='red'))
            
            for i, (x, y) in enumerate(person1.path[1:-1], 1):
                ax.annotate(str(i), (x, y), xytext=(5, 5), textcoords='offset points', 
                           fontsize=8, color='red')
        
        if len(person2.path) > 1:
            path2 = np.array(person2.path)
            ax.plot(path2[:, 0], path2[:, 1], 'bo-', linewidth=3, markersize=8,
                   label=f'Person 2: {len(person2.rooms)} rooms, {person2.total_distance:.1f}m, {person2.total_time:.0f}s')
            
            ax.annotate('START 2', person2.path[0], xytext=(15, -15), textcoords='offset points', 
                       fontsize=9, color='blue', weight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='blue'))
            ax.annotate('END 2', person2.path[-1], xytext=(-10, -15), textcoords='offset points', 
                       fontsize=9, color='blue', weight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='blue'))
            
            for i, (x, y) in enumerate(person2.path[1:-1], 1):
                ax.annotate(str(i), (x, y), xytext=(5, -15), textcoords='offset points', 
                           fontsize=8, color='blue')
        
        ax.set_xlim(-3, 45)
        ax.set_ylim(-3, 23)
        ax.set_xlabel('X (meters)', fontsize=12)
        ax.set_ylabel('Y (meters)', fontsize=12)
        
        total_time = person1.total_time + person2.total_time
        max_time = max(person1.total_time, person2.total_time)
        title_text = f'Optimized Building Inspection - Shortest Path\nTotal Time: {total_time:.0f}s ({total_time/60:.1f}min) | Max Time: {max_time:.0f}s ({max_time/60:.1f}min)'
        ax.set_title(title_text, fontsize=12, weight='bold')
        
        ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=10, frameon=True, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        plt.subplots_adjust(right=0.75)
        plt.savefig('/Users/peanut/Documents/himcm/algorithm/optimized_building_inspection.png', 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.show()
    
    def print_results(self, person1, person2):
        print("=" * 80)
        print("优化建筑房间检查结果 - 最短路径")
        print("=" * 80)
        print(f"人员1路径: {' → '.join(person1.rooms)} → 出口")
        print(f"  距离: {person1.total_distance:.1f}m, 时间: {person1.total_time:.0f}s ({person1.total_time/60:.1f}分钟)")
        print(f"人员2路径: {' → '.join(person2.rooms)} → 出口")
        print(f"  距离: {person2.total_distance:.1f}m, 时间: {person2.total_time:.0f}s ({person2.total_time/60:.1f}分钟)")
        print(f"总距离: {person1.total_distance + person2.total_distance:.1f}m")
        print(f"最大完成时间: {max(person1.total_time, person2.total_time):.0f}s ({max(person1.total_time, person2.total_time)/60:.1f}分钟)")
        print(f"时间差: {abs(person1.total_time - person2.total_time):.0f}s")
        print("=" * 80)

if __name__ == "__main__":
    building = OptimizedBuildingInspection()
    p1, p2 = building.optimize_assignment()
    building.print_results(p1, p2)
    building.visualize(p1, p2)