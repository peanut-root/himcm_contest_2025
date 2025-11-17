# Quickstart Guide - Web Demonstration Application

**Feature**: Web Demonstration Application
**Branch**: `003-web-demo`
**Date**: 2025-11-12

---

## Overview

This guide explains how to run and develop the web demonstration application that visualizes pre-computed firefighter patrol routes.

**What it does**: Displays the 6-room office layout and animates firefighter agents moving along their optimized patrol routes with interactive playback controls.

**Technology**: Vanilla HTML/CSS/JavaScript (no frameworks, no build tools)

---

## Quick Start (5 minutes)

### Option 1: Open Directly in Browser

```bash
cd demo
open index.html  # macOS
# or
start index.html  # Windows
# or
xdg-open index.html  # Linux
```

**Note**: Some browsers block local file access. If the demo doesn't load data files, use Option 2 or 3.

### Option 2: Python HTTP Server

```bash
cd demo
python3 -m http.server 8000
```

Then open http://localhost:8000 in your browser.

### Option 3: Node.js HTTP Server

```bash
cd demo
npx http-server -p 8000
```

Then open http://localhost:8000 in your browser.

### Option 4: VS Code Live Server

1. Install the "Live Server" extension in VS Code
2. Right-click on `demo/index.html`
3. Select "Open with Live Server"

---

## Using the Demo

### Loading a Scenario

1. Use the **Scenario dropdown** in the top-right to select:
   - **Basic** - 2 agents, 6 rooms, simple patrol
   - **Redundancy** - 3 agents, 6 rooms, some rooms inspected twice
   - **Return to Exit** - 2 agents, 4 rooms, agents return to exits
   - **Multi-Agent** - 5 agents, 10 rooms, large facility

2. The building layout and metrics update automatically

### Controlling Animation

- **Play Button**: Start animating agent movements
- **Pause Button**: Freeze animation at current time
- **Restart Button**: Reset to beginning (time = 0)
- **Speed Slider**: Adjust from 0.5x (slow) to 3x (fast)
- **Timeline Scrubber**: Drag to jump to any point in the mission

### Understanding the Display

**Room Colors**:
- **Yellow**: Pending (not yet inspected)
- **Blue**: In Progress (agent currently inspecting)
- **Green**: Completed (inspection finished)

**Agents**:
- Colored circles with labels (A1, A2, etc.)
- Move along paths between rooms
- Tooltips show current action when paused

**Metrics Panel** (right side):
- **Makespan**: Total mission time (bottleneck agent)
- **Agent Times**: Individual completion times
- **Path Length**: Total distance traveled
- **Coverage**: Percentage of rooms inspected

---

## File Structure

```
demo/
├── index.html              # Main application page
├── styles/
│   └── main.css            # Styling (embedded in HTML)
├── scripts/
│   ├── building.js         # Renders 6-room layout
│   ├── animation.js        # Animates agents
│   ├── controls.js         # Play/pause/speed/scrub
│   └── metrics.js          # Displays statistics
├── data/
│   ├── building.json       # 6-room office layout
│   ├── results-basic.json  # Pre-computed scenario
│   ├── results-redundancy.json
│   ├── results-return.json
│   └── results-multi.json
└── README.md               # Overview and instructions
```

---

## Development Guide

### Prerequisites

- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+, or Edge 90+)
- Text editor (VS Code, Sublime, etc.)
- Optional: Local HTTP server for testing

### Making Changes

#### 1. Modify Layout (building.js)

To adjust room positions or sizes:

```javascript
// In building.js
const LAYOUT = {
  rooms: {
    R1: { x: 100, y: 50, width: 180, height: 120 },
    R2: { x: 300, y: 50, width: 180, height: 120 },
    // ...
  },
  hallway: { x: 50, y: 250, width: 700, height: 100 }
};
```

#### 2. Adjust Animation Speed (animation.js)

To change default speed or time scaling:

```javascript
// In animation.js
class AnimationController {
  constructor() {
    this.speed = 1.0;  // Default speed (1x)
    this.timeScale = 100;  // Milliseconds → pixels
  }
}
```

#### 3. Update Styling (main.css)

To change colors, fonts, or layout:

```css
/* In styles/main.css */
.room.pending { background-color: #ffd54f; }
.room.in-progress { background-color: #29b6f6; }
.room.completed { background-color: #66bb6a; }
```

#### 4. Add New Scenarios

To add a new pre-computed scenario:

1. Run the CLI tool to generate results:
   ```bash
   npm run cli -- plan -b examples/your-building.json -a 3 -o results.json
   ```

2. Copy results to demo data directory:
   ```bash
   cp results.json demo/data/results-your-scenario.json
   ```

