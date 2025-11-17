# Quickstart Guide - Web Demonstration Application

**Feature**: Web Demonstration Application
**Branch**: `002-web-demo`
**Date**: 2025-11-12
**Phase**: Phase 1 Design

---

## Overview

This guide helps developers quickly understand and implement the web demonstration application. It covers setup, architecture, and implementation priorities.

---

## 1. Quick Setup (5 minutes)

### Install Dependencies

```bash
cd /Users/ralph/Documents/FreeType/himcm

# Install web-specific dependencies
npm install --save konva gsap
npm install --save-dev vite vitest playwright @playwright/test
```

### Configure Vite

Create `vite.config.ts`:

```typescript
import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  root: './web',
  build: {
    outDir: '../dist-web',
    emptyOutDir: true
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@models': resolve(__dirname, 'src/models'),
      '@algorithms': resolve(__dirname, 'src/algorithms'),
      '@simulation': resolve(__dirname, 'src/simulation')
    }
  }
});
```

### Create Web Directory Structure

```bash
mkdir -p web/src/{components/{canvas,animation,forms,panels,toolbar},services,models,utils}
mkdir -p web/assets/{examples,styles}
mkdir -p web/tests/{canvas,animation,integration}
```

### Create Entry Point

Create `web/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Firefighter Patrol Route Optimizer - Demo</title>
  <link rel="stylesheet" href="/assets/styles/main.css">
</head>
<body>
  <div id="app">
    <div id="toolbar"></div>
    <div id="canvas-container"></div>
    <div id="control-panel"></div>
    <div id="metrics-panel"></div>
  </div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

Create `web/src/main.ts`:

```typescript
import Konva from 'konva';
import { BuildingService } from './services/BuildingService';
import { ExampleService } from './services/ExampleService';
import { CanvasService } from './services/CanvasService';

console.log('Firefighter Patrol Optimizer - Web Demo');

// Initialize services
const buildingService = new BuildingService();
const exampleService = new ExampleService();
const canvasService = new CanvasService();

// Load example and render
(async () => {
  const scenario = await exampleService.loadExample('basic-6-room');
  const container = document.getElementById('canvas-container') as HTMLDivElement;
  canvasService.initialize(container, scenario.building);
  canvasService.renderBuilding(scenario.building);
})();
```

### Add NPM Scripts

Update `package.json`:

```json
{
  "scripts": {
    "dev": "vite",
    "dev:web": "vite",
    "build:web": "vite build",
    "preview:web": "vite preview",
    "test:web": "vitest",
    "test:e2e": "playwright test"
  }
}
```

### Run Dev Server

```bash
npm run dev
# Open browser to http://localhost:5173
```

---

## 2. Architecture Overview

### Layer Structure

```
┌─────────────────────────────────────────┐
│           UI Components                 │
│  (Konva Canvas, Forms, Panels)          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Service Layer                   │
│  (Building, Optimization, Animation)    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Existing CLI Algorithms            │
│  (A*, ILP, Hungarian, Validators)       │
└─────────────────────────────────────────┘
```

### Key Design Decisions

1. **Reuse CLI Code**: Import existing algorithms, don't duplicate
2. **Service Layer**: Stateless facades encapsulating business logic
3. **Static Deployment**: No backend, runs entirely in browser
4. **Component Composition**: Build UI from small, testable components
5. **Type Safety**: Strict TypeScript throughout

---

## 3. Implementation Priority (4 User Stories)

### Phase 1: P1 - Interactive Building Configuration (Priority 1)

**Goal**: Users can design buildings visually

**Tasks** (in order):
1. Implement `BuildingService` (CRUD operations)
2. Implement `CanvasService` (Konva rendering)
3. Create `NodeRenderer`, `EdgeRenderer`, `RoomRenderer` components
4. Create `DrawingTools` toolbar
5. Implement click-to-add nodes
6. Implement drag-to-connect edges
7. Implement `PropertyEditor` for editing node/edge/room properties
8. Add validation feedback
9. Implement export to JSON

**Success Criteria**:
- User can create 6-room building in <5 minutes
- Export JSON matches CLI schema
- Validation errors shown visually

### Phase 2: P2 - Visualize Optimization Results (Priority 2)

**Goal**: Users see animated agent movements

**Tasks** (in order):
1. Implement `OptimizationService` (trigger CLI planner)
2. Implement `AnimationService` (GSAP timelines)
3. Create `AnimatedAgent` renderer
4. Create `AnimationController` (play/pause/speed)
5. Implement agent movement along paths
6. Add room state visualization (pending/in-progress/completed)
7. Implement conflict highlighting
8. Create `MetricsPanel` to display performance metrics
9. Add `TimelineView` for scrubbing

**Success Criteria**:
- Animation runs at 30 FPS
- Users understand results in <30 seconds
- Conflicts highlighted in red

### Phase 3: P3 - Configure and Run Missions (Priority 3)

**Goal**: Users configure missions through forms

**Tasks** (in order):
1. Create `MissionForm` component
2. Implement agent count input
3. Implement start location dropdown
4. Create `RoomSelector` for redundant rooms
5. Add return-to-exit checkbox
6. Add algorithm selector (ILP/Hungarian/Greedy)
7. Implement "Optimize" button with progress indicator
8. Handle optimization errors gracefully
9. Transition to animation view on success

**Success Criteria**:
- 90% users run first optimization without errors
- Clear error messages with suggestions
- Progress indicator for long optimizations

### Phase 4: P4 - Load and Save Scenarios (Priority 4)

**Goal**: Users save/load scenarios

**Tasks** (in order):
1. Implement `StorageService` (LocalStorage)
2. Create `ScenarioPanel` component
3. Implement save scenario dialog
4. Implement load scenario list
5. Add 4 example scenarios to `assets/examples/`
6. Implement `ExampleService` to load examples
7. Add scenario metadata (name, description, tags)
8. Implement delete scenario
9. Add storage usage indicator

**Success Criteria**:
- Scenarios persist across sessions
- 4 example scenarios available
- Storage usage visible

---

## 4. Code Examples

### Example 1: Implement BuildingService

```typescript
// web/src/services/BuildingService.ts
import { Building, Node, Edge, Room } from '@models/building';
import { validateBuilding } from '@/io/validator';
import type { ValidationResult } from '@/io/validator';

