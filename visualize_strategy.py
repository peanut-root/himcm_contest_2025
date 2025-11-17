import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端，避免显示窗口
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from room_inspection_greedy import RoomInspectionGreedy

def visualize_strategy(person1, person2, algorithm, save_path='room_inspection_strategy.png'):
    """
    可视化房间检查策略
    
    参数：
    - person1: 人员1对象
    - person2: 人员2对象
    - algorithm: RoomInspectionGreedy算法实例
    - save_path: 保存图片的路径
    """
    # 获取数据
    hallway_length = algorithm.hallway_length
    exit1_pos = 0
    exit2_pos = hallway_length
    corridor_y = 0
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 不绘制走廊背景，只添加出口标签
    ax.text(exit1_pos - 1, corridor_y, 'Exit1', fontsize=12, 
            fontweight='bold', ha='right', va='center')
    ax.text(exit2_pos + 1, corridor_y, 'Exit2', fontsize=12, 
            fontweight='bold', ha='left', va='center')
    
    # 房间位置和样式
    room_offset = 2.5  # 房间距离走廊的偏移
    room_size = 100    # 房间标记大小
    
    # 绘制房间
    left_rooms = [room for room in algorithm.rooms if room.side == 'left']
    right_rooms = [room for room in algorithm.rooms if room.side == 'right']
    
    # 左侧房间（在走廊上方）
    for room in left_rooms:
        pos = room.distance_from_exit1
        # 绘制房间标记
        ax.scatter(pos, corridor_y + room_offset, s=room_size*2, 
                  c='lightblue', edgecolors='blue', linewidths=2, 
                  marker='s', zorder=3)
        # 绘制连接到走廊的线
        ax.plot([pos, pos], [corridor_y, corridor_y + room_offset], 
               'b--', linewidth=1.5, alpha=0.6, zorder=2)
        # 房间标签
        ax.text(pos, corridor_y + room_offset + 0.8, room.name, 
               fontsize=11, fontweight='bold', ha='center', 
               color='blue', va='bottom')
    
    # 右侧房间（在走廊下方）
    for room in right_rooms:
        pos = room.distance_from_exit1
        # 绘制房间标记
        ax.scatter(pos, corridor_y - room_offset, s=room_size*2, 
                  c='lightcoral', edgecolors='red', linewidths=2, 
                  marker='s', zorder=3)
        # 绘制连接到走廊的线
        ax.plot([pos, pos], [corridor_y, corridor_y - room_offset], 
               'r--', linewidth=1.5, alpha=0.6, zorder=2)
        # 房间标签
        ax.text(pos, corridor_y - room_offset - 0.8, room.name, 
               fontsize=11, fontweight='bold', ha='center', 
               color='red', va='top')
    
    # 人员1的路径（蓝色，实线）
    person1_color = '#2563eb'  # 更鲜明的蓝色
    person1_path_x = person1.path_positions
    person1_path_y = [corridor_y] * len(person1_path_x)
    
    # 绘制路径线（实线，加粗以突出显示）
    ax.plot(person1_path_x, person1_path_y, '-', color=person1_color, 
           linewidth=3.5, label='Person 1 Path', zorder=4, alpha=0.9, linestyle='-')
    
    # 绘制路径点和箭头
    for i in range(len(person1_path_x)):
        x = person1_path_x[i]
        label = person1.path_labels[i]
        
        if i == 0:
            # 起点（圆形标记）
            ax.scatter(x, corridor_y, s=130, c=person1_color, 
                      edgecolors='white', linewidths=2, 
                      marker='o', zorder=5)
            ax.text(x, corridor_y + 0.5, 'P1 Start', fontsize=9, 
                   fontweight='bold', color=person1_color, 
                   ha='center', va='bottom')
        else:
            # 房间位置（圆形标记）
            ax.scatter(x, corridor_y, s=100, c=person1_color, 
                      edgecolors='white', linewidths=1.5, 
                      marker='o', zorder=5)
            ax.text(x, corridor_y + 0.4, label, fontsize=10, 
                   fontweight='bold', color=person1_color, 
                   ha='center', va='bottom')
        
        # 绘制箭头（除了最后一个点）
        if i < len(person1_path_x) - 1:
            x_start = person1_path_x[i]
            x_end = person1_path_x[i + 1]
            dx = x_end - x_start
            
            if abs(dx) > 0.1:  # 只有当移动距离足够大时才绘制箭头
                # 箭头位置（路径的中间位置）
                arrow_x = (x_start + x_end) / 2
                arrow_y = corridor_y
                
                # 根据方向绘制箭头（加粗以突出显示）
                if dx > 0:
                    ax.annotate('', xy=(arrow_x + abs(dx)*0.15, arrow_y), 
                               xytext=(arrow_x - abs(dx)*0.15, arrow_y),
                               arrowprops=dict(arrowstyle='->', color=person1_color, 
                                             lw=2.5, alpha=0.95, shrinkA=0, shrinkB=0,
                                             headwidth=8, headlength=10), 
                               zorder=6)
                else:
                    ax.annotate('', xy=(arrow_x - abs(dx)*0.15, arrow_y), 
                               xytext=(arrow_x + abs(dx)*0.15, arrow_y),
                               arrowprops=dict(arrowstyle='->', color=person1_color, 
                                             lw=2.5, alpha=0.95, shrinkA=0, shrinkB=0,
                                             headwidth=8, headlength=10), 
                               zorder=6)
    
    # 人员2的路径（橙红色，虚线）
    person2_color = '#dc2626'  # 更鲜明的红色
    person2_path_x = person2.path_positions
    person2_path_y = [corridor_y] * len(person2_path_x)
    
    # 绘制路径线（虚线，加粗以突出显示）
    ax.plot(person2_path_x, person2_path_y, '--', color=person2_color, 
           linewidth=3.5, label='Person 2 Path', zorder=4, alpha=0.9, 
           dashes=(6, 3))
    
    # 绘制路径点和箭头
    for i in range(len(person2_path_x)):
        x = person2_path_x[i]
        label = person2.path_labels[i]
        
        if i == 0:
            # 起点（方形标记，与person1区分）
            ax.scatter(x, corridor_y, s=130, c=person2_color, 
                      edgecolors='white', linewidths=2, 
                      marker='s', zorder=5)
            ax.text(x, corridor_y - 0.5, 'P2 Start', fontsize=9, 
                   fontweight='bold', color=person2_color, 
                   ha='center', va='top')
        else:
            # 房间位置（方形标记）
            ax.scatter(x, corridor_y, s=100, c=person2_color, 
                      edgecolors='white', linewidths=1.5, 
                      marker='s', zorder=5)
            ax.text(x, corridor_y - 0.4, label, fontsize=10, 
                   fontweight='bold', color=person2_color, 
                   ha='center', va='top')
        
        # 绘制箭头（除了最后一个点）
        if i < len(person2_path_x) - 1:
            x_start = person2_path_x[i]
            x_end = person2_path_x[i + 1]
            dx = x_end - x_start
            
            if abs(dx) > 0.1:  # 只有当移动距离足够大时才绘制箭头
                # 箭头位置（路径的中间位置）
                arrow_x = (x_start + x_end) / 2
                arrow_y = corridor_y
                
                # 根据方向绘制箭头（加粗以突出显示）
                if dx > 0:
                    ax.annotate('', xy=(arrow_x + abs(dx)*0.15, arrow_y), 
                               xytext=(arrow_x - abs(dx)*0.15, arrow_y),
                               arrowprops=dict(arrowstyle='->', color=person2_color, 
                                             lw=2.5, alpha=0.95, shrinkA=0, shrinkB=0,
                                             headwidth=8, headlength=10), 
                               zorder=6)
                else:
                    ax.annotate('', xy=(arrow_x - abs(dx)*0.15, arrow_y), 
                               xytext=(arrow_x + abs(dx)*0.15, arrow_y),
                               arrowprops=dict(arrowstyle='->', color=person2_color, 
                                             lw=2.5, alpha=0.95, shrinkA=0, shrinkB=0,
                                             headwidth=8, headlength=10), 
                               zorder=6)
    
    # 设置坐标轴
    ax.set_xlim(-2, hallway_length + 2)
    ax.set_ylim(-5, 5)
    ax.set_xlabel('距离 Exit1 的位置 (米)', fontsize=12, fontweight='bold')
    ax.set_ylabel('位置', fontsize=12, fontweight='bold')
    ax.set_xticks(range(0, int(hallway_length) + 1, 5))
    ax.set_yticks([])
    
    # 添加标题
    ax.set_title('Room Inspection Strategy Visualization - Nearest Neighbor Greedy Algorithm', 
                fontsize=14, fontweight='bold', pad=20)
    
    # 添加图例
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    
    # 添加简化的统计信息（去掉框，只显示关键信息）
    person1_rooms_str = ', '.join(person1.rooms_assigned)
    person2_rooms_str = ', '.join(person2.rooms_assigned)
    
    stats_text = (
        f'Person 1: Rooms [{person1_rooms_str}] | Distance: {person1.total_distance:.1f}m | Time: {person1.total_time:.1f}s ({person1.total_time/60:.2f}min)\n'
        f'Person 2: Rooms [{person2_rooms_str}] | Distance: {person2.total_distance:.1f}m | Time: {person2.total_time:.1f}s ({person2.total_time/60:.2f}min)\n'
        f'Total Distance: {person1.total_distance + person2.total_distance:.1f}m | Max Time: {max(person1.total_time, person2.total_time):.1f}s | Time Diff: {abs(person1.total_time - person2.total_time):.1f}s'
    )
    
    ax.text(0.02, 0.98, stats_text, fontsize=9, 
           va='top', ha='left', transform=ax.transAxes,
           family='monospace', bbox=dict(boxstyle='round,pad=0.5', 
                                         facecolor='white', edgecolor='gray', 
                                         alpha=0.7, linewidth=0.5))
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"图片已保存为 {save_path}")
    
    # 显示图片（如果环境支持）
    try:
        plt.show()
    except:
        print("注意：无法显示图形窗口，但图片已保存")
    finally:
        plt.close()


def main():
    """主函数"""
    # 创建算法实例并运行
    algorithm = RoomInspectionGreedy(hallway_length=30.0)
    
    # 运行算法
    person1, person2 = algorithm.greedy_assign_rooms(
        person1_start=0.0,      # 人员1从exit1开始
        person2_start=30.0,     # 人员2从exit2开始
        hallway_speed=1.5,      # 走廊移动速度 1.5米/秒
        room_speed=1.0,         # 房间内移动速度 1.0米/秒
        strategy="nearest"      # 使用最近邻策略
    )
    
    # 打印结果
    algorithm.print_results(person1, person2)
    
    # 可视化
    print("\n正在生成可视化图表...")
    visualize_strategy(person1, person2, algorithm)


if __name__ == "__main__":
    main()