3. Add to scenario dropdown in `index.html`:
   ```html
   <option value="your-scenario">Your Scenario Name</option>
   ```

4. Update scenario loader in `controls.js` to handle the new file

---

## Testing

### Manual Testing Checklist

**Basic Functionality**:
- [ ] Demo loads without errors in browser console
- [ ] Building layout displays with 6 rooms labeled R1-R6
- [ ] 2 exits visible on left and right
- [ ] Central hallway connects all rooms

**Animation**:
- [ ] Click "Play" starts agent movement
- [ ] Agents move smoothly (no jitter)
- [ ] Rooms change color when agents enter/exit
- [ ] Animation runs at approximately 30 FPS (smooth to the eye)

**Controls**:
- [ ] Pause button freezes agents mid-movement
- [ ] Restart button resets to time = 0
- [ ] Speed slider changes animation rate (test 0.5x, 1x, 3x)
- [ ] Timeline scrubber jumps to correct time when dragged

**Scenarios**:
- [ ] Each scenario loads successfully from dropdown
- [ ] Building updates to show correct number of agents
- [ ] Metrics panel updates with new makespan and stats
- [ ] No errors when switching between scenarios rapidly

**Metrics**:
- [ ] Makespan displays correct total time from JSON
- [ ] Individual agent times match route data
- [ ] Path length calculated correctly
- [ ] Coverage percentage shows 100% when complete

### Browser Compatibility

Test in these browsers:
- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (14+)
- Edge (latest)

---

## Troubleshooting

### Demo Won't Load Data Files

**Problem**: Console shows "Failed to fetch" or CORS errors

**Solution**: Use a local HTTP server (Option 2, 3, or 4 above) instead of opening the HTML file directly. Browsers block local file:// access for security.

### Animation is Choppy

**Problem**: Animation stutters or runs slowly

**Solutions**:
1. Close other browser tabs to free up resources
2. Reduce animation speed to 0.5x
3. Check console for JavaScript errors
4. Try a different browser (Chrome usually has best Canvas performance)

### Rooms Not Changing Color

**Problem**: Rooms stay yellow during animation

**Solutions**:
1. Check that results JSON file is loading (open console, look for errors)
2. Verify room IDs in results match room IDs in building.json
3. Ensure `updateAgents()` function is being called each frame
4. Check that agent actions have correct "location" fields

### Timeline Scrubber Not Working

**Problem**: Dragging timeline doesn't move agents

**Solutions**:
1. Pause the animation first (scrubbing while playing may conflict)
2. Check that timeline range matches the makespan from results
3. Verify `scrubTo(time)` function is called on slider input event
4. Look for JavaScript errors in console during scrubbing

### Metrics Not Updating

**Problem**: Metrics panel shows old/wrong values

**Solutions**:
1. Verify scenario loaded successfully (check network tab)
2. Ensure `updateMetrics()` is called after scenario change
3. Check that metrics JSON structure matches expected format
4. Refresh the page to clear any stale state

---

## Performance Tips

### Optimizing for Large Scenarios

If adding scenarios with 10+ agents:

1. **Reduce Canvas Size**: Smaller canvas = faster rendering
   ```javascript
   const canvas = document.getElementById('canvas');
   canvas.width = 600;  // Reduce from 800
   canvas.height = 450; // Reduce from 600
   ```

2. **Increase Frame Skip**: Update every N frames instead of every frame
   ```javascript
   let frameCount = 0;
   function animate() {
     if (frameCount++ % 2 === 0) {  // Skip every other frame
       updateAgents(currentTime);
       render();
     }
     requestAnimationFrame(animate);
   }
   ```

3. **Disable Shadows/Effects**: Remove any CSS shadows or blur effects

---

## Next Steps

After getting the demo running:

1. **Review the code** in `scripts/` to understand the architecture
2. **Customize the layout** to match your specific building configuration
3. **Add tooltips** by implementing hover events on rooms and agents
4. **Enhance metrics** by adding charts or graphs for visualizing performance
5. **Deploy** to GitHub Pages or Netlify for easy sharing

---

## Resources

- **HTML5 Canvas Tutorial**: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API
- **requestAnimationFrame Guide**: https://developer.mozilla.org/en-US/docs/Web/API/window/requestAnimationFrame
- **JavaScript Modules (ES6)**: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules

---

## Support

If you encounter issues:

1. Check the browser console for error messages
2. Verify all JSON files are valid (use a JSON validator)
3. Ensure you're using a modern browser (not IE11)
4. Try the demo on a different machine/browser to isolate the issue

For questions about the CLI tool or pre-computed results format, see the main project documentation in `docs/`.
