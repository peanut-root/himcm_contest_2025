% 房间检查策略可视化脚本
% 策略1: 最近邻贪心算法
% 
% 使用方法：
% 1. 直接运行此脚本（使用内置数据）
% 2. 或先运行 generate_matlab_data.py 生成数据文件，然后运行此脚本

clear; clc; close all;

%% 尝试加载数据文件（如果存在）
if exist('strategy_data.m', 'file') == 2
    fprintf('正在加载 strategy_data.m ...\n');
    run('strategy_data.m');
    fprintf('数据文件加载成功！\n\n');
else
    fprintf('未找到 strategy_data.m，使用默认数据...\n');
    fprintf('提示：运行 generate_matlab_data.py 可以生成最新的数据文件\n\n');
    
    %% 默认参数设置
    hallway_length = 30;  % 走廊长度（米）
    exit1_pos = 0;        % exit1位置
    exit2_pos = 30;       % exit2位置
    
    % 房间位置（距离exit1的距离，米）
    rooms = struct();
    rooms.L1 = 5;   % 左侧房间1
    rooms.L2 = 15;  % 左侧房间2
    rooms.L3 = 25;  % 左侧房间3
    rooms.R1 = 25;  % 右侧房间1（距离exit2 5m = 距离exit1 25m）
    rooms.R2 = 15;  % 右侧房间2（距离exit2 15m = 距离exit1 15m）
    rooms.R3 = 5;   % 右侧房间3（距离exit2 25m = 距离exit1 5m）
    
    % 人员1的路径（从算法结果）
    person1_path = [0, 5, 5, 15, 15];  % 起始位置 -> L1 -> R3 -> L2 -> R2
    person1_rooms = {'Start', 'L1', 'R3', 'L2', 'R2'};
    person1_total_distance = 15.00;
    person1_total_time = 19.00;
    
    % 人员2的路径（从算法结果）
    person2_path = [30, 25, 25];  % 起始位置 -> L3 -> R1
    person2_rooms = {'Start', 'L3', 'R1'};
    person2_total_distance = 5.00;
    person2_total_time = 7.00;
    
    % 统计信息
    total_distance = 20.00;
    max_completion_time = 19.00;
    time_difference = 12.00;
end

%% 创建图形
figure('Position', [100, 100, 1200, 800]);
hold on;
grid on;
axis equal;

%% 不绘制走廊背景，只添加出口标签
corridor_y = 0;
text(exit1_pos-1, corridor_y, 'Exit1', 'FontSize', 12, 'FontWeight', 'bold', ...
     'HorizontalAlignment', 'right');
text(exit2_pos+1, corridor_y, 'Exit2', 'FontSize', 12, 'FontWeight', 'bold', ...
     'HorizontalAlignment', 'left');

%% 绘制房间（左侧和右侧分开显示）
room_offset = 2;  % 房间距离走廊的偏移
room_size = 1.5;  % 房间标记大小

% 左侧房间（在走廊上方）
left_rooms_pos = [rooms.L1, rooms.L2, rooms.L3];
for i = 1:length(left_rooms_pos)
    pos = left_rooms_pos(i);
    room_name = sprintf('L%d', i);
    % 绘制房间标记
    plot(pos, corridor_y + room_offset, 's', 'MarkerSize', room_size*10, ...
         'MarkerFaceColor', [0.8, 0.9, 1.0], 'MarkerEdgeColor', 'b', 'LineWidth', 2);
    % 绘制连接到走廊的线
    plot([pos, pos], [corridor_y, corridor_y + room_offset], 'b--', 'LineWidth', 1);
    % 房间标签
    text(pos, corridor_y + room_offset + 0.8, room_name, 'FontSize', 11, ...
         'FontWeight', 'bold', 'HorizontalAlignment', 'center', 'Color', 'b');
end

