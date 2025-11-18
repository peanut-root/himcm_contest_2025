# Quickstart: Multi-Floor Building Inspection Simulation

**Feature**: 001-multi-floor-inspection
**Date**: 2025-11-17
**Estimated Time**: 5 minutes

## Prerequisites

- Python 3.9 or higher installed
- Existing `complex_single_level_building_inspection.py` functional (for reference)
- PDF floor plans in `docs/` folder (F1.pdf, F3.pdf, F4.pdf)

## Quick Start (3 steps)

### 1. Verify Dependencies

```bash
# Check Python version
python3 --version  # Should be 3.9+

# Verify required libraries (should already be installed from single-level sim)
python3 -c "import numpy, matplotlib; print('Dependencies OK')"
```

If dependencies missing:
```bash
pip3 install numpy matplotlib
```

---

### 2. Run the Simulation

```bash
# Execute multi-floor simulation
python3 multi_floor_building_inspection.py
```

**Expected output**:
```
复杂多层建筑房间检查结果
================================================================================
人员1路径: Storage Room(45s) → Toilet(12s) → Coffee(38s) → ... → 出口
  距离: 125.3m, 时间: 487s (8.1分钟)
人员2路径: Stairwell(5s) → Multi-media(42s) → ... → 出口
  距离: 118.7m, 时间: 502s (8.4分钟)
总距离: 244.0m
最大完成时间: 502s (8.4分钟)
================================================================================
```

**Generated files**:
- `./output/multi_floor_building_inspection.png` (visualization)

---

### 3. View Results

**Option A: Image viewer**
```bash
open ./output/multi_floor_building_inspection.png  # macOS
xdg-open ./output/multi_floor_building_inspection.png  # Linux
start ./output/multi_floor_building_inspection.png  # Windows
```

**Option B: Python inline (if using Jupyter)**
```python
from IPython.display import Image
display(Image('./output/multi_floor_building_inspection.png'))
```

---

## What You Should See

### Console Output

The text output shows:
- **Personnel 1 path**: List of rooms inspected in order with times
- **Personnel 2 path**: List of rooms inspected in order with times
- **Statistics**: Total distances, total times, max completion time

### Visualization (PNG)

The image should show:
- **3 floors stacked vertically** (F1 on bottom, F3 in middle, F4 on top)
- **Rooms labeled** with names from PDFs + inspection times
- **Red path** for Person 1
- **Blue path** for Person 2
- **Stairwell connections** marked with dashed purple lines between floors
- **Start/End markers** (START 1, START 2, END 1, END 2)

---

## Customization Examples

### Change Starting Positions

```python
# Edit main() function in multi_floor_building_inspection.py
building = MultiFloorBuildingInspection()

# Start both on F4 instead of F1
p1, p2 = building.greedy_assign(
    start1=(5, 10, "F4"),  # Person 1 starts on F4
    start2=(15, 10, "F4")  # Person 2 starts on F4
)
```

### Adjust Movement Speeds

```python
# Faster corridor movement, slower stairs
p1, p2 = building.greedy_assign(
    corridor_speed=2.0,          # 2.0 m/s (faster)
    stairwell_speed_factor=0.3   # 0.6 m/s on stairs (slower)
)
```

### Modify Room Complexity

```python
# Find room in __init__() method
Room("Coffee", floor="F1", ..., complexity=2.0)  # Increase from 1.8 to 2.0
```

---

## Validation Checklist

After running the simulation, verify:

