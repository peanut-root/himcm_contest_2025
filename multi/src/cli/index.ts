#!/usr/bin/env node
// CLI entry point

import { Command } from 'commander';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readFileSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const packageJsonPath = join(__dirname, '../../package.json');
const packageJson = JSON.parse(readFileSync(packageJsonPath, 'utf-8'));

const program = new Command();

program
  .name('firefighter-patrol')
  .description('Firefighter patrol route optimization system')
  .version(packageJson.version);

// Import and register commands
async function main() {
  const planModule = await import('./commands/plan.js');
  program.addCommand(planModule.default);

  const validateModule = await import('./commands/validate.js');
  program.addCommand(validateModule.default);

  const visualizeModule = await import('./commands/visualize.js');
  program.addCommand(visualizeModule.default);

  const benchmarkModule = await import('./commands/benchmark.js');
  program.addCommand(benchmarkModule.default);

  // Parse arguments
  await program.parseAsync(process.argv);
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
