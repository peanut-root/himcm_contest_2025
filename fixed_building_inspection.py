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

class BuildingInspection:
    def __init__(self):
        # 根据图纸正确建模房间位置和门
        self.rooms = [
            Room("Storage Room", 0, 16, 10, 4, 5, 16, random.uniform(1.0, 1.5)),
            Room("Restroom Room", 10, 16, 10, 4, 15, 16, random.uniform(1.2, 1.8)),
            Room("Lift", 20, 16, 2, 4, 21, 16, random.uniform(1.0, 1.2)),
            Room("Stairwell", 22, 16, 3, 4, 23.5, 16, random.uniform(1.0, 1.2)),
            Room("Kitchen", 25, 16, 10, 4, 30, 16, random.uniform(1.3, 2.0)),
            Room("Hall", 0, 8, 23, 8, 11.5, 8, random.uniform(1.1, 1.6)),
            Room("Cafeteria", 25, 8, 10, 8, 25, 12, random.uniform(1.2, 1.8)),
            Room("Backstage Equipment Room", 0, 0, 23, 3, 11.5, 3, random.uniform(1.4, 2.0)),
            Room("Multipurpose Classroom", 25, 0, 8, 6, 25, 3, random.uniform(1.1, 1.7)),
            Room("Office", 33, 0, 8, 6, 33, 3, random.uniform(1.0, 1.4))
        ]
        
        # 主要通道点
        self.corridors = [(11.5, 16), (11.5, 8), (11.5, 3), (25, 12), (25, 3)]
    
    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)
    
    def get_path_distance(self, start, end):
        """简化的路径距离计算 - 通过走廊"""
        # 找到最近的走廊点
        min_dist = float('inf')
        for corridor in self.corridors:
            dist = self.distance(start[0], start[1], corridor[0], corridor[1]) + \
                   self.distance(corridor[0], corridor[1], end[0], end[1])
            min_dist = min(min_dist, dist)
        
        # 直接距离作为下界
        direct = self.distance(start[0], start[1], end[0], end[1])
        return max(direct, min_dist * 0.8)  # 考虑走廊效率
    
    def get_sweep_time(self, room):
        vis = random.uniform(0.0, 0.8)
        p_halt = random.uniform(0.05, 0.3)
        return sweep_time_gt(room.area, vis, p_halt, room.complexity)
    
    def greedy_assign(self, start1=(0, 10), start2=(41, 10)):
        # 设置出入口
        exit1 = (0, 10)  # 左侧出口
        exit2 = (41, 10)  # 右侧出口
        
        person1 = Person(1, start1[0], start1[1], [], [start1])
        person2 = Person(2, start2[0], start2[1], [], [start2])
        unassigned = list(range(len(self.rooms)))
        
        while unassigned:
            min_dist1 = min_dist2 = float('inf')
            best_idx1 = best_idx2 = -1
            
            for idx in unassigned:
                room = self.rooms[idx]
                door = (room.door_x, room.door_y)
                
                dist1 = self.get_path_distance((person1.x, person1.y), door)
                dist2 = self.get_path_distance((person2.x, person2.y), door)
                
                if dist1 < min_dist1:
                    min_dist1, best_idx1 = dist1, idx
                if dist2 < min_dist2:
                    min_dist2, best_idx2 = dist2, idx
            
            # 分配给距离更近的人
            if min_dist1 <= min_dist2:
                self._assign_room(person1, best_idx1, min_dist1)
                unassigned.remove(best_idx1)
            else:
                self._assign_room(person2, best_idx2, min_dist2)
                unassigned.remove(best_idx2)
        
        # 检查完所有房间后，返回出口
        self._return_to_exit(person1, exit1)
        self._return_to_exit(person2, exit2)
        
        return person1, person2
    
    def _assign_room(self, person, room_idx, distance):
        room = self.rooms[room_idx]
        
        # 更新位置和路径
        person.path.append((room.door_x, room.door_y))
        person.x, person.y = room.door_x, room.door_y
        person.rooms.append(room.name)
        
        # 计算时间
        move_time = distance / 1.5
        sweep_time = self.get_sweep_time(room)
        
        person.total_distance += distance
        person.total_time += move_time + sweep_time
    
    def _return_to_exit(self, person, exit_pos):
        """检查完所有房间后返回出口"""
        if person.x != exit_pos[0] or person.y != exit_pos[1]:
            exit_distance = self.get_path_distance((person.x, person.y), exit_pos)
            person.path.append(exit_pos)
            person.x, person.y = exit_pos
            person.total_distance += exit_distance
            person.total_time += exit_distance / 1.5
    
    def visualize(self, person1, person2):
        fig, ax = plt.subplots(1, 1, figsize=(16, 10))
        
        # 绘制房间
        colors = plt.cm.Set3(np.linspace(0, 1, len(self.rooms)))
        for i, room in enumerate(self.rooms):
            rect = patches.Rectangle(
                (room.x, room.y), room.width, room.height,
                linewidth=2, edgecolor='black', facecolor=colors[i], alpha=0.4
            )
            ax.add_patch(rect)
            
            # 房间标签
            cx, cy = room.x + room.width/2, room.y + room.height/2
            ax.text(cx, cy, room.name, ha='center', va='center', fontsize=8, weight='bold')
            
            # 门 - 用扇形表示
            door_arc = patches.Wedge((room.door_x, room.door_y), 1.5, 0, 180, 
                                   facecolor='white', edgecolor='black', linewidth=2)
            ax.add_patch(door_arc)
        
        # 走廊节点
        for x, y in self.corridors:
            ax.plot(x, y, 'go', markersize=4, alpha=0.7)
        
        # 出入口标记
        ax.plot(0, 10, 'gs', markersize=12, label='Exit 1')
        ax.plot(41, 10, 'gs', markersize=12, label='Exit 2')
        ax.text(0, 8, 'EXIT 1', ha='center', fontsize=10, weight='bold', color='green')
        ax.text(41, 8, 'EXIT 2', ha='center', fontsize=10, weight='bold', color='green')
        
        # 路径
        if len(person1.path) > 1:
            path1 = np.array(person1.path)
            ax.plot(path1[:, 0], path1[:, 1], 'ro-', linewidth=3, markersize=8, 
                   label=f'Person 1: {len(person1.rooms)} rooms, {person1.total_distance:.1f}m, {person1.total_time:.0f}s')
            for i, (x, y) in enumerate(person1.path):
                if i == 0:
                    ax.annotate('START', (x, y), xytext=(5, 5), textcoords='offset points', 
                               fontsize=8, color='red', weight='bold')
                elif i == len(person1.path) - 1:
                    ax.annotate('END', (x, y), xytext=(5, 5), textcoords='offset points', 
                               fontsize=8, color='red', weight='bold')
                else:
                    ax.annotate(str(i), (x, y), xytext=(5, 5), textcoords='offset points', 
                               fontsize=8, color='red')
        
        if len(person2.path) > 1:
            path2 = np.array(person2.path)
            ax.plot(path2[:, 0], path2[:, 1], 'bo-', linewidth=3, markersize=8,
                   label=f'Person 2: {len(person2.rooms)} rooms, {person2.total_distance:.1f}m, {person2.total_time:.0f}s')
            for i, (x, y) in enumerate(person2.path):
                if i == 0:
                    ax.annotate('START', (x, y), xytext=(5, -15), textcoords='offset points', 
                               fontsize=8, color='blue', weight='bold')
                elif i == len(person2.path) - 1:
                    ax.annotate('END', (x, y), xytext=(5, -15), textcoords='offset points', 
                               fontsize=8, color='blue', weight='bold')
                else:
                    ax.annotate(str(i), (x, y), xytext=(5, -15), textcoords='offset points', 
                               fontsize=8, color='blue')
        
        ax.set_xlim(-2, 43)
        ax.set_ylim(-2, 22)
        ax.set_xlabel('X (meters)')
        ax.set_ylabel('Y (meters)')
        ax.set_title('Building Room Inspection - Corrected Layout & Pathfinding')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        plt.tight_layout()
        plt.savefig('fixed_building_inspection.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def print_results(self, person1, person2):
        print("=" * 70)
        print("建筑房间检查结果 - 修正版")
        print("=" * 70)
        print(f"人员1: {' → '.join(person1.rooms)}")
        print(f"  距离: {person1.total_distance:.1f}m, 时间: {person1.total_time:.0f}s")
        print(f"人员2: {' → '.join(person2.rooms)}")
        print(f"  距离: {person2.total_distance:.1f}m, 时间: {person2.total_time:.0f}s")
        print(f"总距离: {person1.total_distance + person2.total_distance:.1f}m")
        print(f"最大时间: {max(person1.total_time, person2.total_time):.0f}s")
        print("=" * 70)

if __name__ == "__main__":
    building = BuildingInspection()
    p1, p2 = building.greedy_assign()
    building.print_results(p1, p2)
    building.visualize(p1, p2)