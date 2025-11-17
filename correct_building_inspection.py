import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from dataclasses import dataclass
from typing import List, Tuple, Dict
import math
from collections import defaultdict
import heapq

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
    x: float  # 左下角x坐标 (m)
    y: float  # 左下角y坐标 (m)
    width: float  # 宽度 (m)
    height: float  # 高度 (m)
    door_x: float  # 门的x坐标
    door_y: float  # 门的y坐标
    complexity: float  # 复杂度 1-2
    
    @property
    def area(self):
        return self.width * self.height
    
    @property
    def center(self):
        return (self.x + self.width/2, self.y + self.height/2)

@dataclass
class Person:
    id: int
    x: float
    y: float
    rooms: List[str]
    path: List[Tuple[float, float]]
    total_distance: float = 0.0
    total_time: float = 0.0

class CorrectBuildingInspection:
    def __init__(self):
        # 根据原始图纸正确建模房间 (mm转m)
        self.rooms = [
            # 上排房间
            Room("Storage Room", 0, 16, 10, 4, 5, 16, random.uniform(1.0, 1.5)),
            Room("Restroom Room", 10, 16, 10, 4, 15, 16, random.uniform(1.2, 1.8)),
            Room("Lift", 20, 16, 2, 4, 21, 16, random.uniform(1.0, 1.2)),
            Room("Stairwell", 22, 16, 3, 4, 23.5, 16, random.uniform(1.0, 1.2)),
            Room("Kitchen", 25, 16, 10, 4, 30, 16, random.uniform(1.3, 2.0)),
            
            # 中间大厅
            Room("Hall", 0, 8, 23, 8, 11.5, 8, random.uniform(1.1, 1.6)),
            
            # 右侧房间
            Room("Cafeteria", 25, 8, 10, 8, 25, 12, random.uniform(1.2, 1.8)),
            
            # 下排房间
            Room("Backstage Equipment Room", 0, 0, 23, 3, 11.5, 3, random.uniform(1.4, 2.0)),
            Room("Multipurpose Classroom", 25, 0, 8, 6, 25, 3, random.uniform(1.1, 1.7)),
            Room("Office", 33, 0, 8, 6, 33, 3, random.uniform(1.0, 1.4))
        ]
        
        # 走廊节点 - 关键通行点
        self.corridor_nodes = [
            (11.5, 16),  # 上走廊中心
            (11.5, 8),   # 大厅入口
            (11.5, 3),   # 下走廊中心
            (25, 12),    # 右侧走廊
            (25, 3),     # 右下走廊
        ]
        
        # 建筑边界
        self.width = 41.0
        self.height = 20.0
    
    def build_graph(self):
        """构建路径图，考虑门和走廊"""
        graph = defaultdict(list)
        
        # 所有可达点：房间门 + 走廊节点
        all_points = [(r.door_x, r.door_y) for r in self.rooms] + self.corridor_nodes
        
        # 连接规则：
        # 1. 房间门连接到最近的走廊节点
        for room in self.rooms:
            door = (room.door_x, room.door_y)
            min_dist = float('inf')
            nearest_corridor = None
            
            for corridor in self.corridor_nodes:
                dist = self.distance(door[0], door[1], corridor[0], corridor[1])
                if dist < min_dist:
                    min_dist = dist
                    nearest_corridor = corridor
            
            if nearest_corridor:
                graph[door].append((nearest_corridor, min_dist))
                graph[nearest_corridor].append((door, min_dist))
        
        # 2. 走廊节点之间的连接
        corridor_connections = [
            (0, 1), (1, 2), (1, 3), (3, 4)  # 走廊节点索引连接
        ]
        
        for i, j in corridor_connections:
            p1, p2 = self.corridor_nodes[i], self.corridor_nodes[j]
            dist = self.distance(p1[0], p1[1], p2[0], p2[1])
            graph[p1].append((p2, dist))
            graph[p2].append((p1, dist))
        
        return graph
    
    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)
    
    def dijkstra(self, graph, start, end):
        """Dijkstra最短路径算法"""
        distances = {node: float('inf') for node in graph}
        distances[start] = 0
        previous = {}
        pq = [(0, start)]
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current == end:
                break
                
            if current_dist > distances[current]:
                continue
                
            for neighbor, weight in graph[current]:
                distance = current_dist + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current
                    heapq.heappush(pq, (distance, neighbor))
        
        # 重建路径
        path = []
        current = end
        while current in previous:
            path.append(current)
            current = previous[current]
        path.append(start)
        path.reverse()
        
        return path, distances[end]
    
    def get_sweep_time(self, room):
        """使用nasv1算法计算房间搜查时间"""
        vis = random.uniform(0.0, 0.8)
        p_halt = random.uniform(0.05, 0.3)
        return sweep_time_gt(room.area, vis, p_halt, room.complexity)
    
    def greedy_assign_with_pathfinding(self, start1=(0, 10), start2=(41, 10)):
        """使用路径规划的贪心分配"""
        graph = self.build_graph()
        
        person1 = Person(1, start1[0], start1[1], [], [start1])
        person2 = Person(2, start2[0], start2[1], [], [start2])
        unassigned = [r.name for r in self.rooms]
        
        while unassigned:
            min_cost1 = min_cost2 = float('inf')
            best_room1 = best_room2 = None
            best_path1 = best_path2 = None
            
            # 为每个人计算到所有未分配房间的最短路径
            for room_name in unassigned:
                room = next(r for r in self.rooms if r.name == room_name)
                door = (room.door_x, room.door_y)
                
                # Person 1
                path1, dist1 = self.dijkstra(graph, (person1.x, person1.y), door)
                if dist1 < min_cost1:
                    min_cost1, best_room1, best_path1 = dist1, room_name, path1
                
                # Person 2
                path2, dist2 = self.dijkstra(graph, (person2.x, person2.y), door)
                if dist2 < min_cost2:
                    min_cost2, best_room2, best_path2 = dist2, room_name, path2
            
            # 分配给成本更低的人
            if min_cost1 <= min_cost2:
                self._assign_with_path(person1, best_room1, best_path1, min_cost1)
                unassigned.remove(best_room1)
            else:
                self._assign_with_path(person2, best_room2, best_path2, min_cost2)
                unassigned.remove(best_room2)
        
        return person1, person2
    
    def _assign_with_path(self, person, room_name, path, distance):
        room = next(r for r in self.rooms if r.name == room_name)
        
        # 更新路径
        person.path.extend(path[1:])  # 跳过起点
        person.x, person.y = room.door_x, room.door_y
        person.rooms.append(room_name)
        
        # 计算时间
        move_time = distance / 1.5  # 1.5m/s移动速度
        sweep_time = self.get_sweep_time(room)
        
        person.total_distance += distance
        person.total_time += move_time + sweep_time
    
    def visualize(self, person1, person2):
        fig, ax = plt.subplots(1, 1, figsize=(18, 12))
        
        # 绘制房间
        colors = plt.cm.Set3(np.linspace(0, 1, len(self.rooms)))
        for i, room in enumerate(self.rooms):
            rect = patches.Rectangle(
                (room.x, room.y), room.width, room.height,
                linewidth=2, edgecolor='black', facecolor=colors[i], alpha=0.4
            )
            ax.add_patch(rect)
            
            # 房间名称
            cx, cy = room.center
            ax.text(cx, cy, room.name, ha='center', va='center', 
                   fontsize=9, weight='bold', bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
            
            # 门的位置
            ax.plot(room.door_x, room.door_y, 'ks', markersize=8)
        
        # 绘制走廊节点
        for i, (x, y) in enumerate(self.corridor_nodes):
            ax.plot(x, y, 'go', markersize=6)
            ax.text(x+0.5, y+0.5, f'C{i}', fontsize=8, color='green')
        
        # 绘制路径
        if len(person1.path) > 1:
            path1 = np.array(person1.path)
            ax.plot(path1[:, 0], path1[:, 1], 'ro-', linewidth=3, markersize=8, 
                   label=f'Person 1: {" → ".join(person1.rooms)} ({person1.total_distance:.1f}m, {person1.total_time:.0f}s)')
            
            for i, (x, y) in enumerate(person1.path):
                ax.annotate(str(i), (x, y), xytext=(8, 8), textcoords='offset points', 
                           fontsize=10, color='red', weight='bold')
        
        if len(person2.path) > 1:
            path2 = np.array(person2.path)
            ax.plot(path2[:, 0], path2[:, 1], 'bo-', linewidth=3, markersize=8,
                   label=f'Person 2: {" → ".join(person2.rooms)} ({person2.total_distance:.1f}m, {person2.total_time:.0f}s)')
            
            for i, (x, y) in enumerate(person2.path):
                ax.annotate(str(i), (x, y), xytext=(8, -20), textcoords='offset points', 
                           fontsize=10, color='blue', weight='bold')
        
        ax.set_xlim(-2, 43)
        ax.set_ylim(-2, 22)
        ax.set_xlabel('X (meters)', fontsize=12)
        ax.set_ylabel('Y (meters)', fontsize=12)
        ax.set_title('Correct Building Layout - Shortest Path Room Inspection', fontsize=14, weight='bold')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        plt.tight_layout()
        plt.savefig('correct_building_inspection.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def print_results(self, person1, person2):
        print("=" * 80)
        print("正确建筑结构 - 最短路径房间检查分配结果")
        print("=" * 80)
        print(f"人员1路径: {' → '.join(['起点'] + person1.rooms)}")
        print(f"  总距离: {person1.total_distance:.1f}m")
        print(f"  总时间: {person1.total_time:.1f}s ({person1.total_time/60:.1f}分钟)")
        
        print(f"\n人员2路径: {' → '.join(['起点'] + person2.rooms)}")
        print(f"  总距离: {person2.total_distance:.1f}m")
        print(f"  总时间: {person2.total_time:.1f}s ({person2.total_time/60:.1f}分钟)")
        
        print(f"\n总体统计:")
        print(f"  总距离: {person1.total_distance + person2.total_distance:.1f}m")
        max_time = max(person1.total_time, person2.total_time)
        print(f"  最大完成时间: {max_time:.1f}s ({max_time/60:.1f}分钟)")
        print(f"  时间差: {abs(person1.total_time - person2.total_time):.1f}s")
        print("=" * 80)

if __name__ == "__main__":
    building = CorrectBuildingInspection()
    p1, p2 = building.greedy_assign_with_pathfinding()
    building.print_results(p1, p2)
    building.visualize(p1, p2)