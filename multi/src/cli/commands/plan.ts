// Plan command - load building, configure mission, run planner, output results

import { Command } from 'commander';
import chalk from 'chalk';
import { loadBuildingConfig } from '../../io/config-loader.js';
import { validateBuildingTopology } from '../../io/validator.js';
import { saveMissionOutput } from '../../io/output-formatter.js';
import { SimulationEngine } from '../../simulation/engine.js';
import { MissionConfig } from '../../models/mission.js';

const planCommand = new Command('plan')
  .description('Generate optimal patrol routes for firefighters')
  .requiredOption('-b, --building <file>', 'Building configuration JSON file')
  .option('-a, --agents <count>', 'Number of firefighters (default: 2)', '2')
  .option('-s, --start <node>', 'Starting node ID (default: first entrance)')
  .option('-r, --redundant <rooms>', 'Comma-separated room IDs requiring redundant inspection')
  .option('--return-to-exit', 'Require firefighters to return to exit after inspection')
  .option('-o, --output <file>', 'Output file for results (default: results.json)', 'results.json')
  .option('--enter-time <seconds>', 'Time to enter room (default: 5)', '5')
  .option('--exit-time <seconds>', 'Time to exit room (default: 5)', '5')
  .option('--algorithm <type>', 'Allocation algorithm: ilp, hungarian, greedy (default: ilp)', 'ilp')
  .action(async (options) => {
    try {
      console.log(chalk.blue('🚒 Firefighter Patrol Optimization System'));
      console.log();

      // Load building configuration
      console.log(chalk.gray(`Loading building configuration from ${options.building}...`));
      const building = loadBuildingConfig(options.building);
      console.log(chalk.green(`✓ Loaded building: ${building.id}`));

      // Validate topology
      console.log(chalk.gray('Validating building topology...'));
      const validationErrors = validateBuildingTopology(building);
      if (validationErrors.length > 0) {
        console.error(chalk.red('✗ Building validation failed:'));
        validationErrors.forEach((err) => {
          console.error(chalk.red(`  - ${err.field}: ${err.message}`));
        });
        process.exit(1);
      }
      console.log(chalk.green('✓ Building topology valid'));

      // Create agent configuration
      const agentCount = parseInt(options.agents);
      const startNode = options.start || building.entrances[0];
      const agents = Array.from({ length: agentCount }, (_, i) => ({
        id: `A${i + 1}`,
        startNode,
        speed: 1.0,
        label: `Agent ${i + 1}`,
      }));

      // Parse redundant rooms
      const redundantRooms = options.redundant
        ? options.redundant.split(',').map((s: string) => s.trim())
        : [];

      // Create mission configuration
      const missionConfig: MissionConfig = {
        building,
        agents,
        redundantRooms,
        returnToExit: options.returnToExit || false,
        timeParameters: {
          enterTime: parseFloat(options.enterTime),
          exitTime: parseFloat(options.exitTime),
        },
      };

      console.log();
      console.log(chalk.blue('Mission Configuration:'));
      console.log(`  Agents: ${agentCount}`);
      console.log(`  Rooms: ${building.rooms.length}`);
      console.log(`  Redundant rooms: ${redundantRooms.length}`);
      console.log(`  Return to exit: ${missionConfig.returnToExit ? 'Yes' : 'No'}`);
      console.log();

      // Run planning
      console.log(chalk.gray('Planning routes...'));
      const engine = new SimulationEngine();
      const result = await engine.planFromConfig(missionConfig);

      // Display results
      console.log();
      console.log(chalk.green('✓ Planning complete!'));
      console.log();
      console.log(chalk.blue('Results:'));
      console.log(`  Makespan: ${result.makespan.toFixed(1)}s`);

      result.routes.forEach((route) => {
        console.log(
          `  ${route.agentId}: ${route.totalTime.toFixed(1)}s (rooms: ${route.roomsInspected.join(', ')})`
        );
      });

      console.log();
      console.log(chalk.blue('Validation:'));
      console.log(
        `  Coverage: ${result.validation.coverage.allRoomsInspected ? chalk.green('✓ Complete') : chalk.red('✗ Incomplete')}`
      );
      console.log(
        `  Redundancy: ${result.validation.redundancy.redundancySatisfied ? chalk.green('✓ Satisfied') : chalk.red('✗ Failed')}`
      );
      console.log(
        `  Conflicts: ${result.validation.conflicts.noRoomConflicts ? chalk.green('✓ None') : chalk.red('✗ Detected')}`
      );

      if (!result.validation.valid) {
        console.log();
        console.error(chalk.red('Validation errors:'));
        result.validation.errors.forEach((err) => {
          console.error(chalk.red(`  - ${err}`));
        });
      }

      // Save output
      console.log();
      console.log(chalk.gray(`Saving results to ${options.output}...`));
      saveMissionOutput(building.id, result, options.output);
      console.log(chalk.green(`✓ Results saved to ${options.output}`));
    } catch (error) {
      console.error();
      console.error(chalk.red('Error:'), error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  });

export default planCommand;