export class BuildingService {
  createEmptyBuilding(name: string): Building {
    return {
      id: crypto.randomUUID(),
      name,
      nodes: [],
      edges: [],
      rooms: []
    };
  }

  addNode(building: Building, node: Omit<Node, 'id'>): Node {
    const newNode: Node = {
      ...node,
      id: `node-${crypto.randomUUID()}`
    };
    building.nodes.push(newNode);
    return newNode;
  }

  validate(building: Building): ValidationResult {
    return validateBuilding(building);
  }

  exportToJSON(building: Building): string {
    return JSON.stringify(building, null, 2);
  }
}
```

### Example 2: Render Building with Konva

```typescript
// web/src/services/CanvasService.ts
import Konva from 'konva';
import { Building, Node } from '@models/building';

export class CanvasService {
  private stage: Konva.Stage;
  private buildingLayer: Konva.Layer;

  initialize(container: HTMLDivElement, building: Building): Konva.Stage {
    this.stage = new Konva.Stage({
      container,
      width: window.innerWidth,
      height: window.innerHeight,
      draggable: true
    });

    this.buildingLayer = new Konva.Layer();
    this.stage.add(this.buildingLayer);

    return this.stage;
  }

  renderBuilding(building: Building): void {
    this.buildingLayer.destroyChildren();

    // Render nodes
    building.nodes.forEach(node => {
      const circle = new Konva.Circle({
        id: node.id,
        x: node.x,
        y: node.y,
        radius: 15,
        fill: this.getNodeColor(node.kind),
        stroke: '#000',
        strokeWidth: 2,
        draggable: true
      });

      circle.on('dragend', () => {
        node.x = circle.x();
        node.y = circle.y();
      });

      this.buildingLayer.add(circle);
    });

    // Render edges
    building.edges.forEach(edge => {
      const fromNode = building.nodes.find(n => n.id === edge.from);
      const toNode = building.nodes.find(n => n.id === edge.to);

      if (fromNode && toNode) {
        const line = new Konva.Arrow({
          points: [fromNode.x, fromNode.y, toNode.x, toNode.y],
          stroke: '#666',
          strokeWidth: 2,
          fill: '#666',
          pointerLength: 10,
          pointerWidth: 10
        });

        this.buildingLayer.add(line);
      }
    });

    this.buildingLayer.batchDraw();
  }

