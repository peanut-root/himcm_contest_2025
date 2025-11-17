import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from room_inspection_greedy import RoomInspectionGreedy

def main():
    # 创建算法实例并运行
    algorithm = RoomInspectionGreedy(hallway_length=30.0)
    person1, person2 = algorithm.greedy_assign_rooms(
        person1_start=0.0,
        person2_start=30.0,
        hallway_speed=1.5,
        room_speed=1.0,
        strategy="nearest"
    )
    
    # 创建简单的可视化
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 绘制走廊
    ax.axhline(y=0, color='black', linewidth=2, label='Hallway')
    
    # 绘制出口
    ax.scatter([0, 30], [0, 0], s=200, c='red', marker='s', label='Exits')
    ax.text(0, -0.5, 'Exit1', ha='center', fontweight='bold')
    ax.text(30, -0.5, 'Exit2', ha='center', fontweight='bold')
    
    # 绘制房间（全部用黑色连接线）
    left_rooms = [(5, 'L1'), (15, 'L2'), (25, 'L3')]
    right_rooms = [(25, 'R1'), (15, 'R2'), (5, 'R3')]
    
    for pos, name in left_rooms:
        ax.scatter(pos, 1.5, s=150, c='lightblue', marker='s', edgecolors='black')
        ax.text(pos, 1.8, name, ha='center', fontweight='bold')
        ax.plot([pos, pos], [0, 1.5], 'k--', alpha=0.7, linewidth=1)  # 黑色连接线
    
    for pos, name in right_rooms:
        ax.scatter(pos, -1.5, s=150, c='lightcoral', marker='s', edgecolors='black')
        ax.text(pos, -1.8, name, ha='center', fontweight='bold')
        ax.plot([pos, pos], [0, -1.5], 'k--', alpha=0.7, linewidth=1)  # 黑色连接线
    
    # 绘制人员路径（包括进入房间的轨迹和箭头）
    # Person 1 路径: Start(0) -> L1(5) -> R3(5) -> L2(15)
    person1_path_x = [0, 5, 5, 5, 5, 15, 15]
    person1_path_y = [0, 0, 1.5, 0, -1.5, 0, 1.5]
    
    # Person 2 路径: Start(30) -> L3(25) -> R1(25) -> R2(15)
    person2_path_x = [30, 25, 25, 25, 25, 15, 15]
    person2_path_y = [0, 0, 1.5, 0, -1.5, 0, -1.5]
    
    # 绘制Person 1路径
    ax.plot(person1_path_x, person1_path_y, 'b-', linewidth=3, alpha=0.8, label='Person 1 Path')
    for i, (x, y) in enumerate(zip(person1_path_x, person1_path_y)):
        if i == 0:
            ax.scatter(x, y, s=120, c='blue', marker='o', edgecolors='white', linewidths=2, zorder=5)
        else:
            ax.scatter(x, y, s=80, c='blue', marker='o', alpha=0.7, zorder=5)
    
    # 绘制Person 2路径
    ax.plot(person2_path_x, person2_path_y, 'r-', linewidth=3, alpha=0.8, label='Person 2 Path')
    for i, (x, y) in enumerate(zip(person2_path_x, person2_path_y)):
        if i == 0:
            ax.scatter(x, y, s=120, c='red', marker='s', edgecolors='white', linewidths=2, zorder=5)
        else:
            ax.scatter(x, y, s=80, c='red', marker='s', alpha=0.7, zorder=5)
    
    # 添加箭头指示方向
    # Person 1 箭头
    ax.annotate('', xy=(3, 0), xytext=(1, 0), arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    ax.annotate('', xy=(5, 1), xytext=(5, 0.5), arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    ax.annotate('', xy=(5, 0.5), xytext=(5, 1), arrowprops=dict(arrowstyle='->', color='blue', lw=2))  # L1回程
    ax.annotate('', xy=(5, -1), xytext=(5, -0.5), arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    ax.annotate('', xy=(5, -0.5), xytext=(5, -1), arrowprops=dict(arrowstyle='->', color='blue', lw=2))  # R3回程
    ax.annotate('', xy=(12, 0), xytext=(8, 0), arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    ax.annotate('', xy=(15, 1), xytext=(15, 0.5), arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    
    # Person 2 箭头
    ax.annotate('', xy=(27, 0), xytext=(29, 0), arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax.annotate('', xy=(25, 1), xytext=(25, 0.5), arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax.annotate('', xy=(25, 0.5), xytext=(25, 1), arrowprops=dict(arrowstyle='->', color='red', lw=2))  # L3回程
    ax.annotate('', xy=(25, -1), xytext=(25, -0.5), arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax.annotate('', xy=(25, -0.5), xytext=(25, -1), arrowprops=dict(arrowstyle='->', color='red', lw=2))  # R1回程
    ax.annotate('', xy=(18, 0), xytext=(22, 0), arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax.annotate('', xy=(15, -1), xytext=(15, -0.5), arrowprops=dict(arrowstyle='->', color='red', lw=2))
    
    # 设置图形属性
    ax.set_xlim(-2, 32)
    ax.set_ylim(-2.5, 2.5)
    ax.set_xlabel('Distance from Exit1 (meters)')
    ax.set_title('Room Inspection Strategy - Nearest Neighbor Greedy Algorithm')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 添加统计信息
    stats_text = (
        f'Person 1: Rooms {person1.rooms_assigned} | Distance: {person1.total_distance:.1f}m | Time: {person1.total_time/60:.2f}min\n'
        f'Person 2: Rooms {person2.rooms_assigned} | Distance: {person2.total_distance:.1f}m | Time: {person2.total_time/60:.2f}min\n'
        f'Total Distance: {person1.total_distance + person2.total_distance:.1f}m | Max Time: {max(person1.total_time, person2.total_time)/60:.2f}min'
    )
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # 保存图片
    plt.tight_layout()
    plt.savefig('room_inspection_strategy.png', dpi=300, bbox_inches='tight')
    print("可视化图表已保存为 'room_inspection_strategy.png'")
    
    # 打印结果
    algorithm.print_results(person1, person2)

if __name__ == "__main__":
    main()