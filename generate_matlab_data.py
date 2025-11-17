"""
生成MATLAB可视化所需的数据文件
运行算法并将结果保存为MATLAB可以读取的格式
"""

import json
from room_inspection_greedy import RoomInspectionGreedy

def generate_matlab_data():
    """生成MATLAB数据文件"""
    # 创建算法实例并运行
    algorithm = RoomInspectionGreedy(hallway_length=30.0)
    
    # 运行算法
    person1, person2 = algorithm.greedy_assign_rooms(
        person1_start=0.0,
        person2_start=30.0,
        move_speed=1.0,
        strategy="nearest"
    )
    
    # 构建人员路径（包括起始位置和每个房间的位置）
    def build_path(person, start_pos):
        """构建完整路径"""
        path = [start_pos]
        current_pos = start_pos
        
        for room_name in person.rooms_assigned:
            room = algorithm.get_room_by_name(room_name)
            room_pos = room.distance_from_exit1
            # 只有当位置发生变化时才添加到路径
            if room_pos != current_pos:
                path.append(room_pos)
                current_pos = room_pos
            else:
                # 如果位置相同，也添加（表示在同一位置检查不同房间）
                path.append(room_pos)
        
        return path, ['Start'] + person.rooms_assigned
    
    person1_path, person1_rooms = build_path(person1, 0.0)
    person2_path, person2_rooms = build_path(person2, 30.0)
    
    # 房间位置数据
    rooms_data = {}
    for room in algorithm.rooms:
        rooms_data[room.name] = {
            'distance_from_exit1': room.distance_from_exit1,
            'distance_from_exit2': room.distance_from_exit2,
            'side': room.side,
            'inspection_time': room.inspection_time
        }
    
    # 准备MATLAB数据
    matlab_data = {
        'hallway_length': 30.0,
        'exit1_pos': 0.0,
        'exit2_pos': 30.0,
        'rooms': rooms_data,
        'person1': {
            'path': person1_path,
            'rooms': person1_rooms,
            'total_distance': person1.total_distance,
            'total_time': person1.total_time,
            'final_position': person1.current_position
        },
        'person2': {
            'path': person2_path,
            'rooms': person2_rooms,
            'total_distance': person2.total_distance,
            'total_time': person2.total_time,
            'final_position': person2.current_position
        },
        'statistics': {
            'total_distance': person1.total_distance + person2.total_distance,
            'max_completion_time': max(person1.total_time, person2.total_time),
            'time_difference': abs(person1.total_time - person2.total_time)
        }
    }
    
    # 保存为JSON文件（MATLAB可以读取）
    with open('strategy_data.json', 'w', encoding='utf-8') as f:
        json.dump(matlab_data, f, indent=2, ensure_ascii=False)
    
    # 生成MATLAB脚本可以读取的.m文件
    with open('strategy_data.m', 'w', encoding='utf-8') as f:
        f.write('% 房间检查策略数据文件（自动生成）\n')
        f.write('% 运行 generate_matlab_data.py 生成此文件\n\n')
        
        f.write('% 走廊参数\n')
        f.write(f'hallway_length = {matlab_data["hallway_length"]};\n')
        f.write(f'exit1_pos = {matlab_data["exit1_pos"]};\n')
        f.write(f'exit2_pos = {matlab_data["exit2_pos"]};\n\n')
        
        f.write('% 房间位置\n')
        f.write('rooms = struct();\n')
        for room_name, room_data in rooms_data.items():
            f.write(f'rooms.{room_name} = {room_data["distance_from_exit1"]};  % {room_data["side"]} side\n')
        f.write('\n')
        
        f.write('% 人员1路径\n')
        f.write(f'person1_path = {person1_path};\n')
        # 构建房间列表字符串
        person1_rooms_str = ', '.join([f"'{r}'" for r in person1_rooms])
        f.write(f'person1_rooms = {{{person1_rooms_str}}};\n')
        f.write(f'person1_total_distance = {person1.total_distance};\n')
        f.write(f'person1_total_time = {person1.total_time};\n\n')
        
        f.write('% 人员2路径\n')
        f.write(f'person2_path = {person2_path};\n')
        # 构建房间列表字符串
        person2_rooms_str = ', '.join([f"'{r}'" for r in person2_rooms])
        f.write(f'person2_rooms = {{{person2_rooms_str}}};\n')
        f.write(f'person2_total_distance = {person2.total_distance};\n')
        f.write(f'person2_total_time = {person2.total_time};\n\n')
        
        f.write('% 统计信息\n')
        f.write(f'total_distance = {matlab_data["statistics"]["total_distance"]};\n')
        f.write(f'max_completion_time = {matlab_data["statistics"]["max_completion_time"]};\n')
        f.write(f'time_difference = {matlab_data["statistics"]["time_difference"]};\n')
    
    print("MATLAB数据文件已生成:")
    print("  - strategy_data.json")
    print("  - strategy_data.m")
    print("\n可以在MATLAB中运行 visualize_strategy.m 来可视化策略")


if __name__ == "__main__":
    generate_matlab_data()

