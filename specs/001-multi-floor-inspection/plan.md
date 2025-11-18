# Implementation Plan: Multi-Floor Building Inspection Simulation

**Branch**: `001-multi-floor-inspection` | **Date**: 2025-11-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-multi-floor-inspection/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Extend the existing single-level building inspection simulation (complex_single_level_building_inspection.py) to support 3-floor buildings connected via stairwells. The simulation will model realistic vertical movement with time penalties, extract room data from PDF floor plans (F1.pdf, F3.pdf, F4.pdf), and visualize multi-floor personnel paths with stairwell transitions. Technical approach: Python dataclasses for Floor/Room/Person entities, matplotlib for 3-floor visualization, greedy optimization algorithm adapted for 3D spatial pathfinding with corridor and stairwell waypoints.

## Technical Context

**Language/Version**: Python 3.9+ (matching existing complex_single_level_building_inspection.py)
**Primary Dependencies**:
  - numpy (array operations, path calculations)
  - matplotlib (visualization, patches for doors/rooms)
  - dataclasses (entity modeling: Floor, Room, Person, PathSegment)
  - typing (type hints for List, Tuple)
  - math (distance calculations, sqrt)

**Storage**: Files only (PDF floor plans in docs/, PNG output in ./output/)
**Testing**: Visual validation (manual inspection of generated visualizations), sanity checks (room count, path continuity)
**Target Platform**: macOS/Linux/Windows desktop (Python script execution)
**Project Type**: Single project (standalone Python simulation script)
**Performance Goals**:
  - Simulation execution < 5 seconds for 3-floor, 20-room building
  - Supports up to 10 floors, 50 rooms within 30 seconds
  - Path optimization within 5% of manual verification

**Constraints**:
  - Must reuse existing sweep_time_gt formula from single-level simulation
  - PDF room data manually transcribed (no automated PDF parsing)
  - Visualization must fit 3 floors on single output image
  - Memory usage < 100MB for typical 3-floor scenarios

**Scale/Scope**:
  - 3 floors (F1, F3, F4) with ~20 total rooms
  - 2 personnel baseline (extensible to N personnel in P3)
  - 2 optimization strategies (greedy + load-balanced)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify compliance with principles from `.specify/memory/constitution.md`:

- [x] **Simulation Accuracy** (Principle I): ✅ Physical constraints modeled (1.5 m/s corridors, 0.75 m/s stairs, sweep_time_gt formula), floor plans reference F1/F3/F4.pdf, USAR complexity factors (1.0/1.5/1.8), inspection times include visibility/halt/clutter parameters
- [x] **Multi-Floor Architecture** (Principle II): ✅ Floor dataclass with independent floor configs, explicit Stairwell entity with transition times, vertical movement distinguished from horizontal (0.5x speed factor), floor-specific room collections and exits
- [x] **Data-Driven Configuration** (Principle III): ✅ Room properties extracted from PDFs (manually transcribed from F1/F3/F4.pdf), complexity factors configurable per room type, algorithm parameters (speed, visibility, halt) adjustable via function args
- [x] **Visualization Requirements** (Principle IV): ✅ Matplotlib rendering with mm→m conversion, room labels + inspection times displayed, personnel paths traced with sequence numbers, door wedges with orientations, 3-floor combined or separate views at 300 DPI
- [x] **Algorithm Optimization** (Principle V): ✅ Greedy assignment (nearest room + lowest current time), load-balanced strategy (minimize makespan), distance minimization via corridor waypoints, 2+ personnel support, return-to-nearest-exit logic

**Violations Requiring Justification**: None - all constitutional principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Repository root structure (single project)
.
├── multi_floor_building_inspection.py  # Main simulation script (new file)
├── complex_single_level_building_inspection.py  # Existing reference
├── docs/
│   ├── F1.pdf  # Floor 1 architectural plan (existing)
│   ├── F3.pdf  # Floor 3 architectural plan (existing)
│   └── F4.pdf  # Floor 4 architectural plan (existing)
├── output/
│   └── multi_floor_building_inspection.png  # Generated visualization (gitignored)
└── README.md  # Updated with multi-floor simulation usage
```

**Structure Decision**: Single standalone Python script following the pattern of `complex_single_level_building_inspection.py`. No separate src/ directory needed since this is a research simulation, not a production application. The script will contain all dataclasses (Floor, Room, Person, Stairwell, PathSegment), the MultiFloorBuildingInspection class, greedy assignment algorithm, and visualization logic. This keeps the codebase simple and easy to understand for HiMCM contest documentation.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations. All complexity is justified:
- **Manual PDF transcription** (instead of automated parsing): Simplifies implementation, only 3 PDFs with ~20 rooms total, one-time effort
- **Single monolithic script** (instead of modular src/ structure): Appropriate for research simulation, easier to share/review for contest submission
- **Visual validation** (instead of automated tests): Matches existing single-level pattern, sufficient for research validation

---

## Phase 1 Design Completion & Constitution Re-Check

**Artifacts Generated**:
- ✅ `research.md` - All technical unknowns resolved (3D pathfinding, visualization, PDF extraction, stairwell connectivity, greedy algorithm adaptation)
- ✅ `data-model.md` - 5 core entities defined (Room, Floor, Stairwell, Person, PathSegment) with validation rules and relationships
- ✅ `contracts/simulation_interface.md` - Public API contracts for MultiFloorBuildingInspection class methods
- ✅ `quickstart.md` - 3-step quickstart guide with validation checklist and troubleshooting
- ✅ `CLAUDE.md` - Agent context updated with Python 3.9+, file-based storage

**Constitution Re-Check (Post-Design)**:

All 5 constitutional principles remain satisfied after Phase 1 design:

- [x] **Principle I - Simulation Accuracy**: ✅ Data model includes USAR complexity factors (1.0/1.5/1.8), sweep_time_gt formula preserved, PDF room data with exact dimensions
- [x] **Principle II - Multi-Floor Architecture**: ✅ Floor dataclass with independent configs, Stairwell entity with floor height and transition time calculations, vertical vs horizontal movement distinguished
- [x] **Principle III - Data-Driven Configuration**: ✅ Room properties from PDFs (manual transcription documented in research.md), configurable speeds via function parameters, complexity per room type
- [x] **Principle IV - Visualization Requirements**: ✅ 3-floor vertical stacking design (research.md Q2), 300 DPI output, room labels + times, door wedges, stairwell visual connectors
- [x] **Principle V - Algorithm Optimization**: ✅ Greedy 3D distance heuristic (research.md Q5), load-balanced strategy planned for P2, return-to-nearest-exit in contracts

**No design changes required** - Proceed to implementation phase (/speckit.tasks)

---

## Implementation Readiness

**Ready for /speckit.tasks**: ✅

All Phase 1 deliverables complete. The design satisfies:
- Technical feasibility (research.md validates all approaches)
- Data model completeness (5 entities with full validation rules)
- Interface clarity (simulation_interface.md defines contracts)
- User onboarding (quickstart.md provides 3-step guide)
- Constitutional compliance (all 5 principles satisfied)

Next command: `/speckit.tasks` to generate dependency-ordered implementation tasks
