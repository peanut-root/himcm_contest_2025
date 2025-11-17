# Technology Research - Web Demonstration Application

**Feature**: Web Demonstration Application
**Branch**: `002-web-demo`
**Date**: 2025-11-12
**Research Phase**: Phase 0

---

## Overview

This document resolves all technical clarifications identified in the implementation plan's Technical Context section. Research focused on selecting technologies that integrate well with the existing TypeScript 5.9 CLI codebase, support static deployment, and enable high-performance interactive visualization.

---

## 1. Canvas Rendering Library

### Decision

**Konva.js** (version 9.x)

### Rationale

- **API Design**: High-level, intuitive APIs specifically designed for interactive 2D graphics with nodes, shapes, and layers - perfect match for building/room/node visualization
- **Interactivity**: Excellent drag-and-drop, event handling, and user input support - critical for building editor
- **Built-in Features**: Native zoom/pan support, layer management, hit detection
- **TypeScript Support**: First-class TypeScript definitions with comprehensive IntelliSense
- **Animation Integration**: Built-in tweening system works well with GSAP for complex animations
- **Performance**: Efficient rendering for 20+ rooms and 10 agents target
- **Bundle Size**: ~75KB gzipped - reasonable for feature set

### Alternatives Considered

- **Pixi.js**: Rejected - WebGL-based, overkill for graph visualization, more complex API suited for games
- **Fabric.js**: Rejected - Better for image/text editing than node-based graph structures
- **Paper.js**: Rejected - Vector graphics focused, less optimized for interactive nodes/edges
- **Native Canvas API**: Rejected - Too low-level, would require extensive custom code for events and transforms

### Integration Notes

Konva integrates cleanly with existing TypeScript models:

```typescript
import Konva from 'konva';
import { Graph } from '../src/models/graph';

class BuildingCanvas {
  private stage: Konva.Stage;
  private buildingLayer: Konva.Layer;

  renderGraph(graph: Graph) {
    graph.forEachNode((id, attrs) => {
      const node = new Konva.Circle({
        x: attrs.x,
        y: attrs.y,
        radius: 10,
        fill: attrs.kind === 'EXIT' ? 'green' : 'blue',
        draggable: true
      });
      this.buildingLayer.add(node);
    });
  }
}
```

---

## 2. Animation Framework

### Decision

**GSAP (GreenSock Animation Platform)** version 3.12+

### Rationale

- **Performance**: Industry-leading animation performance, consistently 60fps with GPU acceleration
- **Timeline System**: Perfect for coordinating multi-agent movements with precise timing
- **Playback Controls**: Built-in `play()`, `pause()`, `reverse()`, `progress()`, `timeScale()` for scrubbing
- **Path Animation**: MotionPath plugin animates objects along custom paths - ideal for patrol routes
- **TypeScript Support**: Excellent type definitions, full IntelliSense
- **Konva Integration**: Works seamlessly with Konva shape properties
- **Licensing**: Free for web usage (including commercial)
- **Bundle Size**: Core ~47KB gzipped, modular architecture

### Alternatives Considered

- **Anime.js**: Rejected - Lighter (6KB) but lacks sophisticated timeline system and advanced playback controls
- **requestAnimationFrame**: Rejected - Too low-level, requires custom easing and timeline management
- **CSS Animations**: Rejected - Poor programmatic control, limited canvas integration

### Integration Notes

GSAP timelines map directly to Route actions:

```typescript
import gsap from 'gsap';
import type { Route, AgentAction } from '../src/models/route';

class RouteAnimator {
  private timeline: gsap.core.Timeline;

  animateRoute(route: Route, shape: Konva.Shape) {
    this.timeline = gsap.timeline({ paused: true });

    route.actions.forEach((action: AgentAction) => {
      if (action.type === 'MOVE') {
        this.timeline.to(shape, {
          duration: action.duration / 1000,
          x: action.targetX,
          y: action.targetY
        });
      }
    });

    return {
      play: () => this.timeline.play(),
      pause: () => this.timeline.pause(),
      scrub: (progress: number) => this.timeline.progress(progress)
    };
  }
}
```

---

## 3. UI Component Library

### Decision

**Native HTML/CSS with TypeScript** (optional **Lit** for complex components)

### Rationale

- **Zero Overhead**: No framework bundle size for forms, buttons, panels
- **Modern CSS**: Grid, Flexbox, Custom Properties handle layouts elegantly
- **TypeScript Classes**: Clean component encapsulation without framework complexity
- **Progressive Enhancement**: Start native, add Lit (~6KB) only if complexity justifies
- **Control**: Full control over DOM, no framework opinions or constraints
- **Static Deployment**: No SSR, hydration, or build complexity

