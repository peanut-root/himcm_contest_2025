import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from room_inspection_greedy import RoomInspectionGreedy
from shortest_path_solver import ShortestPathSolver

def visualize_optimal_strategy(person1, person2, algorithm, save_path='optimal_strategy.png'):
    """可视化最优路径策略"""
    hallway_length = algorithm.hallway_length
    
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    # 出口标签
    ax.text(-1, 0, 'Exit1', fontsize=12, fontweight='bold', ha='right', va='center')
    ax.text(hallway_length + 1, 0, 'Exit2', fontsize=12, fontweight='bold', ha='left', va='center')
    
    # 绘制房间
    room_offset = 2.5
    for room in algorithm.rooms:
        pos = room.distance_from_exit1
        if room.side == 'left':
            ax.scatter(pos, room_offset, s=200, c='lightblue', edgecolors='blue', 
                      linewidths=2, marker='s', zorder=3)
            ax.plot([pos, pos], [0, room_offset], 'b--', linewidth=1.5, alpha=0.6)
            ax.text(pos, room_offset + 0.8, room.name, fontsize=11, fontweight='bold', 
                   ha='center', color='blue', va='bottom')
        else:
            ax.scatter(pos, -room_offset, s=200, c='lightcoral', edgecolors='red', 
                      linewidths=2, marker='s', zorder=3)
            ax.plot([pos, pos], [0, -room_offset], 'r--', linewidth=1.5, alpha=0.6)
            ax.text(pos, -room_offset - 0.8, room.name, fontsize=11, fontweight='bold', 
                   ha='center', color='red', va='top')
    
    # 人员1路径（蓝色）
    person1_color = '#2563eb'
    ax.plot(person1.path_positions, [0] * len(person1.path_positions), 
           '-', color=person1_color, linewidth=3.5, label='Person 1 (Optimal)', zorder=4)
    
    for i, (x, label) in enumerate(zip(person1.path_positions, person1.path_labels)):
        marker = 'o' if i == 0 else 'o'
        size = 130 if i == 0 else 100
        ax.scatter(x, 0, s=size, c=person1_color, edgecolors='white', 
                  linewidths=2, marker=marker, zorder=5)
        y_offset = 0.5 if i == 0 else 0.4
        ax.text(x, y_offset, label if i == 0 else label, fontsize=10, 
               fontweight='bold', color=person1_color, ha='center', va='bottom')
        
        # 箭头
        if i < len(person1.path_positions) - 1:
            x_start, x_end = person1.path_positions[i], person1.path_positions[i + 1]
            if abs(x_end - x_start) > 0.1:
                arrow_x = (x_start + x_end) / 2
                dx = x_end - x_start
                if dx > 0:
                    ax.annotate('', xy=(arrow_x + abs(dx)*0.15, 0), 
                               xytext=(arrow_x - abs(dx)*0.15, 0),
                               arrowprops=dict(arrowstyle='->', color=person1_color, 
                                             lw=2.5, headwidth=8, headlength=10), zorder=6)
                else:
                    ax.annotate('', xy=(arrow_x - abs(dx)*0.15, 0), 
                               xytext=(arrow_x + abs(dx)*0.15, 0),
                               arrowprops=dict(arrowstyle='->', color=person1_color, 
                                             lw=2.5, headwidth=8, headlength=10), zorder=6)
    
    # 人员2路径（红色）
    person2_color = '#dc2626'
    ax.plot(person2.path_positions, [0] * len(person2.path_positions), 
           '--', color=person2_color, linewidth=3.5, label='Person 2 (Optimal)', 
           zorder=4, dashes=(6, 3))
    
    for i, (x, label) in enumerate(zip(person2.path_positions, person2.path_labels)):
        marker = 's' if i == 0 else 's'
        size = 130 if i == 0 else 100
        ax.scatter(x, 0, s=size, c=person2_color, edgecolors='white', 
                  linewidths=2, marker=marker, zorder=5)
        y_offset = -0.5 if i == 0 else -0.4
        ax.text(x, y_offset, label if i == 0 else label, fontsize=10, 
               fontweight='bold', color=person2_color, ha='center', va='top')
        
        # 箭头
        if i < len(person2.path_positions) - 1:
            x_start, x_end = person2.path_positions[i], person2.path_positions[i + 1]
            if abs(x_end - x_start) > 0.1:
                arrow_x = (x_start + x_end) / 2
                dx = x_end - x_start
                if dx > 0:
                    ax.annotate('', xy=(arrow_x + abs(dx)*0.15, 0), 
                               xytext=(arrow_x - abs(dx)*0.15, 0),
                               arrowprops=dict(arrowstyle='->', color=person2_color, 
                                             lw=2.5, headwidth=8, headlength=10), zorder=6)
                else:
                    ax.annotate('', xy=(arrow_x - abs(dx)*0.15, 0), 
                               xytext=(arrow_x + abs(dx)*0.15, 0),
                               arrowprops=dict(arrowstyle='->', color=person2_color, 
                                             lw=2.5, headwidth=8, headlength=10), zorder=6)
    
    # 设置
    ax.set_xlim(-2, hallway_length + 2)
    ax.set_ylim(-5, 5)
    ax.set_xlabel('距离 Exit1 的位置 (米)', fontsize=12, fontweight='bold')
    ax.set_title('最优路径策略 - 最短完成时间', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper left', fontsize=11)
    ax.set_yticks([])
    
    # 统计信息
    stats_text = (
        f'Person 1: {person1.rooms_assigned} | {person1.total_distance:.1f}m | {person1.total_time:.1f}s\n'
        f'Person 2: {person2.rooms_assigned} | {person2.total_distance:.1f}m | {person2.total_time:.1f}s\n'
        f'最大完成时间: {max(person1.total_time, person2.total_time):.1f}s | 总距离: {person1.total_distance + person2.total_distance:.1f}m'
    )
    
    ax.text(0.02, 0.98, stats_text, fontsize=9, va='top', ha='left', 
           transform=ax.transAxes, family='monospace',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                    edgecolor='gray', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"最优路径图已保存: {save_path}")
    plt.close()

def main():
    algorithm = RoomInspectionGreedy(hallway_length=30.0)
    solver = ShortestPathSolver(algorithm)
    
    # 求解最优路径
    person1, person2 = solver.solve_optimal(
        person1_start=0.0, person2_start=30.0, 
        hallway_speed=1.5, room_speed=1.0
    )
    
    # 可视化
    visualize_optimal_strategy(person1, person2, algorithm)

if __name__ == "__main__":
    main()