% 右侧房间（在走廊下方）
right_rooms_pos = [rooms.R1, rooms.R2, rooms.R3];
right_room_names = {'R1', 'R2', 'R3'};
for i = 1:length(right_rooms_pos)
    pos = right_rooms_pos(i);
    room_name = right_room_names{i};
    % 绘制房间标记
    plot(pos, corridor_y - room_offset, 's', 'MarkerSize', room_size*10, ...
         'MarkerFaceColor', [1.0, 0.9, 0.8], 'MarkerEdgeColor', 'r', 'LineWidth', 2);
    % 绘制连接到走廊的线
    plot([pos, pos], [corridor_y, corridor_y - room_offset], 'r--', 'LineWidth', 1);
    % 房间标签
    text(pos, corridor_y - room_offset - 0.8, room_name, 'FontSize', 11, ...
         'FontWeight', 'bold', 'HorizontalAlignment', 'center', 'Color', 'r');
end

%% 绘制人员1的路径（蓝色）
person1_color = [0, 0.4470, 0.7410];  % 蓝色
person1_label_added = false;

% 绘制完整的路径线
plot(person1_path, ones(size(person1_path)) * corridor_y, '-', ...
     'Color', person1_color, 'LineWidth', 4, 'DisplayName', 'Person 1 Path');

% 绘制路径点和房间标记，并添加箭头
step_counter = 0;
for i = 1:length(person1_path)
    x = person1_path(i);
    if i == 1
        % 起点
        plot(x, corridor_y, 'o', 'MarkerSize', 14, 'MarkerFaceColor', person1_color, ...
             'MarkerEdgeColor', 'w', 'LineWidth', 2.5);
        text(x, corridor_y + 0.7, 'P1 Start', 'FontSize', 9, ...
             'FontWeight', 'bold', 'Color', person1_color, ...
             'HorizontalAlignment', 'center', 'BackgroundColor', 'w');
    else
        % 房间位置
        step_counter = step_counter + 1;
        if i <= length(person1_rooms)
            room_name = person1_rooms{i};
            if ~strcmp(room_name, 'Start')
                plot(x, corridor_y, 's', 'MarkerSize', 12, 'MarkerFaceColor', person1_color, ...
                     'MarkerEdgeColor', 'w', 'LineWidth', 2);
                % 添加房间名称和步骤编号
                text(x, corridor_y + 0.6, sprintf('%d: %s', step_counter, room_name), ...
                     'FontSize', 9, 'FontWeight', 'bold', 'Color', person1_color, ...
                     'HorizontalAlignment', 'center', 'BackgroundColor', 'w');
            end
        end
    end
    
    % 添加箭头（除了最后一个点）
    if i < length(person1_path)
        x_start = person1_path(i);
        x_end = person1_path(i + 1);
        dx = x_end - x_start;
        
        if abs(dx) > 0.1  % 只有当移动距离足够大时才绘制箭头
            % 箭头位置（路径的中间位置，稍微偏向起点）
            arrow_x = x_start + dx * 0.4;
            arrow_y = corridor_y;
            
            % 使用quiver绘制箭头（箭头长度为路径段长度的30%）
            arrow_length = dx * 0.3;
            quiver(arrow_x, arrow_y, arrow_length, 0, 'Color', person1_color, ...
                   'LineWidth', 2.5, 'MaxHeadSize', 1.0, 'AutoScale', 'off');
        end
    end
end

%% 绘制人员2的路径（红色）
person2_color = [0.8500, 0.3250, 0.0980];  % 橙红色
person2_label_added = false;

% 绘制完整的路径线
plot(person2_path, ones(size(person2_path)) * corridor_y, '-', ...
     'Color', person2_color, 'LineWidth', 4, 'DisplayName', 'Person 2 Path');

