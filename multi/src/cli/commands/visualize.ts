// Visualize command - generate timeline visualization from mission results

import { Command } from 'commander';
import chalk from 'chalk';
import { writeFileSync } from 'fs';
import { loadMissionOutput } from '../../io/output-formatter.js';
import { buildTimeline } from '../../simulation/timeline.js';
import { generateMermaidGantt, generateTextGantt } from '../../visualization/gantt.js';

const visualizeCommand = new Command('visualize')
  .description('Generate timeline visualization from mission results')
  .argument('<file>', 'Mission results JSON file')
  .option('-f, --format <type>', 'Output format: text, mermaid, or both (default: both)', 'both')
  .option('-o, --output <file>', 'Output file (default: timeline)', 'timeline')
  .option('-w, --width <chars>', 'Width for text visualization (default: 100)', '100')
  .action(async (file, options) => {
    try {
      console.log(chalk.blue('Generating timeline visualization...'));
      console.log();

      // Load mission results
      const results = loadMissionOutput(file) as any;
      console.log(chalk.gray(`Loaded mission: ${results.missionId}`));
      console.log(chalk.gray(`Routes: ${results.routes.length}`));
      console.log(chalk.gray(`Makespan: ${results.makespan}s`));
      console.log();

      // Build timeline
      const timeline = buildTimeline(results.routes);
      console.log(chalk.green(`✓ Timeline built with ${timeline.agents.length} agents`));
      console.log(chalk.gray(`  Duration: ${timeline.duration}s`));
      console.log(chalk.gray(`  Events: ${timeline.events.length}`));

      // Check for conflicts
      const hasConflicts = timeline.events.some((e) => e.description.includes('Conflict'));
      if (hasConflicts) {
        console.log(chalk.yellow('  ⚠ Room conflicts detected!'));
      }
      console.log();

      const format = options.format.toLowerCase();

      // Generate text visualization
      if (format === 'text' || format === 'both') {
        const width = parseInt(options.width);
        const textGantt = generateTextGantt(timeline, width);

        // Display in console
        console.log(chalk.blue('Text Timeline:'));
        console.log(textGantt);
        console.log();

        // Save to file
        const textFile = `${options.output}.txt`;
        writeFileSync(textFile, textGantt);
        console.log(chalk.green(`✓ Text visualization saved to ${textFile}`));
      }

      // Generate Mermaid visualization
      if (format === 'mermaid' || format === 'both') {
        const mermaidGantt = generateMermaidGantt(timeline, `Mission: ${results.missionId}`);

        // Save to .mmd file
        const mermaidFile = `${options.output}.mmd`;
        writeFileSync(mermaidFile, mermaidGantt);
        console.log(chalk.green(`✓ Mermaid diagram saved to ${mermaidFile}`));

        // Generate HTML wrapper for easy viewing
        const html = generateMermaidHTML(mermaidGantt, results.missionId);
        const htmlFile = `${options.output}.html`;
        writeFileSync(htmlFile, html);
        console.log(chalk.green(`✓ Interactive HTML saved to ${htmlFile}`));
        console.log(chalk.gray(`  Open ${htmlFile} in a browser to view the timeline`));
      }

      console.log();
      console.log(chalk.blue('Visualization complete!'));
    } catch (error) {
      console.error();
      console.error(chalk.red('Error:'), error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  });

/**
 * Generate standalone HTML file with Mermaid diagram
 */
function generateMermaidHTML(mermaidCode: string, title: string): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title} - Timeline Visualization</title>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            gantt: {
                titleTopMargin: 25,
                barHeight: 30,
                barGap: 8,
                topPadding: 50,
                leftPadding: 100,
                gridLineStartPadding: 35,
                fontSize: 12,
                numberSectionStyles: 4,
            }
        });
    </script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #2196f3;
            padding-bottom: 10px;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .legend {
            margin-top: 30px;
            padding: 15px;
            background-color: #f9f9f9;
            border-left: 4px solid #2196f3;
        }
        .legend h3 {
            margin-top: 0;
        }
        .legend-item {
            margin: 8px 0;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: 600;
            margin-right: 8px;
        }
        .badge-critical { background-color: #f44336; color: white; }
        .badge-active { background-color: #2196f3; color: white; }
        .badge-done { background-color: #4caf50; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚒 ${title}</h1>
        <div class="mermaid">
${mermaidCode}
        </div>
        <div class="legend">
            <h3>Legend</h3>
            <div class="legend-item">
                <span class="badge badge-critical">CRITICAL</span>
                Room Inspection (exclusive access required)
            </div>
            <div class="legend-item">
                <span class="badge badge-active">ACTIVE</span>
                Corridor Movement (parallel access allowed)
            </div>
            <div class="legend-item">
                <span class="badge badge-done">DONE</span>
                Room Entry/Exit
            </div>
        </div>
    </div>
</body>
</html>`;
}

export default visualizeCommand;
