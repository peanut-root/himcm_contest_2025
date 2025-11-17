import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from dataclasses import dataclass
from typing import List, Tuple
import math

# 房间搜查时间计算函数 (来自nasv1)
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
    x: float  # 中心x坐标 (m)
    y: float  # 中心y坐标 (m) 
    width: float  # 宽度 (m)
    height: float  # 高度 (m)
    complexity: float  # 复杂度 1-2
    
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
        # 基于图纸尺寸创建房间 (mm转m)
        self.rooms = [
            Room("Storage Room", 5.0, 17.5, 10.0, 3.0, random.uniform(1.0, 1.5)),
            Room("Restroom Room", 15.0, 17.5, 10.0, 3.0, random.uniform(1.2, 1.8)),
            Room("Lift", 21.0, 17.5, 2.0, 3.0, random.uniform(1.0, 1.2)),
            Room("Stairwell", 23.0, 17.5, 3.0, 3.0, random.uniform(1.0, 1.2)),
            Room("Kitchen", 30.0, 17.5, 10.0, 3.0, random.uniform(1.3, 2.0)),
            Room("Hall", 11.5, 10.0, 23.0, 8.0, random.uniform(1.1, 1.6)),
            Room("Cafeteria", 30.0, 11.0, 10.0, 8.0, random.uniform(1.2, 1.8)),
            Room("Backstage Equipment Room", 11.5, 1.5, 23.0, 3.0, random.uniform(1.4, 2.0)),
            Room("Multipurpose Classroom", 21.0, 5.0, 8.0, 6.0, random.uniform(1.1, 1.7)),
            Room("Office", 33.0, 5.0, 8.0, 6.0, random.uniform(1.0, 1.4))
        ]
        
        # 建筑边界
        self.width = 41.0  # 总宽度
        self.height = 20.0  # 总高度
    
    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)
    
    def get_sweep_time(self, room):
        """使用nasv1算法计算房间搜查时间"""
        vis = random.uniform(0.0, 0.8)  # 可见度
        p_halt = random.uniform(0.05, 0.3)  # 停顿概率
        return sweep_time_gt(room.area, vis, p_halt, room.complexity)
    
    def greedy_assign(self, start1=(0, 0), start2=(41, 0)):
        person1 = Person(1, start1[0], start1[1], [], [start1])
        person2 = Person(2, start2[0], start2[1], [], [start2])
        unassigned = [r.name for r in self.rooms]
        
        while unassigned:
            # 找最近房间
            min_dist1 = min_dist2 = float('inf')
            nearest1 = nearest2 = None
            
            for room_name in unassigned:
                room = next(r for r in self.rooms if r.name == room_name)
                d1 = self.distance(person1.x, person1.y, room.x, room.y)
                d2 = self.distance(person2.x, person2.y, room.x, room.y)
                
                if d1 < min_dist1:
                    min_dist1, nearest1 = d1, room_name
                if d2 < min_dist2:
                    min_dist2, nearest2 = d2, room_name
            
            # 分配给距离更近的人
            if min_dist1 <= min_dist2:
                self._assign(person1, nearest1, min_dist1)
                unassigned.remove(nearest1)
            else:
                self._assign(person2, nearest2, min_dist2)
                unassigned.remove(nearest2)
        
        return person1, person2
    
    def _assign(self, person, room_name, distance):
        room = next(r for r in self.rooms if r.name == room_name)
        person.x, person.y = room.x, room.y
        person.rooms.append(room_name)
        person.path.append((room.x, room.y))
        person.total_distance += distance
        sweep_time = self.get_sweep_time(room)
        person.total_time += distance/1.5 + sweep_time  # 1.5m/s移动速度
    
    def visualize(self, person1, person2):
        fig, ax = plt.subplots(1, 1, figsize=(16, 10))
        
        # 绘制房间
        colors = plt.cm.Set3(np.linspace(0, 1, len(self.rooms)))
        for i, room in enumerate(self.rooms):
            rect = patches.Rectangle(
                (room.x - room.width/2, room.y - room.height/2),
                room.width, room.height,
                linewidth=1, edgecolor='black', facecolor=colors[i], alpha=0.3
            )
            ax.add_patch(rect)
            ax.text(room.x, room.y, room.name, ha='center', va='center', fontsize=8, weight='bold')
        
        # 绘制路径
        if len(person1.path) > 1:
            path1 = np.array(person1.path)
            ax.plot(path1[:, 0], path1[:, 1], 'ro-', linewidth=2, markersize=6, label=f'Person 1: {person1.rooms}')
            for i, (x, y) in enumerate(person1.path):
                ax.annotate(str(i), (x, y), xytext=(5, 5), textcoords='offset points', fontsize=8, color='red')
        
        if len(person2.path) > 1:
            path2 = np.array(person2.path)
            ax.plot(path2[:, 0], path2[:, 1], 'bo-', linewidth=2, markersize=6, label=f'Person 2: {person2.rooms}')
            for i, (x, y) in enumerate(person2.path):
                ax.annotate(str(i), (x, y), xytext=(5, -15), textcoords='offset points', fontsize=8, color='blue')
        
        ax.set_xlim(-2, 43)
        ax.set_ylim(-2, 22)
        ax.set_xlabel('X (meters)')
        ax.set_ylabel('Y (meters)')
        ax.set_title('Complex Building Room Inspection - Greedy Algorithm')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        plt.tight_layout()
        plt.savefig('complex_building_inspection.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def print_results(self, person1, person2):
        print("=" * 80)
        print("复杂建筑房间检查分配结果")
        print("=" * 80)
        print(f"人员1路径: {' → '.join(['起点'] + person1.rooms)}")
        print(f"  总距离: {person1.total_distance:.1f}m")
        print(f"  总时间: {person1.total_time:.1f}s ({person1.total_time/60:.1f}分钟)")
        
        print(f"\n人员2路径: {' → '.join(['起点'] + person2.rooms)}")
        print(f"  总距离: {person2.total_distance:.1f}m")
        print(f"  总时间: {person2.total_time:.1f}s ({person2.total_time/60:.1f}分钟)")
        
        print(f"\n总体统计:")
        print(f"  总距离: {person1.total_distance + person2.total_distance:.1f}m")
        print(f"  最大完成时间: {max(person1.total_time, person2.total_time):.1f}s ({max(person1.total_time, person2.total_time)/60:.1f}分钟)")
        print(f"  时间差: {abs(person1.total_time - person2.total_time):.1f}s")
        print("=" * 80)

if __name__ == "__main__":
    building = ComplexBuildingInspection()
    p1, p2 = building.greedy_assign()
    building.print_results(p1, p2)
    building.visualize(p1, p2)