  private getNodeColor(kind: string): string {
    switch (kind) {
      case 'EXIT': return '#4caf50';
      case 'CORRIDOR': return '#2196f3';
      case 'DOOR': return '#ff9800';
      default: return '#999';
    }
  }
}
```

### Example 3: Animate Agent Movement

```typescript
// web/src/services/AnimationService.ts
import gsap from 'gsap';
import Konva from 'konva';
import { OptimizationResults, Route, AgentAction } from '@models/route';

export class AnimationService {
  private timeline: gsap.core.Timeline;
  private agents: Map<string, Konva.Circle> = new Map();

  initialize(results: OptimizationResults, layer: Konva.Layer) {
    this.timeline = gsap.timeline({ paused: true });

    // Create agent shapes
    results.routes.forEach((route, index) => {
      const agent = new Konva.Circle({
        radius: 10,
        fill: this.getAgentColor(index),
        stroke: '#000',
        strokeWidth: 1
      });

      layer.add(agent);
      this.agents.set(route.agentId, agent);

      // Add actions to timeline
      this.buildAgentTimeline(route, agent);
    });

    layer.batchDraw();
  }

  private buildAgentTimeline(route: Route, shape: Konva.Circle) {
    route.actions.forEach(action => {
      if (action.type === 'MOVE') {
        this.timeline.to(shape, {
          duration: action.duration / 1000,
          x: action.targetX,  // You'll need to look up node coordinates
          y: action.targetY,
          ease: 'none'
        }, action.startTime / 1000);
      }
    });
  }

  play() {
    this.timeline.play();
  }

  pause() {
    this.timeline.pause();
  }

  seek(time: number) {
    this.timeline.seek(time / 1000);
  }

  private getAgentColor(index: number): string {
    const colors = ['#f44336', '#2196f3', '#4caf50', '#ff9800', '#9c27b0'];
    return colors[index % colors.length];
  }
}
```

---

## 5. Testing Strategy

### Unit Tests (Vitest)

Test services in isolation:

```typescript
// web/tests/services/BuildingService.test.ts
import { describe, it, expect } from 'vitest';
import { BuildingService } from '../../src/services/BuildingService';

describe('BuildingService', () => {
  const service = new BuildingService();

  it('should create empty building', () => {
    const building = service.createEmptyBuilding('Test Building');
    expect(building.name).toBe('Test Building');
    expect(building.nodes).toHaveLength(0);
  });

  it('should add node with generated ID', () => {
    const building = service.createEmptyBuilding('Test');
    const node = service.addNode(building, {
      kind: 'EXIT',
      x: 100,
      y: 100
    });

    expect(node.id).toBeDefined();
    expect(building.nodes).toHaveLength(1);
  });

  it('should validate building topology', () => {
    const building = service.createEmptyBuilding('Test');
    const validation = service.validate(building);

    expect(validation.valid).toBe(false);
    expect(validation.errors).toContain('No EXIT nodes found');
  });
});
```

### E2E Tests (Playwright)

Test full user workflows:

```typescript
// web/tests/e2e/building-editor.spec.ts
import { test, expect } from '@playwright/test';

test('should create building and add nodes', async ({ page }) => {
  await page.goto('/');

  // Click "New Building"
  await page.click('button:has-text("New Building")');

  // Enter building name
  await page.fill('#building-name', 'Test Office');
  await page.click('button:has-text("Create")');

  // Add exit node
  await page.click('button[data-tool="add-exit"]');
  await page.click('#canvas-container', { position: { x: 200, y: 200 } });

  // Verify node appears
  const node = page.locator('.konvajs-content circle').first();
  await expect(node).toBeVisible();

  // Validate
  await page.click('button:has-text("Validate")');
  await expect(page.locator('.notification.success')).toBeVisible();
});
```

---

## 6. Development Workflow

### Daily Workflow

```bash
# Start dev server
npm run dev

# In another terminal, run tests in watch mode
npm run test:web

# Make changes, tests re-run automatically
# Browser hot-reloads automatically
```

### Before Commit

```bash
# Run all tests
npm run test:web
npm run test:e2e

# Build production bundle
npm run build:web

