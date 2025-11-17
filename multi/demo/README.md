# 消防员巡视优化 - Web 演示

这是一个交互式的 Web 应用程序，用于可视化消防员建筑巡视路径优化方案。

## 概述

本演示可视化了 CLI 优化工具生成的巡视路线结果，展示：

- **建筑布局**: 6 个房间的办公楼配置，包含出口和走廊
- **消防员动画**: 消防员沿着优化路径移动的动画效果
- **房间状态**: 检查进度的可视化指示（待检查 → 检查中 → 已完成）
- **性能指标**: 实时显示完成时间、覆盖率和路径长度
- **播放控制**: 交互式控制，包括播放、暂停、速度调整和时间轴拖动

## 🚀 快速启动

### 方法 1: Python HTTP 服务器（推荐）

```bash
cd demo
python3 -m http.server 8000
```

然后在浏览器中打开: http://localhost:8000

### 方法 2: Node.js HTTP 服务器

```bash
cd demo
npx http-server -p 8000
```

然后在浏览器中打开: http://localhost:8000

### 方法 3: PHP 内置服务器

```bash
cd demo
php -S localhost:8000
```

### 方法 4: VS Code Live Server

1. 安装 [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) 扩展
2. 右键点击 \`demo/index.html\`
3. 选择 "Open with Live Server"

### 方法 5: 直接在浏览器中打开

```bash
cd demo
open index.html  # macOS
# 或
start index.html  # Windows
# 或
xdg-open index.html  # Linux
```

**注意**: 某些浏览器会阻止本地文件访问。如果演示无法加载数据文件，请使用方法 1-4。

## ✨ 功能特性

### 预配置场景

应用包含 4 个优化场景，展示不同的任务策略：

#### 1. Basic (基本场景)
- **消防员**: 2 个
- **房间**: 6 个
- **完成时间**: 109 秒
- **路径长度**: 62 单位
- **策略**: 完全覆盖，使用最近出口
- **特点**: 完美对称的路径分配

**路径分配**:
- A1: exit-left → R1 → R2 → R3 → exit-right (18 单位)
- A2: exit-right → R6 → R5 → R4 → exit-left (18 单位)

#### 2. Redundancy (冗余检查)
- **消防员**: 3 个
- **房间**: 6 个（含冗余检查）
- **完成时间**: 135 秒
- **路径长度**: 55 单位
- **策略**: 关键房间双重验证
- **特点**: A3 对 R1 和 R3 进行二次检查

**路径分配**:
- A1: exit-left → R1 → R4 → exit-left (8 单位)
- A2: exit-right → R2 → R5 → exit-right (8 单位)
- A3: exit-right → R3 → R6 → R1 → R3 → exit-right (39 单位)

#### 3. Return (返回起点)
- **消防员**: 2 个
- **房间**: 4 个
- **完成时间**: 87 秒
- **路径长度**: 48 单位
- **策略**: 返回起始出口
- **特点**: 消防员必须返回原始出发点

**路径分配**:
- A1: exit-left → R1 → R3 → exit-left (24 单位)
- A2: exit-right → R6 → R4 → exit-right (24 单位)

#### 4. Multi (多消防员高并行)
- **消防员**: 5 个
- **房间**: 6 个
- **完成时间**: 77 秒
- **路径长度**: 42 单位
- **策略**: 最大化并行操作
- **特点**: 更多消防员，更快完成

**路径分配**:
- A1: exit-left → R1 → exit-left (4 单位)
- A2: exit-left → R2 → exit-left (14 单位)
- A3: exit-right → R3 → exit-right (4 单位)
- A4: exit-left → R4 → exit-left (4 单位)
- A5: exit-left → R5 → R6 → exit-right (16 单位)

### 播放控制

- **Play/Pause**: 开始或暂停动画
- **Restart**: 重置到开始位置
- **Speed Control**: 调整播放速度 (0.5x - 3.0x)
- **Timeline Scrubber**: 拖动到任意时间点

### 性能指标显示

- **Makespan**: 总完成时间（最长消防员完成时间）
- **Coverage**: 房间检查覆盖率百分比
- **Path Length**: 所有消防员的总移动距离
- **Agent Times**: 每个消防员的单独完成时间
- **Agent Paths**: 详细的路径序列和移动距离

## 📐 距离模型

演示使用真实的建筑导航距离模型：

### 移动单位

- **进出房间**: 1 单位（垂直：走廊 ↔ 房间门）
- **走廊移动**: 5 单位/房间宽度（水平）
- **进出大楼**: 1 单位（走廊 ↔ 出口）
- **垂直穿越**: 4 单位（跨越走廊上下排房间）

### 计算示例

**R1 → R2** (水平相邻房间):
```
出 R1 门 (1) + 走廊水平移动 (5) + 进 R2 门 (1) = 7 单位
```

**R1 → R4** (垂直对应房间):
```
出 R1 门 (1) + 垂直穿越走廊 (4) + 进 R4 门 (1) = 6 单位
```

**R1 → R6** (对角房间):
```
出 R1 门 (1) + 水平 (10) + 垂直 (4) + 进 R6 门 (1) = 16 单位
```

## 📁 文件结构

```
demo/
├── index.html              # 主页面
├── README.md               # 本文档
├── styles/
│   └── main.css            # 样式表
├── scripts/
│   ├── building.js         # 建筑和房间渲染
│   ├── animation.js        # 消防员动画控制
│   ├── controls.js         # 播放控制和用户交互
│   └── metrics.js          # 性能指标显示
└── data/
    ├── building.json             # 建筑布局定义
    ├── results-basic.json        # 基本场景数据
    ├── results-redundancy.json   # 冗余场景数据
    ├── results-return.json       # 返回场景数据
    └── results-multi.json        # 多消防员场景数据
```

## 🎯 使用提示

### 房间状态颜色

- **黄色** (#ffd54f): 待检查
- **蓝色** (#29b6f6): 检查中
- **绿色** (#66bb6a): 已完成

### 消防员颜色

- A1: 红色 (#E74C3C)
- A2: 蓝色 (#3498DB)
- A3: 绿色 (#2ECC71)
- A4: 橙色 (#F39C12)
- A5: 紫色 (#9B59B6)

## 🔧 技术栈

- **Vanilla JavaScript ES6+**: 无框架，模块化设计
- **HTML5 Canvas**: 2D 渲染和动画
- **CSS3**: 现代化样式和布局
- **静态文件**: 无需服务器端代码，无需构建步骤

## 🌐 浏览器兼容性

支持所有现代桌面浏览器：

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📝 许可证

MIT License - 详见项目根目录 LICENSE 文件

## 🔗 相关链接

- [主项目 README](../README.md)
- [CLI 工具文档](../docs/快速入门指南.md)
- [项目规范](../specs/001-firefighter-patrol-optimization/spec.md)

---

**演示状态**: ✅ 生产就绪 | **版本**: 1.0.0 | **最后更新**: 2025-11-12