% 绘制路径点和房间标记，并添加箭头
step_counter = 0;
for i = 1:length(person2_path)
    x = person2_path(i);
    if i == 1
        % 起点
        plot(x, corridor_y, 'o', 'MarkerSize', 14, 'MarkerFaceColor', person2_color, ...
             'MarkerEdgeColor', 'w', 'LineWidth', 2.5);
        text(x, corridor_y - 0.7, 'P2 Start', 'FontSize', 9, ...
             'FontWeight', 'bold', 'Color', person2_color, ...
             'HorizontalAlignment', 'center', 'BackgroundColor', 'w');
    else
        % 房间位置
        step_counter = step_counter + 1;
        if i <= length(person2_rooms)
            room_name = person2_rooms{i};
            if ~strcmp(room_name, 'Start')
                plot(x, corridor_y, 's', 'MarkerSize', 12, 'MarkerFaceColor', person2_color, ...
                     'MarkerEdgeColor', 'w', 'LineWidth', 2);
                % 添加房间名称和步骤编号
                text(x, corridor_y - 0.6, sprintf('%d: %s', step_counter, room_name), ...
                     'FontSize', 9, 'FontWeight', 'bold', 'Color', person2_color, ...
                     'HorizontalAlignment', 'center', 'BackgroundColor', 'w');
            end
        end
    end
    
    % 添加箭头（除了最后一个点）
    if i < length(person2_path)
        x_start = person2_path(i);
        x_end = person2_path(i + 1);
        dx = x_end - x_start;
        
        if abs(dx) > 0.1  % 只有当移动距离足够大时才绘制箭头
            % 箭头位置（路径的中间位置，稍微偏向起点）
            arrow_x = x_start + dx * 0.4;
            arrow_y = corridor_y;
            
            % 使用quiver绘制箭头（箭头长度为路径段长度的30%）
            arrow_length = dx * 0.3;
            quiver(arrow_x, arrow_y, arrow_length, 0, 'Color', person2_color, ...
                   'LineWidth', 2.5, 'MaxHeadSize', 1.0, 'AutoScale', 'off');
        end
    end
end

%% 添加图例和标题
legend({'Person 1 Path', 'Person 2 Path'}, 'Location', 'northwest', 'FontSize', 12);
title('房间检查策略可视化 - 最近邻贪心算法（策略1）', 'FontSize', 14, 'FontWeight', 'bold');
xlabel('距离 Exit1 的位置 (米)', 'FontSize', 12);
ylabel('位置', 'FontSize', 12);

% 设置坐标轴范围
xlim([-2, 32]);
ylim([-4, 4]);

% 添加网格
set(gca, 'XTick', 0:5:30);
set(gca, 'YTick', []);

%% 添加统计信息文本框
% 构建人员1的房间列表字符串
person1_rooms_str = strjoin(person1_rooms(2:end), ', ');
% 构建人员2的房间列表字符串
person2_rooms_str = strjoin(person2_rooms(2:end), ', ');

stats_text = {
    sprintf('人员1: 检查房间 [%s]', person1_rooms_str);
    sprintf('       总移动距离: %.2f 米', person1_total_distance);
    sprintf('       总时间: %.2f 分钟', person1_total_time);
    sprintf('');
    sprintf('人员2: 检查房间 [%s]', person2_rooms_str);
    sprintf('       总移动距离: %.2f 米', person2_total_distance);
    sprintf('       总时间: %.2f 分钟', person2_total_time);
    sprintf('');
    sprintf('总体: 总移动距离 %.2f 米', total_distance);
    sprintf('      最大完成时间: %.2f 分钟', max_completion_time);
    sprintf('      时间差: %.2f 分钟', time_difference);
};

text(32, 3, stats_text, 'FontSize', 10, 'VerticalAlignment', 'top', ...
     'HorizontalAlignment', 'left', 'BackgroundColor', 'w', ...
     'EdgeColor', 'k', 'Margin', 5);

%% 保存图片
print('room_inspection_strategy.png', '-dpng', '-r300');
fprintf('图片已保存为 room_inspection_strategy.png\n');