# Check bundle size
ls -lh dist-web/assets/*.js
```

### Debugging

- **Browser DevTools**: Use React DevTools or Vue DevTools if using framework
- **Konva Inspector**: `console.log(stage.toJSON())` to inspect canvas state
- **GSAP DevTools**: Use GSDevTools plugin for timeline debugging
- **Vitest UI**: Run `npx vitest --ui` for interactive test debugging

---

## 7. Common Patterns

### Pattern 1: Update UI on State Change

```typescript
class AppState {
  private observers: Array<() => void> = [];

  subscribe(callback: () => void): () => void {
    this.observers.push(callback);
    return () => {
      const index = this.observers.indexOf(callback);
      this.observers.splice(index, 1);
    };
  }

  private notify() {
    this.observers.forEach(cb => cb());
  }

  updateBuilding(building: Building) {
    this.building = building;
    this.notify();
  }
}

// Usage
appState.subscribe(() => {
  canvasService.renderBuilding(appState.building);
});
```

### Pattern 2: Service Composition

```typescript
class OptimizationWorkflow {
  constructor(
    private buildingService: BuildingService,
    private validationService: ValidationService,
    private optimizationService: OptimizationService
  ) {}

  async run(config: MissionConfig): Promise<OptimizationResults> {
    // Step 1: Validate building
    const buildingValidation = this.validationService.validateBuilding(config.building);
    if (!buildingValidation.valid) {
      throw new Error('Invalid building');
    }

    // Step 2: Validate mission config
    const missionValidation = this.validationService.validateMissionConfig(config);
    if (!missionValidation.valid) {
      throw new Error('Invalid mission configuration');
    }

    // Step 3: Run optimization
    const results = await this.optimizationService.optimize(config);

    return results;
  }
}
```

### Pattern 3: Error Boundaries

```typescript
class ServiceError extends Error {
  constructor(
    public code: string,
    message: string,
    public context?: any
  ) {
    super(message);
  }
}

// Usage
try {
  await optimizationService.optimize(config);
} catch (error) {
  if (error instanceof ServiceError) {
    if (error.code === 'INFEASIBLE') {
      showNotification('No solution found', 'error');
    }
  } else {
    console.error('Unexpected error:', error);
    showNotification('An error occurred', 'error');
  }
}
```

---

## 8. Performance Tips

### Konva Optimization

```typescript
// Use layer caching for static elements
buildingLayer.cache();

// Batch updates
layer.batchDraw();  // Instead of layer.draw() multiple times

// Destroy unused shapes
shape.destroy();

// Use shapes instead of images for better performance
// Avoid filters on frequently updated shapes
```

### Animation Optimization

```typescript
// Use GSAP's automatic GPU acceleration
gsap.set(shape, { force3D: true });

// Limit simultaneous animations
// Use timeline instead of individual tweens

// Throttle high-frequency events
const throttledUpdate = throttle(() => {
  updateUI();
}, 16);  // ~60fps
```

### Bundle Size Optimization

```typescript
// Import only what you need
import { Circle, Layer } from 'konva/lib/shapes';  // Instead of full Konva

// Use dynamic imports for heavy features
const { OptimizationService } = await import('./services/OptimizationService');

// Check bundle analysis
npm run build:web -- --mode analyze
```

---

## 9. Troubleshooting

### Issue: Konva canvas not rendering

**Solution**: Ensure container has explicit width/height:

```css
#canvas-container {
  width: 100vw;
  height: 100vh;
}
```

### Issue: GSAP timeline not playing

**Solution**: Check timeline is not paused:

```typescript
timeline.paused(false);
timeline.play();
```

### Issue: Import errors from CLI code

**Solution**: Check Vite alias configuration:

```typescript
resolve: {
  alias: {
    '@': resolve(__dirname, 'src')
  }
}
```

### Issue: LocalStorage quota exceeded

**Solution**: Compress scenarios or limit saved count:

```typescript
if (error.name === 'QuotaExceededError') {
  // Delete oldest scenarios
  const scenarios = storageService.listScenarios();
  scenarios.slice(-5).forEach(s => storageService.deleteScenario(s.id));
}
```

---

## 10. Next Steps

After completing quickstart:

1. **Read data-model.md** - Understand data structures
2. **Read contracts/services.md** - Understand service interfaces
3. **Read spec.md** - Review full requirements
4. **Start with P1** - Implement Interactive Building Configuration
5. **Write tests** - Add unit tests as you implement
6. **Iterate** - Deploy to GitHub Pages, gather feedback

---

## Resources

- **Konva Docs**: https://konvajs.org/docs/
- **GSAP Docs**: https://greensock.com/docs/
- **Vite Guide**: https://vitejs.dev/guide/
- **Vitest Docs**: https://vitest.dev/
- **Playwright Docs**: https://playwright.dev/

**Estimated Time to First Prototype**: 2-3 days for P1 (building editor)
**Estimated Time to Full MVP**: 1-2 weeks for all 4 user stories

Happy coding! 🚀
