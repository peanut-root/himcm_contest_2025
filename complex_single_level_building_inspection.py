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
        # 需要检查的房间（按照USAR标准设置复杂度）
        self.rooms = [
            Room("Storage Room", 0, 17, 10, 3, 5, 17, 270, 1.8),  # 仓库（货架、设备）
            Room("Restroom Room", 10, 17, 10, 3, 15, 17, 270, 1.0),  # 空旷洗手间
            Room("Lift", 20, 17, 2, 3, 21, 17, 270, 1.0),  # 空电梯间
            Room("Stairwell", 22, 17, 3, 3, 23.5, 17, 270, 1.0),  # 空楼梯间
            Room("Kitchen", 25, 17, 10, 3, 30, 17, 270, 1.8),  # 厨房（设备、器具）
            Room("Hall", 0, 8, 23, 8, 11.5, 8, 90, 1.0),  # 空大厅
            Room("Cafeteria", 25, 8, 10, 8, 25, 12, 180, 1.5),  # 餐厅（桌椅、家具）
            Room("Backstage Equipment Room", 0, 0, 23, 3, 11.5, 3, 90, 1.8),  # 后台设备间（设备）
            Room("Multipurpose Classroom", 25, 0, 8, 6, 25, 3, 180, 1.5),  # 多功能教室（家具）
            Room("Office", 33, 0, 8, 6, 33, 3, 180, 1.0)  # 空办公室
        ]
        
        # 走廊区域（仅用于可视化，不需要检查）
        self.corridors_areas = [
            {"name": "Upper Corridor", "x": 0, "y": 16, "width": 35, "height": 1}
        ]
        
        # 出入口门
        self.exit_doors = [
            {"x": 0, "y": 10, "angle": 0},     # Exit1门
            {"x": 35, "y": 16.5, "angle": 0}   # Exit2门
        ]
        
        # 出入口位置
        self.exit1 = (0, 10)   # 左侧出口
        self.exit2 = (35, 16.5)  # 右侧出口（Cafeteria上面走廊右端）
        
        # 主要通道点
        self.corridors = [(17.5, 16.5), (11.5, 16.5), (11.5, 8), (11.5, 3), (25, 12), (25, 3), (35, 16.5)]
    
    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)
    
    def get_path_distance(self, start, end):
        """简化的路径距离计算 - 通过走廊"""
        min_dist = float('inf')
        for corridor in self.corridors:
            dist = self.distance(start[0], start[1], corridor[0], corridor[1]) + \
                   self.distance(corridor[0], corridor[1], end[0], end[1])
            min_dist = min(min_dist, dist)
        
        direct = self.distance(start[0], start[1], end[0], end[1])
        return max(direct, min_dist * 0.8)
    
    def get_sweep_time(self, room):
        vis = random.uniform(0.0, 0.8)
        p_halt = random.uniform(0.05, 0.3)
        return sweep_time_gt(room.area, vis, p_halt, room.complexity)
    
    def find_nearest_exit(self, person):
        """找到最近的出口"""
        dist1 = self.get_path_distance((person.x, person.y), self.exit1)
        dist2 = self.get_path_distance((person.x, person.y), self.exit2)
        return self.exit1 if dist1 <= dist2 else self.exit2
    
    def greedy_assign(self, start1=(0, 10), start2=(35, 16.5)):
        person1 = Person(1, start1[0], start1[1], [], [start1])
        person2 = Person(2, start2[0], start2[1], [], [start2])
        unassigned = list(range(len(self.rooms)))
        
        while unassigned:
            best_assignment = None
            best_cost = float('inf')
            
            # 为每个人计算最优房间分配
            for idx in unassigned:
                room = self.rooms[idx]
                door = (room.door_x, room.door_y)
                
                # 计算分配给person1的成本
                dist1 = self.get_path_distance((person1.x, person1.y), door)
                move_time1 = dist1 / 1.5
                sweep_time1 = self.get_sweep_time(room)
                total_time1_after = person1.total_time + move_time1 + sweep_time1
                
                # 计算分配给person2的成本
                dist2 = self.get_path_distance((person2.x, person2.y), door)
                move_time2 = dist2 / 1.5
                sweep_time2 = self.get_sweep_time(room)
                total_time2_after = person2.total_time + move_time2 + sweep_time2
                
                # 选择使得最大完成时间最小的分配
                if total_time1_after <= total_time2_after:
                    cost = total_time1_after
                    assignment = (1, idx, dist1)
                else:
                    cost = total_time2_after
                    assignment = (2, idx, dist2)
                
                if cost < best_cost:
                    best_cost = cost
                    best_assignment = assignment
            
            # 执行最优分配
            person_id, room_idx, distance = best_assignment
            if person_id == 1:
                self._assign_room(person1, room_idx, distance)
            else:
                self._assign_room(person2, room_idx, distance)
            unassigned.remove(room_idx)
        
        # 检查完所有房间后，返回最近的出口
        self._return_to_nearest_exit(person1)
        self._return_to_nearest_exit(person2)
        
        return person1, person2
    
    def _assign_room(self, person, room_idx, distance):
        room = self.rooms[room_idx]
        
        person.path.append((room.door_x, room.door_y))
        person.x, person.y = room.door_x, room.door_y
        
        move_time = distance / 1.5
        sweep_time = self.get_sweep_time(room)
        
        # 存储房间名和检查时间
        person.rooms.append(f"{room.name}({sweep_time:.0f}s)")
        
        person.total_distance += distance
        person.total_time += move_time + sweep_time
    
    def _return_to_nearest_exit(self, person):
        """检查完所有房间后返回最近的出口"""
        nearest_exit = self.find_nearest_exit(person)
        if person.x != nearest_exit[0] or person.y != nearest_exit[1]:
            exit_distance = self.get_path_distance((person.x, person.y), nearest_exit)
            person.path.append(nearest_exit)
            person.x, person.y = nearest_exit
            person.total_distance += exit_distance
            person.total_time += exit_distance / 1.5
    
    def visualize(self, person1, person2):
        fig, ax = plt.subplots(1, 1, figsize=(18, 12))
        
        # 绘制走廊区域（白色）
        for corridor in self.corridors_areas:
            rect = patches.Rectangle(
                (corridor["x"], corridor["y"]), corridor["width"], corridor["height"],
                linewidth=2, edgecolor='black', facecolor='white', alpha=0.8
            )
            ax.add_patch(rect)
            cx, cy = corridor["x"] + corridor["width"]/2, corridor["y"] + corridor["height"]/2
            ax.text(cx, cy, corridor["name"], ha='center', va='center', fontsize=8, 
                   style='italic', color='gray')
        
        # 绘制需要检查的房间
        colors = plt.cm.Set3(np.linspace(0, 1, len(self.rooms)))
        for i, room in enumerate(self.rooms):
            rect = patches.Rectangle(
                (room.x, room.y), room.width, room.height,
                linewidth=2, edgecolor='black', facecolor=colors[i], alpha=0.4
            )
            ax.add_patch(rect)
            
            # 房间标签和检查时间
            cx, cy = room.x + room.width/2, room.y + room.height/2
            # 计算该房间的检查时间用于显示
            sample_sweep_time = self.get_sweep_time(room)
            room_label = f"{room.name}\n({sample_sweep_time:.0f}s)"
            ax.text(cx, cy, room_label, ha='center', va='center', fontsize=8, weight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9))
            
            # 门 - 半扇形（90度），向房间内部开启
            # 计算门向房间内部的方向
            if room.door_angle == 270:  # 门在房间下边，向上开
                door_start_angle = 0
            elif room.door_angle == 90:   # 门在房间上边，向下开  
                door_start_angle = 180
            elif room.door_angle == 180:  # 门在房间左边，向右开
                door_start_angle = 270
            else:  # 门在房间右边，向左开
                door_start_angle = 90
                
            door_arc = patches.Wedge((room.door_x, room.door_y), 1.0, 
                                   door_start_angle, door_start_angle + 90,
                                   facecolor='lightgray', edgecolor='black', linewidth=1.5, alpha=0.7)
            ax.add_patch(door_arc)
        
        # 走廊节点
        for x, y in self.corridors:
            ax.plot(x, y, 'go', markersize=4, alpha=0.5)
        
        # 出入口门和标记
        for i, door in enumerate(self.exit_doors, 1):
            # 出入口门的扇形
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
            
            # 起点和终点标记
            ax.annotate('START 1', person1.path[0], xytext=(-15, 10), textcoords='offset points', 
                       fontsize=9, color='red', weight='bold', 
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='red'))
            ax.annotate('END 1', person1.path[-1], xytext=(10, 10), textcoords='offset points', 
                       fontsize=9, color='red', weight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='red'))
            
            # 中间点编号
            for i, (x, y) in enumerate(person1.path[1:-1], 1):
                ax.annotate(str(i), (x, y), xytext=(5, 5), textcoords='offset points', 
                           fontsize=8, color='red')
        
        if len(person2.path) > 1:
            path2 = np.array(person2.path)
            ax.plot(path2[:, 0], path2[:, 1], 'bo-', linewidth=3, markersize=8,
                   label=f'Person 2: {len(person2.rooms)} rooms, {person2.total_distance:.1f}m, {person2.total_time:.0f}s')
            
            # 起点和终点标记
            ax.annotate('START 2', person2.path[0], xytext=(15, -15), textcoords='offset points', 
                       fontsize=9, color='blue', weight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='blue'))
            ax.annotate('END 2', person2.path[-1], xytext=(-10, -15), textcoords='offset points', 
                       fontsize=9, color='blue', weight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='blue'))
            
            # 中间点编号
            for i, (x, y) in enumerate(person2.path[1:-1], 1):
                ax.annotate(str(i), (x, y), xytext=(5, -15), textcoords='offset points', 
                           fontsize=8, color='blue')
        
        ax.set_xlim(-3, 45)
        ax.set_ylim(-3, 23)
        ax.set_xlabel('X (meters)', fontsize=12)
        ax.set_ylabel('Y (meters)', fontsize=12)
        
        # 在图上方显示总检查时间
        total_time = person1.total_time + person2.total_time
        max_time = max(person1.total_time, person2.total_time)
        title_text = f'Complex Single Level Building - Room Inspection\nTotal Time: {total_time:.0f}s ({total_time/60:.1f}min) | Max Time: {max_time:.0f}s ({max_time/60:.1f}min)'
        ax.set_title(title_text, fontsize=12, weight='bold')
        
        # 调整图例位置和大小
        ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=10, frameon=True, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        # 调整布局以显示完整图例
        plt.subplots_adjust(right=0.75)
        plt.savefig('./complex_single_level_building_inspection.png', 
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

if __name__ == "__main__":
    building = ComplexBuildingInspection()
    p1, p2 = building.greedy_assign()
    building.print_results(p1, p2)
    building.visualize(p1, p2)