### Alternatives Considered

- **React/Vue/Svelte**: Rejected - Unnecessary for single demo page, 30-100KB+ overhead, complex build
- **Tailwind CSS**: Rejected - Overkill for focused demo, adds build steps
- **Web Component Libraries** (Shoelace, FAST): Rejected - Premature, build custom first

### Integration Notes

TypeScript class-based components with native DOM:

```typescript
class ControlPanel {
  private container: HTMLElement;

  constructor(container: HTMLElement, callbacks: {
    onPlay: () => void;
    onPause: () => void;
  }) {
    this.container = container;
    this.render(callbacks);
  }

  private render(callbacks: any) {
    this.container.innerHTML = `
      <div class="control-panel">
        <button id="play-btn">Play</button>
        <button id="pause-btn">Pause</button>
      </div>
    `;

    this.container.querySelector('#play-btn')
      ?.addEventListener('click', callbacks.onPlay);
  }
}
```

Optional Lit for reactive components:

```typescript
import { LitElement, html } from 'lit';
import { customElement, property } from 'lit/decorators.js';

@customElement('metrics-panel')
class MetricsPanel extends LitElement {
  @property({ type: Number }) makespan = 0;

  render() {
    return html`<div>Makespan: ${this.makespan}s</div>`;
  }
}
```

---

## 4. Build Tool

### Decision

**Vite** version 5.x

### Rationale

- **TypeScript Native**: Zero-config TypeScript via esbuild (10-100x faster than tsc)
- **Static Site Generation**: Build mode generates optimized static assets
- **Fast Development**: Instant HMR, server starts in ~200ms
- **Tree-Shaking**: Uses Rollup for production, ensures minimal bundles
- **Asset Handling**: Built-in support for JSON, images, fonts
- **Module Resolution**: Path aliases for importing CLI source code
- **Future-Proof**: Adopted by major frameworks, active development
- **Developer Experience**: Excellent error messages, build analysis

### Alternatives Considered

- **esbuild**: Rejected - Lacks dev server, HMR, plugin ecosystem
- **Rollup**: Rejected - Slower dev experience, more configuration
- **Webpack**: Rejected - Complex configuration, slower builds, overkill

### Integration Notes

Vite configuration with path aliases to reuse CLI code:

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  root: './web',
  build: {
    outDir: '../dist-web',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'web/index.html')
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@algorithms': resolve(__dirname, 'src/algorithms'),
      '@models': resolve(__dirname, 'src/models')
    }
  },
  optimizeDeps: {
    include: ['graphology', 'javascript-lp-solver']
  }
});
```

Project structure:
```
himcm/
├── src/              # Existing CLI (shared)
├── web/              # New web demo
│   ├── index.html
│   ├── main.ts
│   └── components/
├── dist/             # CLI build output
├── dist-web/         # Web build output
└── vite.config.ts
```

---

## 5. Testing Framework

### Decision

**Vitest** (unit/integration) + **Playwright** (E2E)

### Rationale

**Vitest**:
- **Vite-Native**: Zero config, shares Vite plugins and settings
- **Fast**: 2-10x faster than Jest via esbuild transformation
- **TypeScript Native**: Works out-of-box with TS 5.9
- **Jest-Compatible**: Familiar API, easy migration
- **Browser Mode**: New stable feature for component testing
- **Built-in Coverage**: Istanbul/V8 without extra config

**Playwright**:
- **Browser Automation**: Test complete workflows (load → optimize → animate)
- **Cross-Browser**: Chrome, Firefox, Safari from single codebase
- **Visual Regression**: Built-in screenshot comparison
- **Debugging**: Time-travel debugging, trace viewer
- **TypeScript First-Class**: Excellent type support
- **Parallel Execution**: Fast CI/CD test runs

**Why Both**: Clear separation - Vitest for logic (algorithms, services), Playwright for UI flows

### Alternatives Considered

- **Jest**: Rejected - Slower than Vitest, requires extra TS config
- **Cypress**: Rejected - Heavier than Playwright, limited browser support
- **Playwright Alone**: Rejected - Too slow for unit tests

### Integration Notes

Vitest config merging with Vite:

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import { mergeConfig } from 'vite';
import viteConfig from './vite.config';

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      globals: true,
      environment: 'jsdom',
      coverage: {
        provider: 'v8',
        reporter: ['text', 'html']
      }
    }
  })
);
```

Unit test example:

