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

## 未来改进

可以考虑的改进方向：
1. 添加动态规划算法寻找最优解
2. 支持更多人员（3人、4人等）
3. 考虑房间之间的优先级
4. 支持房间检查时间的动态变化
5. 可视化路径分配结果