- [ ] **All rooms inspected**: Count rooms in output == total rooms in PDFs
  - F1: 7 rooms (Toilet, Coffee, Entrance, Stairwell, Public Activity Area, self-service, Equipment)
  - F3: 5 rooms (Multi-media, Specialty Museum, Erotic reading materials, Children's Exhibition Room, parent-child interaction, Stairwell, Toilet)
  - F4: 5 rooms (Office, Meeting x2, Professional bookstore, Stairwell, Toilet)
  - **Total: 17 rooms** (adjust if PDFs differ)

- [ ] **No room duplicates**: Each room appears exactly once across Person 1 + Person 2

- [ ] **Paths continuous**: No gaps in visualization, all segments connected

- [ ] **Stairwell transitions shown**: Purple dashed lines between floors where personnel change levels

- [ ] **Times reasonable**:
  - Inspection times vary by room (larger/complex rooms take longer)
  - Total time includes movement + inspection
  - Stairwell transitions add time penalty

- [ ] **Room names match PDFs**: Chinese characters preserved, exact names from floor plans

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'numpy'"

**Solution**:
```bash
pip3 install numpy matplotlib
```

---

### Issue: "FileNotFoundError: ./output/..."

**Solution**: Create output directory manually:
```bash
mkdir -p ./output
```

---

### Issue: "Visualization shows overlapping floors"

**Solution**: Check figure size in `visualize()` method:
```python
fig, axes = plt.subplots(3, 1, figsize=(18, 24))  # Increase height if needed
```

---

### Issue: "Some rooms not assigned"

**Solution**: Verify room initialization in `__init__()`:
- Check that all rooms from PDFs are created
- Verify floor assignments ("F1", "F3", "F4")
- Ensure stairwell connects all floors

Debug with:
```python
print(f"Total rooms: {len(building.rooms)}")
print(f"Assigned rooms: {len(p1.rooms) + len(p2.rooms)}")
```

---

### Issue: "Stairwell speed factor = 0 causes error"

**Solution**: Use non-zero value (typical: 0.5):
```python
p1, p2 = building.greedy_assign(stairwell_speed_factor=0.5)
```

---

## Performance Benchmarks

Expected execution times on typical hardware:

| Configuration | Time | Notes |
|---------------|------|-------|
| 3 floors, 17 rooms, 2 personnel | < 2s | Baseline |
| 3 floors, 17 rooms, 3 personnel | < 3s | P3 feature |
| 5 floors, 30 rooms, 2 personnel | < 5s | Scalability test |
| 10 floors, 50 rooms, 2 personnel | < 15s | Constitution max |

If execution exceeds these times, consider:
- Reducing visualization resolution (DPI < 300)
- Simplifying pathfinding (fewer corridor waypoints)
- Profiling with `python -m cProfile`

---

## Next Steps

### Compare Optimization Strategies (P2)

```python
# Run with greedy strategy (default)
p1_greedy, p2_greedy = building.greedy_assign()
print(f"Greedy makespan: {max(p1_greedy.total_time, p2_greedy.total_time):.0f}s")

# Run with load-balanced strategy (implement in P2)
p1_balanced, p2_balanced = building.load_balanced_assign()
print(f"Balanced makespan: {max(p1_balanced.total_time, p2_balanced.total_time):.0f}s")
```

### Extend to More Personnel (P3)

```python
# Modify greedy_assign() to accept N personnel
p1, p2, p3 = building.greedy_assign_n_personnel(
    personnel_count=3,
    start_positions=[(0, 10, "F1"), (0, 10, "F1"), (35, 16.5, "F4")]
)
```

### Parameter Sensitivity Analysis (P3)

```python
# Test different speed configurations
for corridor_speed in [1.0, 1.5, 2.0]:
    for stair_factor in [0.3, 0.5, 0.7]:
        p1, p2 = building.greedy_assign(
            corridor_speed=corridor_speed,
            stairwell_speed_factor=stair_factor
        )
        print(f"Speed {corridor_speed}/{stair_factor}: {max(p1.total_time, p2.total_time):.0f}s")
```

---

## Success Criteria Verification

After completing quickstart, you should be able to confirm:

- [x] **SC-001**: Simulation executes in < 5 seconds ✅
- [x] **SC-002**: All rooms inspected exactly once (verify count) ✅
- [x] **SC-003**: Stairwell transitions visually marked (purple dashed lines) ✅
- [x] **SC-005**: Room names match PDFs 100% ✅
- [x] **SC-006**: Path continuity (no gaps in visualization) ✅
- [x] **SC-007**: Personnel at exit in final position ✅
- [x] **PE-001**: 300 DPI output readable ✅

If all criteria pass, the simulation is working correctly. Ready to proceed to optimization comparisons (P2) or parameter configuration (P3).
