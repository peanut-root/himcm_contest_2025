from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import math


@dataclass
class Room:
    """房间信息"""
    name: str
    side: str  # 'left' or 'right'
    distance_from_exit1: float  # 距离exit1的距离（米）
    distance_from_exit2: float  # 距离exit2的距离（米）
    inspection_time: float = 1.0  # 检查房间所需时间（秒）


@dataclass
class Person:
    """检查人员信息"""
    id: int
    current_position: float  # 当前位置（距离exit1的距离，0-30）
    rooms_assigned: List[str]  # 分配的房间列表
    total_distance: float  # 总移动距离
    total_time: float  # 总时间
    path_positions: List[float] = field(default_factory=list)  # 路径位置列表（用于可视化）
    path_labels: List[str] = field(default_factory=list)  # 路径标签列表（用于可视化）
    
    def __post_init__(self):
        """初始化路径列表"""
        if not self.path_positions:
            self.path_positions = [self.current_position]
        if not self.path_labels:
            self.path_labels = ['Start']


class RoomInspectionGreedy:
    """房间检查贪心算法"""
    
    def __init__(self, hallway_length: float = 30.0):
        """
        初始化
        
        参数：
        - hallway_length: 走廊长度（米）
        """
        self.hallway_length = hallway_length
        self.rooms = self._initialize_rooms()
        self.persons = []
        
    def _initialize_rooms(self) -> List[Room]:
        """初始化房间布局"""
        rooms = []
        
        # 左侧房间（距离exit1）
        left_rooms = [
            ("L1", 5),
            ("L2", 15),
            ("L3", 25)
        ]
        
        # 右侧房间（距离exit2，转换为距离exit1）
        right_rooms = [
            ("R1", 5),   # 距离exit2 5m = 距离exit1 25m
            ("R2", 15),  # 距离exit2 15m = 距离exit1 15m
            ("R3", 25)   # 距离exit2 25m = 距离exit1 5m
        ]
        
        for name, dist_from_exit1 in left_rooms:
            dist_from_exit2 = self.hallway_length - dist_from_exit1
            rooms.append(Room(
                name=name,
                side='left',
                distance_from_exit1=dist_from_exit1,
                distance_from_exit2=dist_from_exit2,
                inspection_time=35.0  # 房间检查时间35秒（固定值）
            ))
        
        for name, dist_from_exit2 in right_rooms:
            dist_from_exit1 = self.hallway_length - dist_from_exit2
            rooms.append(Room(
                name=name,
                side='right',
                distance_from_exit1=dist_from_exit1,
                distance_from_exit2=dist_from_exit2,
                inspection_time=35.0  # 房间检查时间35秒（固定值）
            ))
        
        return rooms
    
    def get_room_by_name(self, name: str) -> Optional[Room]:
        """根据房间名获取房间对象"""
        for room in self.rooms:
            if room.name == name:
                return room
        return None
    
    def calculate_distance(self, pos1: float, pos2: float) -> float:
        """计算两点之间的距离（沿走廊，不能穿墙）"""
        return abs(pos1 - pos2)
    
    def greedy_assign_rooms(self, 
                           person1_start: float = 0.0, 
                           person2_start: float = 30.0,
                           hallway_speed: float = 1.5,  # 走廊移动速度（米/秒）
                           room_speed: float = 1.0,     # 房间内移动速度（米/秒）
                           strategy: str = "nearest") -> Tuple[Person, Person]:
        """
        贪心算法分配房间（默认使用最近邻策略）
        
        参数：
        - person1_start: 人员1的起始位置（距离exit1的距离）
        - person2_start: 人员2的起始位置（距离exit1的距离）
        - hallway_speed: 走廊移动速度（米/秒），默认1.5 m/s
        - room_speed: 房间内移动速度（米/秒），默认1.0 m/s
        - strategy: 策略类型
            - "nearest": 总是选择距离当前位置最近的未分配房间（默认）
            - "balanced": 平衡两个人的工作量
        
        返回：
        - (person1, person2): 两个人员的分配结果
        """
        # 初始化两个人员
        person1 = Person(
            id=1,
            current_position=person1_start,
            rooms_assigned=[],
            total_distance=0.0,
            total_time=0.0,
            path_positions=[person1_start],
            path_labels=['Start']
        )
        person2 = Person(
            id=2,
            current_position=person2_start,
            rooms_assigned=[],
            total_distance=0.0,
            total_time=0.0,
            path_positions=[person2_start],
            path_labels=['Start']
        )
        
        # 未分配的房间
        unassigned_rooms = [room.name for room in self.rooms]
        
        if strategy == "nearest":
            # 策略1：最近邻贪心算法（带平衡机制）
            while unassigned_rooms:
                # 为每个人计算到最近未分配房间的距离
                person1_nearest = self._find_nearest_room(
                    person1.current_position, unassigned_rooms
                )
                person2_nearest = self._find_nearest_room(
                    person2.current_position, unassigned_rooms
                )
                
                # 计算距离
                dist1 = self.calculate_distance(
                    person1.current_position,
                    self.get_room_by_name(person1_nearest).distance_from_exit1
                )
                dist2 = self.calculate_distance(
                    person2.current_position,
                    self.get_room_by_name(person2_nearest).distance_from_exit1
                )
                
                # 平衡机制：优先确保房间分配均衡
                room_count1 = len(person1.rooms_assigned)
                room_count2 = len(person2.rooms_assigned)
                room_count_diff = room_count1 - room_count2
                distance_diff = abs(dist1 - dist2)
                
                # 如果房间数量有差异，优先分配给房间少的人
                # 只有当距离差异特别大（>12米）时，才选择距离更近的
                if abs(room_count_diff) > 0:
                    # 有房间数量差异，优先平衡
                    if room_count_diff > 0:  # person1房间更多
                        # 如果person2的距离不是特别远（距离差异<=12米），分配给person2
                        if distance_diff <= 12.0 or dist2 <= dist1 + 5.0:
                            self._assign_room_to_person(
                                person2, person2_nearest, dist2, hallway_speed, room_speed
                            )
                            unassigned_rooms.remove(person2_nearest)
                        else:
                            # person2距离太远，仍然分配给person1
                            self._assign_room_to_person(
                                person1, person1_nearest, dist1, hallway_speed, room_speed
                            )
                            unassigned_rooms.remove(person1_nearest)
                    else:  # person2房间更多
                        # 如果person1的距离不是特别远（距离差异<=12米），分配给person1
                        if distance_diff <= 12.0 or dist1 <= dist2 + 5.0:
                            self._assign_room_to_person(
                                person1, person1_nearest, dist1, hallway_speed, room_speed
                            )
                            unassigned_rooms.remove(person1_nearest)
                        else:
                            # person1距离太远，仍然分配给person2
                            self._assign_room_to_person(
                                person2, person2_nearest, dist2, hallway_speed, room_speed
                            )
                            unassigned_rooms.remove(person2_nearest)
                else:
                    # 房间数量相同，选择距离更近的人
                    if dist1 <= dist2:
                        self._assign_room_to_person(
                            person1, person1_nearest, dist1, hallway_speed, room_speed
                        )
                        unassigned_rooms.remove(person1_nearest)
                    else:
                        self._assign_room_to_person(
                            person2, person2_nearest, dist2, hallway_speed, room_speed
                        )
                        unassigned_rooms.remove(person2_nearest)
        
        elif strategy == "balanced":
            # 策略2：平衡工作量
            while unassigned_rooms:
                # 计算每个人如果分配最近房间后的总时间
                person1_nearest = self._find_nearest_room(
                    person1.current_position, unassigned_rooms
                )
                person2_nearest = self._find_nearest_room(
                    person2.current_position, unassigned_rooms
                )
                
                dist1 = self.calculate_distance(
                    person1.current_position,
                    self.get_room_by_name(person1_nearest).distance_from_exit1
                )
                dist2 = self.calculate_distance(
                    person2.current_position,
                    self.get_room_by_name(person2_nearest).distance_from_exit1
                )
                
                # 计算分配后的总时间（走廊移动时间 + 房间移动时间 + 房间检查时间）
                move_time1 = dist1 / hallway_speed
                move_time2 = dist2 / hallway_speed
                room1 = self.get_room_by_name(person1_nearest)
                room2 = self.get_room_by_name(person2_nearest)
                # 房间检查时间包括进入和离开房间的移动时间（假设房间深度2米，来回4米）
                room_enter_exit_distance = 4.0  # 进入和离开房间的总距离
                room_move_time = room_enter_exit_distance / room_speed
                
                time1_after = person1.total_time + move_time1 + room_move_time + room1.inspection_time
                time2_after = person2.total_time + move_time2 + room_move_time + room2.inspection_time
                
                # 选择分配后总时间较小的人，或者如果时间相同则选择距离更近的
                if time1_after < time2_after or \
                   (time1_after == time2_after and dist1 <= dist2):
                    self._assign_room_to_person(
                        person1, person1_nearest, dist1, hallway_speed, room_speed
                    )
                    unassigned_rooms.remove(person1_nearest)
                else:
                    self._assign_room_to_person(
                        person2, person2_nearest, dist2, hallway_speed, room_speed
                    )
                    unassigned_rooms.remove(person2_nearest)
        
        return person1, person2
    
    def _find_nearest_room(self, position: float, unassigned_rooms: List[str]) -> str:
        """找到距离当前位置最近的未分配房间"""
        min_distance = float('inf')
        nearest_room = None
        
        for room_name in unassigned_rooms:
            room = self.get_room_by_name(room_name)
            distance = self.calculate_distance(
                position, room.distance_from_exit1
            )
            if distance < min_distance:
                min_distance = distance
                nearest_room = room_name
        
        return nearest_room
    
    def _assign_room_to_person(self, person: Person, room_name: str, 
                               distance: float, hallway_speed: float, room_speed: float):
        """将房间分配给人员，更新位置和时间（确保不穿墙）"""
        room = self.get_room_by_name(room_name)
        
        # 计算走廊移动距离（不能穿墙，必须沿走廊移动）
        hallway_distance = abs(person.current_position - room.distance_from_exit1)
        
        # 计算时间
        # 走廊移动时间（秒）
        hallway_move_time = hallway_distance / hallway_speed
        
        # 房间内移动时间（进入和离开房间，假设房间深度2米，来回4米）
        room_enter_exit_distance = 4.0  # 进入和离开房间的总距离
        room_move_time = room_enter_exit_distance / room_speed
        
        # 房间检查时间（秒）
        inspection_time_seconds = room.inspection_time
        
        # 更新距离和时间（只计算走廊移动距离，房间内移动不计入总移动距离）
        person.total_distance += hallway_distance
        person.total_time += hallway_move_time + room_move_time + inspection_time_seconds
        
        # 更新位置（检查完房间后，人员回到走廊中房间门口的位置）
        person.current_position = room.distance_from_exit1
        
        # 记录路径（用于可视化）
        person.path_positions.append(room.distance_from_exit1)
        person.path_labels.append(room_name)
        
        # 添加房间到分配列表
        person.rooms_assigned.append(room_name)
    
    def print_results(self, person1: Person, person2: Person):
        """打印结果"""
        print("=" * 60)
        print("房间检查分配结果")
        print("=" * 60)
        print(f"\n人员1:")
        print(f"  分配房间: {person1.rooms_assigned}")
        print(f"  总移动距离: {person1.total_distance:.2f} 米")
        print(f"  总时间: {person1.total_time:.2f} 秒 ({person1.total_time/60:.2f} 分钟)")
        print(f"  最终位置: {person1.current_position:.2f} 米（距离exit1）")
        
        print(f"\n人员2:")
        print(f"  分配房间: {person2.rooms_assigned}")
        print(f"  总移动距离: {person2.total_distance:.2f} 米")
        print(f"  总时间: {person2.total_time:.2f} 秒 ({person2.total_time/60:.2f} 分钟)")
        print(f"  最终位置: {person2.current_position:.2f} 米（距离exit1）")
        
        print(f"\n总体统计:")
        print(f"  总移动距离: {person1.total_distance + person2.total_distance:.2f} 米")
        max_time = max(person1.total_time, person2.total_time)
        print(f"  最大完成时间: {max_time:.2f} 秒 ({max_time/60:.2f} 分钟)")
        time_diff = abs(person1.total_time - person2.total_time)
        print(f"  时间差: {time_diff:.2f} 秒 ({time_diff/60:.2f} 分钟)")
        print("=" * 60)
    
    def get_visualization_data(self, person1: Person, person2: Person):
        """获取可视化数据"""
        return {
            'person1': {
                'path_positions': person1.path_positions,
                'path_labels': person1.path_labels,
                'rooms_assigned': person1.rooms_assigned,
                'total_distance': person1.total_distance,
                'total_time': person1.total_time
            },
            'person2': {
                'path_positions': person2.path_positions,
                'path_labels': person2.path_labels,
                'rooms_assigned': person2.rooms_assigned,
                'total_distance': person2.total_distance,
                'total_time': person2.total_time
            },
            'rooms': {
                room.name: {
                    'distance_from_exit1': room.distance_from_exit1,
                    'side': room.side
                }
                for room in self.rooms
            },
            'hallway_length': self.hallway_length
        }


def main():
    """主函数 - 使用最近邻贪心算法（策略1）"""
    # 创建算法实例
    algorithm = RoomInspectionGreedy(hallway_length=30.0)
    
    # 设置房间检查时间（如果需要）
    # algorithm.get_room_by_name("L1").inspection_time = 2.0
    
    print("房间布局信息:")
    for room in algorithm.rooms:
        print(f"  {room.name}: 距离exit1 {room.distance_from_exit1}m, "
              f"距离exit2 {room.distance_from_exit2}m, "
              f"检查时间 {room.inspection_time}秒")
    
    print("\n" + "=" * 60)
    print("最近邻贪心算法（策略1）")
    print("=" * 60)
    person1, person2 = algorithm.greedy_assign_rooms(
        person1_start=0.0,      # 人员1从exit1开始
        person2_start=30.0,     # 人员2从exit2开始
        hallway_speed=1.5,      # 走廊移动速度 1.5米/秒
        room_speed=1.0,         # 房间内移动速度 1.0米/秒
        strategy="nearest"      # 使用最近邻策略
    )
    algorithm.print_results(person1, person2)
    
    return person1, person2, algorithm


if __name__ == "__main__":
    main()

