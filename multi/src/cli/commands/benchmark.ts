// Benchmark command - compare algorithm performance

import { Command } from 'commander';
import chalk from 'chalk';
import { loadBuildingConfig } from '../../io/config-loader.js';
import { validateBuildingTopology } from '../../io/validator.js';
import { ilpAllocate } from '../../algorithms/allocation/ilp.js';
import { hungarianAllocate } from '../../algorithms/allocation/hungarian.js';
import { greedyAllocate } from '../../algorithms/allocation/greedy.js';

const benchmarkCommand = new Command('benchmark')
  .description('Compare performance of different allocation algorithms')
  .argument('<file>', 'Building configuration JSON file')
  .option('-a, --agents <count>', 'Number of firefighters (default: 2)', '2')
  .option('-r, --redundant <rooms>', 'Comma-separated room IDs requiring redundant inspection')
  .option('--runs <number>', 'Number of runs per algorithm (default: 5)', '5')
  .action(async (file, options) => {
    try {
      console.log(chalk.blue('🔬 Algorithm Performance Benchmark'));
      console.log();

      // Load and validate building
      console.log(chalk.gray(`Loading building configuration from ${file}...`));
      const building = loadBuildingConfig(file);

      const validationErrors = validateBuildingTopology(building);
      if (validationErrors.length > 0) {
        console.error(chalk.red('✗ Building validation failed:'));
        validationErrors.forEach((err) => {
          console.error(chalk.red(`  - ${err.field}: ${err.message}`));
        });
        process.exit(1);
      }

      // Configuration
      const agentCount = parseInt(options.agents);
      const startNode = building.entrances[0];
      const agents = Array.from({ length: agentCount }, (_, i) => ({
        id: `A${i + 1}`,
        startNode,
        speed: 1.0,
        label: `Agent ${i + 1}`,
      }));

      const redundantRooms = options.redundant
        ? options.redundant.split(',').map((s: string) => s.trim())
        : [];

      const runs = parseInt(options.runs);

      console.log(chalk.green('✓ Configuration loaded'));
      console.log(chalk.gray(`  Building: ${building.id}`));
      console.log(chalk.gray(`  Rooms: ${building.rooms.length}`));
      console.log(chalk.gray(`  Agents: ${agentCount}`));
      console.log(chalk.gray(`  Redundant rooms: ${redundantRooms.length}`));
      console.log(chalk.gray(`  Runs per algorithm: ${runs}`));
      console.log();

      // Benchmark results
      interface BenchmarkResult {
        algorithm: string;
        avgTime: number;
        minTime: number;
        maxTime: number;
        success: boolean;
        allocation?: any;
        error?: string;
      }

      const results: BenchmarkResult[] = [];

      // Benchmark Greedy Algorithm
      console.log(chalk.cyan('Testing Greedy Algorithm...'));
      let greedyTimes: number[] = [];
      let greedyAllocation: any;

      for (let i = 0; i < runs; i++) {
        const start = performance.now();
        greedyAllocation = greedyAllocate(agents, building.rooms, redundantRooms);
        const end = performance.now();
        greedyTimes.push(end - start);
      }

      results.push({
        algorithm: 'Greedy',
        avgTime: greedyTimes.reduce((a, b) => a + b) / runs,
        minTime: Math.min(...greedyTimes),
        maxTime: Math.max(...greedyTimes),
        success: true,
        allocation: greedyAllocation,
      });

      console.log(chalk.green(`  ✓ Completed ${runs} runs`));

      // Benchmark Hungarian Algorithm
      console.log(chalk.cyan('Testing Hungarian Algorithm...'));
      let hungarianTimes: number[] = [];
      let hungarianAllocation: any;

      for (let i = 0; i < runs; i++) {
        const start = performance.now();
        hungarianAllocation = hungarianAllocate(agents, building.rooms, redundantRooms);
        const end = performance.now();
        hungarianTimes.push(end - start);
      }

      results.push({
        algorithm: 'Hungarian',
        avgTime: hungarianTimes.reduce((a, b) => a + b) / runs,
        minTime: Math.min(...hungarianTimes),
        maxTime: Math.max(...hungarianTimes),
        success: true,
        allocation: hungarianAllocation,
      });

      console.log(chalk.green(`  ✓ Completed ${runs} runs`));

      // Benchmark ILP Algorithm
      console.log(chalk.cyan('Testing ILP Algorithm...'));
      let ilpTimes: number[] = [];
      let ilpAllocation: any;

      try {
        for (let i = 0; i < runs; i++) {
          const start = performance.now();
          ilpAllocation = await ilpAllocate(agents, building.rooms, redundantRooms);
          const end = performance.now();
          ilpTimes.push(end - start);
        }

        results.push({
          algorithm: 'ILP',
          avgTime: ilpTimes.reduce((a, b) => a + b) / runs,
          minTime: Math.min(...ilpTimes),
          maxTime: Math.max(...ilpTimes),
          success: true,
          allocation: ilpAllocation,
        });

        console.log(chalk.green(`  ✓ Completed ${runs} runs`));
      } catch (error) {
        results.push({
          algorithm: 'ILP',
          avgTime: 0,
          minTime: 0,
          maxTime: 0,
          success: false,
          error: error instanceof Error ? error.message : String(error),
        });

        console.log(chalk.yellow(`  ⚠ Failed: ${error instanceof Error ? error.message : String(error)}`));
      }

      // Display results
      console.log();
      console.log(chalk.blue('═'.repeat(80)));
      console.log(chalk.blue.bold('Benchmark Results'));
      console.log(chalk.blue('═'.repeat(80)));
      console.log();

      // Table header
      console.log(chalk.bold('Algorithm      Avg Time     Min Time     Max Time     Status'));
      console.log('─'.repeat(80));

      // Sort by average time
      results.sort((a, b) => a.avgTime - b.avgTime);

      for (const result of results) {
        const name = result.algorithm.padEnd(13);
        const avgTime = result.success
          ? `${result.avgTime.toFixed(2)}ms`.padEnd(12)
          : 'N/A'.padEnd(12);
        const minTime = result.success
          ? `${result.minTime.toFixed(2)}ms`.padEnd(12)
          : 'N/A'.padEnd(12);
        const maxTime = result.success
          ? `${result.maxTime.toFixed(2)}ms`.padEnd(12)
          : 'N/A'.padEnd(12);
        const status = result.success ? chalk.green('✓ Success') : chalk.red('✗ Failed');

        console.log(`${name} ${avgTime} ${minTime} ${maxTime} ${status}`);
      }

      console.log();

      // Recommendation
      const fastest = results.filter((r) => r.success)[0];
      if (fastest) {
        console.log(chalk.bold.green(`Recommendation: ${fastest.algorithm}`));
        console.log(chalk.gray(`  Fastest average execution time: ${fastest.avgTime.toFixed(2)}ms`));
      }

      console.log();

      // Allocation comparison
      console.log(chalk.blue('Allocation Details:'));
      console.log();

      for (const result of results) {
        if (result.success && result.allocation) {
          console.log(chalk.cyan(`${result.algorithm} Allocation:`));

          const assignments = result.allocation.assignments as Map<string, string[]>;
          assignments.forEach((rooms, agentId) => {
            console.log(`  ${agentId}: ${rooms.length} rooms (${rooms.join(', ')})`);
          });

          console.log();
        }
      }

    } catch (error) {
      console.error();
      console.error(chalk.red('Error:'), error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  });

export default benchmarkCommand;