```typescript
import { describe, it, expect } from 'vitest';
import { BuildingService } from './services/BuildingService';

describe('BuildingService', () => {
  it('should validate building topology', () => {
    const service = new BuildingService();
    const result = service.validate(testBuilding);
    expect(result.valid).toBe(true);
  });
});
```

E2E test example:

```typescript
import { test, expect } from '@playwright/test';

test('should animate patrol route', async ({ page }) => {
  await page.goto('/');
  await page.selectOption('#building-select', 'basic-6-room');
  await page.click('#play-button');

  const agent = page.locator('.agent-A1');
  const initialPos = await agent.boundingBox();

  await page.waitForTimeout(1000);
  const newPos = await agent.boundingBox();

  expect(initialPos?.x).not.toBe(newPos?.x);
});
```

---

## Technology Stack Summary

| Category | Technology | Bundle Size | Justification |
|----------|-----------|-------------|---------------|
| Canvas Rendering | Konva.js 9.x | ~75KB gzipped | Interactive graph visualization, drag-and-drop, zoom/pan |
| Animation | GSAP 3.12+ | ~47KB gzipped | Timeline system, playback controls, path animation |
| UI Components | Native HTML/CSS + TypeScript | 0KB (Lit: ~6KB optional) | Minimal overhead, full control |
| Build Tool | Vite 5.x | N/A (dev tool) | Fast dev server, TypeScript native, static output |
| Testing | Vitest + Playwright | N/A (dev tools) | Fast unit tests, comprehensive E2E |

**Total Additional Bundle**: ~122KB gzipped (excluding existing CLI algorithms)

---

## Code Reuse Strategy

The web application will import and reuse existing CLI code:

```typescript
// Reuse existing models
import { Node, Edge, Room, Agent } from '@models/building';
import { Mission, MissionConfig } from '@models/mission';
import { Route, AgentAction } from '@models/route';
import { Graph } from '@models/graph';

// Reuse existing algorithms
import { aStarPathfinding } from '@algorithms/pathfinding/astar';
import { ilpAllocate } from '@algorithms/allocation/ilp';
import { hungarianAllocate } from '@algorithms/allocation/hungarian';
import { validateCoverage } from '@algorithms/validation/coverage';
import { detectRoomConflicts } from '@algorithms/validation/conflicts';

// Reuse existing simulation
import { MissionPlanner } from '@/simulation/planner';
import { buildTimeline } from '@/simulation/timeline';

// Reuse existing validation
import { validateBuilding } from '@/io/validator';
```

**Benefits**:
- Single source of truth for algorithms
- Guaranteed CLI compatibility
- No code duplication
- Shared TypeScript types

---

## Development Workflow

### Setup Phase
1. Install dependencies: `npm install konva gsap vite vitest playwright`
2. Create `web/` directory structure
3. Configure Vite with path aliases to `src/`
4. Set up TypeScript config extending base `tsconfig.json`

### Development Phase
1. Run Vite dev server: `npm run dev` (hot reload)
2. Implement canvas visualization with Konva
3. Add GSAP animation layer
4. Build native HTML/CSS UI components
5. Write Vitest unit tests alongside features

### Testing Phase
1. Run unit tests: `npm run test` (Vitest watch mode)
2. Run E2E tests: `npm run test:e2e` (Playwright)
3. Check coverage: `npm run coverage`

### Build Phase
1. Build production bundle: `npm run build`
2. Preview: `npm run preview`
3. Deploy `dist-web/` to static host (GitHub Pages, Netlify, Vercel)

---

## Risk Mitigation

### Performance Concerns
- **Risk**: Animation lag with 10 agents
- **Mitigation**: GSAP GPU acceleration, Konva layer caching, requestAnimationFrame throttling

### Bundle Size
- **Risk**: Excessive bundle size
- **Mitigation**: Vite tree-shaking, lazy loading for non-critical features, bundle analysis

### Browser Compatibility
- **Risk**: Older browsers fail
- **Mitigation**: Target modern browsers only (documented in requirements), polyfills if needed

### CLI Compatibility
- **Risk**: Web app produces incompatible JSON
- **Mitigation**: Reuse existing validators, automated tests comparing CLI vs Web output

---

## Next Steps

With technology decisions resolved, proceed to:
1. **Phase 1 Design**: Create data model, contracts, and quickstart guide
2. **Implementation**: Begin with User Story 1 (P1) - Interactive Building Configuration
3. **Validation**: Ensure all constitution checks pass post-design

**Research Complete**: All NEEDS CLARIFICATION items resolved. Ready for Phase 1 design artifacts.
