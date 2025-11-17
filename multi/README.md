# 消防员巡视路径优化系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen.svg)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue.svg)](https://www.typescriptlang.org/)

一个基于图论和整数线性规划的消防员建筑巡视路径优化系统，用于最小化总完成时间的同时确保所有房间的完全覆盖。

## 📋 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [安装](#安装)
- [使用方法](#使用方法)
  - [Web 演示应用](#web-演示应用)
  - [CLI 命令行工具](#1-规划巡视路线cli)
- [示例场景](#示例场景)
- [命令参考](#命令参考)
- [架构设计](#架构设计)
- [算法说明](#算法说明)
- [开发指南](#开发指南)
  - [技术文档](#技术文档) ⭐
  - [构建和测试](#构建和测试)

## ✨ 功能特性

### 核心功能

- **🎯 路径优化**: 使用整数线性规划（ILP）最小化总完成时间（makespan）
- **🔍 完全覆盖**: 保证所有房间至少被检查一次
- **🔄 冗余检查**: 支持关键房间由不同消防员进行两次检查
- **🚪 返回出口**: 可选的任务完成后返回最近出口功能
- **📊 时间线可视化**: 生成交互式甘特图显示并行操作
- **⚡ 冲突检测**: 自动检测并报告房间检查时间冲突
- **🌐 Web 演示**: 交互式可视化界面，实时动画展示优化路径

### 算法支持

- **ILP (整数线性规划)**: 最优解，适用于中小规模场景
- **Hungarian (匈牙利算法)**: 次优解，快速分配
- **Greedy (贪心算法)**: 基准算法，快速但可能不是最优

### 输出格式

- **JSON**: 完整的路线详情和性能指标
- **文本时间线**: ASCII 甘特图用于终端查看
- **Mermaid 图表**: 专业的可视化图表
- **交互式 HTML**: 在浏览器中查看的独立网页

## 🚀 快速开始

### 前置要求

- Node.js >= 18.0.0
- npm >= 9.0.0
- Python 3.x（可选，用于启动 Web 演示）

### 方式 1: Web 演示（推荐）

最快速的体验方式，无需安装依赖：

```bash
# 克隆仓库
git clone <repository-url>
cd himcm/demo

# 启动 Web 服务器
python3 -m http.server 8000

# 在浏览器中打开
# http://localhost:8000
```

在浏览器中你将看到：
- ✅ 4 个预配置的优化场景
- ✅ 实时消防员移动动画
- ✅ 交互式播放控制
- ✅ 详细的性能指标

### 方式 2: CLI 工具

完整的优化引擎，可自定义场景：

```bash
# 克隆仓库
git clone <repository-url>
cd himcm

# 安装依赖
npm install

# 构建项目
npm run build

# 生成基本 6 房间场景的巡视路线
npm run example

# 查看结果
cat results.json

# 生成可视化时间线
npm run viz:basic

# 在浏览器中打开 timeline.html 查看交互式甘特图
```

## 📚 使用方法

### Web 演示应用

#### 快速启动

Web 演示提供了可视化界面，展示预先计算的优化路径方案：

```bash
# 启动 Web 演示服务器
cd demo
python3 -m http.server 8000

# 在浏览器中打开
open http://localhost:8000
```

或使用 Node.js:

```bash
cd demo
npx http-server -p 8000
```

#### 演示场景

Web 应用包含 4 个预配置场景：

1. **Basic (基本场景)** - 2 个消防员，6 个房间
   - 完成时间: 109秒
   - 路径长度: 62 单位
   - 完全覆盖，使用最近出口

2. **Redundancy (冗余场景)** - 3 个消防员，冗余检查
   - 完成时间: 135秒
   - 路径长度: 55 单位
   - 关键房间双重检查

3. **Return (返回场景)** - 2 个消防员，返回起点
   - 完成时间: 87秒
   - 路径长度: 48 单位
   - 消防员返回起始出口

4. **Multi (多消防员场景)** - 5 个消防员，高并行
   - 完成时间: 77秒
   - 路径长度: 42 单位
   - 最大化并行操作

#### 演示功能

- **实时动画**: 观看消防员移动和房间检查过程
- **播放控制**: 播放、暂停、重启、时间轴拖动
- **速度调节**: 0.5x - 3.0x 播放速度
- **性能指标**: 实时显示完成时间、覆盖率、路径长度
- **消防员路径**: 显示每个消防员的详细路径和距离
- **房间状态**: 可视化房间检查状态（待检查/检查中/已完成）

#### 距离模型

演示使用真实的建筑距离模型：

- **进出房间**: 1 单位（垂直移动：走廊 ↔ 房间门）
- **走廊移动**: 5 单位/房间宽度（水平移动）
- **进出大楼**: 1 单位（走廊 ↔ 出口）
- **垂直穿越**: 4 单位（跨越走廊）

示例计算（R1 → R2）：
```
出 R1 门 (1) + 走廊移动 (5) + 进 R2 门 (1) = 7 单位
```

#### 从源代码构建演示

Web 演示是纯静态应用，无需构建步骤：

```bash
# 1. 确保目录结构正确
demo/
├── index.html
├── styles/
│   └── main.css
├── scripts/
│   ├── building.js
│   ├── animation.js
│   ├── controls.js
│   └── metrics.js
└── data/
    ├── building.json
    ├── results-basic.json
    ├── results-redundancy.json
    ├── results-return.json
    └── results-multi.json

# 2. 启动任意 HTTP 服务器
# 方法 1: Python
python3 -m http.server 8000

# 方法 2: Node.js
npx http-server -p 8000

# 方法 3: PHP
php -S localhost:8000

# 3. 在浏览器中打开
# http://localhost:8000
```

#### 自定义场景数据

要创建自定义演示场景：

1. **修改建筑布局** (`demo/data/building.json`):
```json
{
  "id": "office-6-room",
  "nodes": [...],
  "edges": [...],
  "rooms": [...],
  "entrances": ["exit-left", "exit-right"]
}
```

2. **添加结果数据** (`demo/data/results-custom.json`):
```json
{
  "missionId": "custom-scenario",
  "scenario": "custom",
  "makespan": 120,
  "routes": [
    {
      "agentId": "A1",
      "startLocation": "exit-left",
      "actions": [
        {
          "type": "MOVE",
          "startTime": 0,
          "duration": 1,
          "from": "exit-left",
          "to": "hallway"
        },
        {
          "type": "INSPECT",
          "startTime": 2,
          "duration": 30,
          "location": "R1"
        }
      ],
      "roomsInspected": ["R1"],
      "completionTime": 34
    }
  ],
  "metrics": {
    "totalPathLength": 20,
    "coverage": 100,
    "roomsInspected": 6,
    "totalRooms": 6
  }
}
```

3. **更新场景选择器** (`demo/index.html`):
```html
<select id="scenario">
  <option value="custom">Custom Scenario</option>
</select>
```

### 1. 规划巡视路线（CLI）

```bash
# 基本用法
npm run plan -- -b <建筑配置文件> -a <消防员数量> -o <输出文件>

# 完整示例
npm run plan -- \
  -b examples/basic-6-room.json \
  -a 2 \
  -r R1,R3 \
  --return-to-exit \
  -o results.json
```

### 2. 验证配置或结果

```bash
# 验证建筑配置
npm run validate examples/basic-6-room.json

# 验证任务结果
npm run validate results.json
```

### 3. 生成可视化

```bash
# 生成所有格式（文本、Mermaid、HTML）
npm run visualize results.json

# 仅生成文本格式
npm run visualize results.json -f text -o timeline

# 自定义宽度
npm run visualize results.json -w 120
```

### 4. 性能基准测试

```bash
# 比较不同算法的性能
npm run benchmark examples/basic-6-room.json
```

## 🏢 示例场景

### 场景 1: 基本 6 房间办公楼

```bash
npm run example
# 输出: results.json
# 2 个消防员, 6 个房间, 完成时间: 195秒
```

### 场景 2: 冗余检查模式

关键房间（服务器机房、化学品存储）需要双重验证：

```bash
npm run example:redundancy
# 输出: redundancy-results.json
# 3 个消防员, 6 个房间（2个冗余）, 完成时间: 220秒
```

### 场景 3: 返回出口模式

确保所有消防员任务完成后返回安全出口：

```bash
npm run example:return
# 输出: return-results.json
# 2 个消防员, 4 个房间, 返回最近出口
```

### 场景 4: 组合模式

冗余检查 + 返回出口：

```bash
npm run example:combined
# 输出: combined-results.json
# 完整的安全协议执行
```

## 📖 命令参考

### plan 命令

生成最优巡视路线。

```bash
npm run plan -- [选项]

选项:
  -b, --building <文件>     建筑配置 JSON 文件（必需）
  -a, --agents <数量>       消防员数量（默认: 2）
  -s, --start <节点>        起始节点 ID（默认: 第一个入口）
  -r, --redundant <房间>    需要冗余检查的房间 ID（逗号分隔）
  --return-to-exit          要求消防员检查后返回出口
  -o, --output <文件>       输出文件（默认: results.json）
  --enter-time <秒数>       进入房间时间（默认: 5）
  --exit-time <秒数>        退出房间时间（默认: 5）
  --algorithm <类型>        算法: ilp, hungarian, greedy（默认: ilp）
```

### validate 命令

验证建筑配置或任务结果。

```bash
npm run validate <文件>

选项:
  -t, --type <类型>  文件类型: building 或 mission（自动检测）
```

### visualize 命令

生成时间线可视化。

```bash
npm run visualize <结果文件> [选项]

选项:
  -f, --format <类型>  输出格式: text, mermaid, both（默认: both）
  -o, --output <文件>  输出文件前缀（默认: timeline）
  -w, --width <字符>   文本可视化宽度（默认: 100）
```

### benchmark 命令

比较算法性能。

```bash
npm run benchmark <建筑文件> [选项]

选项:
  -a, --agents <数量>   消防员数量（默认: 2）
  -r, --redundant <房间>  冗余房间（逗号分隔）
  --runs <次数>          每个算法运行次数（默认: 5）
```

## 🏗️ 架构设计

### 项目结构

```
src/
├── models/          # 数据模型（Building, Room, Agent, Route等）
├── algorithms/      # 优化算法
│   ├── allocation/  # 任务分配（ILP, Hungarian, Greedy）
│   ├── pathfinding/ # 路径查找（A*）
│   └── validation/  # 验证和指标计算
├── simulation/      # 任务规划和执行引擎
├── visualization/   # 时间线生成（Mermaid, 文本）
├── io/             # 配置加载和输出格式化
└── cli/            # 命令行界面
    └── commands/   # CLI 命令实现

demo/              # Web 演示应用
├── index.html     # 主 HTML 页面
├── styles/        # CSS 样式
├── scripts/       # JavaScript 模块
│   ├── building.js   # 建筑渲染
│   ├── animation.js  # 消防员动画
│   ├── controls.js   # 播放控制
│   └── metrics.js    # 指标显示
└── data/          # 预配置场景数据
    ├── building.json           # 建筑布局
    ├── results-basic.json      # 基本场景
    ├── results-redundancy.json # 冗余场景
    ├── results-return.json     # 返回场景
    └── results-multi.json      # 多消防员场景

examples/           # 示例建筑配置
specs/             # 项目规范和任务
docs/              # 项目文档
```

### 核心组件

1. **Graph 模型**: 基于 graphology 的建筑图表示
2. **Mission Planner**: 协调任务分配和路径规划
3. **Simulation Engine**: 任务执行和状态管理
4. **Validation Layer**: 覆盖率、冗余性和冲突验证
5. **Visualization**: 时间线生成和甘特图渲染

## 🧮 算法说明

### 整数线性规划 (ILP)

**目标函数**: 最小化完成时间 T_max

```
minimize T_max
subject to:
  - 每个房间至少检查 1 次
  - 冗余房间检查 2 次（不同消防员）
  - 工作负载平衡
  - 时间约束
```

**适用场景**: 1-20 个房间，1-10 个消防员

**优点**:
- 找到最优或近似最优解
- 考虑多个约束条件
- 工作负载平衡

**缺点**:
- 大规模场景计算时间较长
- 可能无解（自动降级到贪心算法）

### A* 路径规划

使用欧几里得距离启发式函数查找最短路径。

**特性**:
- 动态边权重（首次通过需要清障）
- 保证最短路径
- 支持单向/双向边

### 性能指标

系统计算以下指标：

- **Makespan**: 总完成时间 T_max = max(T_a)
- **路径长度**: 总移动距离
- **冗余覆盖率**: 完成的冗余检查百分比
- **清障效率**: 已清除边/总遍历次数
- **负载均衡**: 消防员完成时间的标准差

## 🔧 开发指南

### 技术文档

**📘 [优化引擎技术文档](docs/技术文档-优化引擎.md)** - 完整的架构、算法和 API 参考

包含内容:
- 🏗️ 系统架构和设计原则
- 📦 核心模块详解（Models, Algorithms, Simulation）
- 🧮 算法深度解析（ILP, A*, Hungarian, Greedy）
- 🔌 扩展和修改指南
- 📚 完整 API 参考
- 💡 最佳实践和性能优化

### 构建和测试

```bash
# 构建 TypeScript
npm run build

# 运行测试
npm test

# 测试覆盖率
npm run test:coverage

# 代码检查
npm run lint

# 代码格式化
npm run format
```

### 创建自定义建筑

创建符合架构的 JSON 文件：

```json
{
  "id": "my-building",
  "nodes": [
    {"id": "exit-1", "kind": "EXIT", "x": 0, "y": 0},
    {"id": "corridor-1", "kind": "CORRIDOR", "x": 10, "y": 0},
    {"id": "door-R1", "kind": "DOOR", "x": 10, "y": 5}
  ],
  "edges": [
    {"id": "e1", "from": "exit-1", "to": "corridor-1", "baseTime": 10}
  ],
  "rooms": [
    {"id": "R1", "doorNode": "door-R1", "verifyTime": 30}
  ],
  "entrances": ["exit-1"],
  "exits": ["exit-1"]
}
```

使用 `npm run validate` 验证配置。

### 添加新算法

1. 在 `src/algorithms/allocation/` 创建新文件
2. 实现 `AllocationResult` 接口
3. 在 `plan` 命令中注册算法
4. 在 `benchmark` 命令中添加比较

## 📊 输出格式

### JSON 结果

```json
{
  "missionId": "office-6-room",
  "makespan": 195,
  "routes": [
    {
      "agentId": "A1",
      "actions": [...],
      "roomsInspected": ["R1", "R3", "R5"],
      "totalTime": 185
    }
  ],
  "metrics": {
    "makespan": 195,
    "redundancyCoverage": { "rate": 1.0 },
    "loadBalance": { "stdDev": 5.0 }
  },
  "validation": {
    "valid": true,
    "coverage": { "allRoomsInspected": true },
    "conflicts": { "noRoomConflicts": true }
  }
}
```

### 时间线可视化

**文本格式** - 终端查看：
```
A1  |▓▓▒▒████▒▒▓▓▒▒████▒▒
A2  |▓▓▓▓▒▒████▒▒▓▓▓▓▒▒████▒▒
```

**HTML 格式** - 浏览器交互式查看，包含：
- 彩色甘特图
- 时间轴标记
- 活动图例
- 冲突高亮

## 🤝 贡献

欢迎提交问题和拉取请求！

## 📝 许可证

MIT License - 详见 LICENSE 文件

## 🙏 致谢

本项目使用以下开源库：
- [graphology](https://graphology.github.io/) - 图数据结构
- [javascript-lp-solver](https://github.com/JWally/jsLPSolver) - 线性规划求解器
- [commander](https://github.com/tj/commander.js) - CLI 框架
- [chalk](https://github.com/chalk/chalk) - 终端颜色
- [mermaid](https://mermaid.js.org/) - 图表生成

---

**项目状态**: ✅ 生产就绪 | **版本**: 1.0.0 | **HiMCM 数学建模竞赛项目**
