from dataclasses import dataclass
from typing import List, Tuple
from itertools import permutations
import math
from room_inspection_greedy import RoomInspectionGreedy, Person, Room


class ShortestPathSolver:
    """最短路径求解器 - 使用动态规划求解TSP问题"""
    
    def __init__(self, algorithm: RoomInspectionGreedy):
        self.algorithm = algorithm
        self.rooms = algorithm.rooms
        self.hallway_length = algorithm.hallway_length
    
    def solve_optimal(self, person1_start: float = 0.0, person2_start: float = 30.0,
                     hallway_speed: float = 1.5, room_speed: float = 1.0) -> Tuple[Person, Person]:
        """
        求解最优分配方案
        使用暴力搜索所有可能的分配组合，找到总时间最短的方案
        """
        room_names = [room.name for room in self.rooms]
        n_rooms = len(room_names)
        
        best_total_time = float('inf')
        best_person1 = None
        best_person2 = None
        
        # 尝试所有可能的房间分配组合
        for i in range(1, n_rooms):  # person1分配1到n-1个房间
            for person1_rooms in self._combinations(room_names, i):
                person2_rooms = [room for room in room_names if room not in person1_rooms]
                
                # 为每个人找到最优访问顺序
                person1_optimal = self._find_optimal_order(
                    list(person1_rooms), person1_start, hallway_speed, room_speed
                )
                person2_optimal = self._find_optimal_order(
                    person2_rooms, person2_start, hallway_speed, room_speed
                )
                
                # 计算总完成时间（最大值）
                total_time = max(person1_optimal.total_time, person2_optimal.total_time)
                
                if total_time < best_total_time:
                    best_total_time = total_time
                    best_person1 = person1_optimal
                    best_person2 = person2_optimal
        
        return best_person1, best_person2
    
    def _combinations(self, items: List[str], r: int) -> List[List[str]]:
        """生成组合"""
        from itertools import combinations
        return [list(combo) for combo in combinations(items, r)]
    
    def _find_optimal_order(self, room_names: List[str], start_pos: float,
                           hallway_speed: float, room_speed: float) -> Person:
        """为给定房间列表找到最优访问顺序"""
        if not room_names:
            return Person(id=0, current_position=start_pos, rooms_assigned=[], 
                         total_distance=0.0, total_time=0.0)
        
        best_time = float('inf')
        best_person = None
        
        # 尝试所有可能的访问顺序
        for order in permutations(room_names):
            person = Person(
                id=0,
                current_position=start_pos,
                rooms_assigned=[],
                total_distance=0.0,
                total_time=0.0,
                path_positions=[start_pos],
                path_labels=['Start']
            )
            
            # 按顺序访问房间
            for room_name in order:
                room = self.algorithm.get_room_by_name(room_name)
                distance = abs(person.current_position - room.distance_from_exit1)
                
                # 计算时间
                hallway_move_time = distance / hallway_speed
                room_move_time = 4.0 / room_speed  # 房间内移动
                inspection_time = room.inspection_time
                
                # 更新
                person.total_distance += distance
                person.total_time += hallway_move_time + room_move_time + inspection_time
                person.current_position = room.distance_from_exit1
                person.rooms_assigned.append(room_name)
                person.path_positions.append(room.distance_from_exit1)
                person.path_labels.append(room_name)
            
            if person.total_time < best_time:
                best_time = person.total_time
                best_person = person
        
        return best_person


def main():
    """主函数 - 比较贪心算法和最优算法"""
    algorithm = RoomInspectionGreedy(hallway_length=30.0)
    solver = ShortestPathSolver(algorithm)
    
    print("=" * 60)
    print("贪心算法 vs 最优算法比较")
    print("=" * 60)
    
    # 贪心算法
    print("\n【贪心算法结果】")
    person1_greedy, person2_greedy = algorithm.greedy_assign_rooms(
        person1_start=0.0, person2_start=30.0, hallway_speed=1.5, room_speed=1.0, strategy="nearest"
    )
    algorithm.print_results(person1_greedy, person2_greedy)
    
    # 最优算法
    print("\n【最优算法结果】")
    person1_optimal, person2_optimal = solver.solve_optimal(
        person1_start=0.0, person2_start=30.0, hallway_speed=1.5, room_speed=1.0
    )
    algorithm.print_results(person1_optimal, person2_optimal)
    
    # 比较
    greedy_max_time = max(person1_greedy.total_time, person2_greedy.total_time)
    optimal_max_time = max(person1_optimal.total_time, person2_optimal.total_time)
    improvement = greedy_max_time - optimal_max_time
    
    print(f"\n【算法比较】")
    print(f"贪心算法最大完成时间: {greedy_max_time:.2f}秒")
    print(f"最优算法最大完成时间: {optimal_max_time:.2f}秒")
    print(f"改进: {improvement:.2f}秒 ({improvement/greedy_max_time*100:.1f}%)")


if __name__ == "__main__":
    main()