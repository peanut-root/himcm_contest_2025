# 房间检查贪心算法

## 问题描述

两个人需要检查完所有房间，优化路径分配。

### 房间布局
- **走廊长度**: 30m
- **出口**: exit1 和 exit2（在走廊两端）
- **左侧房间**:
  - L1: 距离 exit1 5m
  - L2: 距离 exit1 15m
  - L3: 距离 exit1 25m
- **右侧房间**:
  - R1: 距离 exit2 5m
  - R2: 距离 exit2 15m
  - R3: 距离 exit2 25m

## 需要补充的参数

以下参数可以在代码中配置，目前使用默认值：

1. **人员起始位置** (默认: person1在exit1, person2在exit2)
   - `person1_start`: 人员1的起始位置（距离exit1的距离，0-30米）
   - `person2_start`: 人员2的起始位置（距离exit1的距离，0-30米）

2. **移动速度** (默认: 1.0 米/分钟)
   - `move_speed`: 人员在走廊中的移动速度（米/分钟）

3. **房间检查时间** (默认: 1.0 分钟/房间)
   - 每个房间的检查时间可以不同
   - 可在代码中为每个房间单独设置 `inspection_time`

4. **优化目标** (可选)
   - 最小化总移动距离
   - 最小化最大完成时间（makespan）
   - 平衡两个人的工作量

## 使用方法

### 基本使用

```python
from room_inspection_greedy import RoomInspectionGreedy

# 创建算法实例
algorithm = RoomInspectionGreedy(hallway_length=30.0)

# 设置房间检查时间（可选）
algorithm.get_room_by_name("L1").inspection_time = 2.0
algorithm.get_room_by_name("L2").inspection_time = 1.5
# ... 其他房间

# 运行贪心算法（默认使用策略1：最近邻）
person1, person2 = algorithm.greedy_assign_rooms(
    person1_start=0.0,    # 人员1从exit1开始（默认）
    person2_start=30.0,   # 人员2从exit2开始（默认）
    move_speed=1.0,       # 移动速度 1米/分钟（默认）
    strategy="nearest"    # 策略1：最近邻（默认），或使用 "balanced" 切换为策略2
)

# 打印结果
algorithm.print_results(person1, person2)
```

### 运行示例

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行算法
python room_inspection_greedy.py
```

## 算法策略

**当前使用：策略1 - 最近邻贪心算法**

### 策略1: 最近邻贪心算法 (nearest) [默认]
- 每次选择距离当前位置最近的未分配房间
- 如果两个人都可以检查最近的房间，选择距离更近的
- **优点**: 简单快速，最小化移动距离
- **缺点**: 可能导致工作量不均衡

### 策略2: 平衡工作量贪心算法 (balanced) [可选]
- 考虑每个人的总工作量（时间）
- 选择分配后能使总时间更均衡的方案
- **优点**: 工作量更均衡，减少最大完成时间
- **缺点**: 可能增加总移动距离

> 注意：当前代码默认使用策略1。如需使用策略2，可在调用 `greedy_assign_rooms()` 时设置 `strategy="balanced"`

## 输出说明

算法会输出：
- 每个人的房间分配序列
- 总移动距离
- 总时间（包括移动时间和检查时间）
- 最终位置
- 总体统计（总距离、最大完成时间、时间差）

## 自定义参数示例

如果需要修改参数，编辑 `room_inspection_greedy.py` 中的 `main()` 函数：

```python
def main():
    algorithm = RoomInspectionGreedy(hallway_length=30.0)
    
    # 设置不同的检查时间
    algorithm.get_room_by_name("L1").inspection_time = 3.0
    algorithm.get_room_by_name("L2").inspection_time = 2.0
    algorithm.get_room_by_name("L3").inspection_time = 1.0
    algorithm.get_room_by_name("R1").inspection_time = 1.5
    algorithm.get_room_by_name("R2").inspection_time = 2.5
    algorithm.get_room_by_name("R3").inspection_time = 1.5
    
    # 设置不同的起始位置和移动速度
    person1, person2 = algorithm.greedy_assign_rooms(
        person1_start=10.0,   # 人员1从距离exit1 10m的位置开始
        person2_start=20.0,   # 人员2从距离exit1 20m的位置开始
        move_speed=2.0,       # 移动速度 2米/分钟
        strategy="balanced"
    )
    
    algorithm.print_results(person1, person2)
```

## 多层建筑检查模拟

### 功能说明
`multi_floor_building_inspection.py` - 实现了四层建筑（F1、F2、F3、F4）的房间检查模拟系统。

### 主要特性
- **多楼层支持**: 四层建筑结构（F1、F2、F3、F4），通过楼梯间连接
- **真实布局**: 基于 `docs/` 文件夹中的平面图（F1.png、F2.png、F3.pdf、F4.pdf）
- **走廊路径**: 采用曼哈顿距离，模拟真实走廊移动（不穿墙）
- **门禁系统**: 人员只能通过房间门进出
- **楼梯转换**: 支持楼层间垂直移动（速度为走廊的 0.5 倍）
- **贪心算法**: 最近邻分配策略，优化总完成时间
- **可视化输出**: 生成四层平面图，显示人员路径和房间分配

### 使用方法

```bash
# 运行模拟
python3 multi_floor_building_inspection.py

# 查看结果
# 控制台输出：人员路径、距离、时间统计
# 可视化文件：./output/multi_floor_building_inspection.png
```

### 输出示例

```
复杂多层建筑房间检查结果
================================================================================
人员1路径: Toilet(111s) → Stairwell(97s) → ... → 出口
  距离: 217.7m, 时间: 2747s (45.8分钟)
人员2路径: Office(102s) → Erotic reading materials(109s) → ... → 出口
  距离: 299.1m, 时间: 2856s (47.6分钟)
总距离: 516.8m
最大完成时间: 2856s (47.6分钟)
================================================================================
```

### 建筑结构
- **F1 楼层**: 7 个房间（洗手间、咖啡室、公共活动区、入口、楼梯间、自助服务区、设备间）
- **F2 楼层**: 8 个房间（洗手间、阅览室×2、电脑室、电源室、楼梯间、公共展览厅）
- **F3 楼层**: 7 个房间（多媒体室、专业博物馆、情色阅读资料室、儿童展览室、亲子互动区、楼梯间、洗手间）
- **F4 楼层**: 7 个房间（办公室×2、会议室×2、专业书店、楼梯间、洗手间）

### 技术细节
- **移动速度**: 走廊 1.5 m/s，楼梯 0.75 m/s
- **复杂度因子**: 空房间 1.0，有家具 1.5，有设备 1.8
- **检查时间**: 基于 USAR 标准，考虑房间面积、能见度、通信中断概率

## 未来改进

可以考虑的改进方向：
1. 添加动态规划算法寻找最优解
2. 支持更多人员（3人、4人等）
3. 考虑房间之间的优先级
4. 支持房间检查时间的动态变化
5. 实现优化策略对比功能（贪心 vs 负载均衡）

