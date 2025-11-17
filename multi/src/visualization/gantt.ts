// Mermaid Gantt chart generator - convert TimelineData to Mermaid syntax

import { TimelineData } from '../models/mission.js';

/**
 * Generate Mermaid Gantt chart syntax from timeline data
 * Output can be rendered using Mermaid CLI or pasted into mermaid.live
 */
export function generateMermaidGantt(timeline: TimelineData, title: string = 'Firefighter Patrol Mission'): string {
  const lines: string[] = [];

  // Gantt chart header
  lines.push('gantt');
  lines.push(`    title ${title}`);
  lines.push('    dateFormat X'); // Use milliseconds/seconds as timestamps
  lines.push('    axisFormat %S'); // Show seconds

  // Add sections for each agent
  for (const agent of timeline.agents) {
    lines.push('');
    lines.push(`    section ${agent.agentId}`);

    for (const activity of agent.activities) {
      const taskName = sanitizeMermaidLabel(activity.label);
      const start = Math.floor(activity.startTime);
      const end = Math.floor(activity.endTime);

      // Mermaid Gantt syntax: TaskName :status, id, start, duration
      // We use 'active' for ongoing tasks, 'done' for completed
      const status = getCriticalStatus(activity.type);
      const id = `${agent.agentId}_${start}`;

      lines.push(`    ${taskName} :${status}, ${id}, ${start}, ${end - start}s`);
    }
  }

  return lines.join('\n');
}

/**
 * Generate simplified text-based Gantt chart for terminal display
 */
export function generateTextGantt(timeline: TimelineData, width: number = 80): string {
  const lines: string[] = [];
  const duration = timeline.duration;
  const scale = (width - 20) / duration; // Reserve 20 chars for labels

  lines.push('Timeline Visualization:');
  lines.push('='.repeat(width));
  lines.push('');

  // Time ruler
  const ruler = 'Time: 0' + ' '.repeat(width - 20) + `${Math.floor(duration)}s`;
  lines.push(ruler);
  lines.push('-'.repeat(width));

  // Agent timelines
  for (const agent of timeline.agents) {
    const agentLabel = agent.agentId.padEnd(10);
    let timeline_str = agentLabel + '|';

    // Create character array for timeline
    const chars = new Array(width - 11).fill(' ');

    // Draw activities
    for (const activity of agent.activities) {
      const startPos = Math.floor(activity.startTime * scale);
      const endPos = Math.floor(activity.endTime * scale);
      const char = getActivityChar(activity.type);

      for (let i = startPos; i < endPos && i < chars.length; i++) {
        chars[i] = char;
      }
    }

    timeline_str += chars.join('');
    lines.push(timeline_str);
  }

  lines.push('='.repeat(width));
  lines.push('');
  lines.push('Legend:');
  lines.push('  █ = INSPECT (room inspection)');
  lines.push('  ▓ = MOVE (corridor traversal)');
  lines.push('  ▒ = ENTER/EXIT (room entry/exit)');
  lines.push('');

  // Add events
  if (timeline.events.length > 0) {
    lines.push('Events:');
    for (const event of timeline.events) {
      lines.push(`  [${Math.floor(event.time)}s] ${event.description}`);
    }
  }

  return lines.join('\n');
}

/**
 * Sanitize labels for Mermaid syntax (remove special characters)
 */
function sanitizeMermaidLabel(label: string): string {
  return label.replace(/[:#]/g, '').trim();
}

/**
 * Get Mermaid status for activity type
 */
function getCriticalStatus(type: string): string {
  switch (type) {
    case 'INSPECT':
      return 'crit'; // Critical task (red)
    case 'MOVE':
      return 'active'; // Active task (blue)
    case 'ENTER':
    case 'EXIT_ROOM':
      return 'done'; // Done task (green)
    default:
      return 'active';
  }
}

/**
 * Get character representation for activity type
 */
function getActivityChar(type: string): string {
  switch (type) {
    case 'INSPECT':
      return '█'; // Full block (critical)
    case 'MOVE':
      return '▓'; // Medium shade
    case 'ENTER':
    case 'EXIT_ROOM':
      return '▒'; // Light shade
    default:
      return '░';
  }
}
