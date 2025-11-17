// Validate command - validate building configuration or mission results

import { Command } from 'commander';
import chalk from 'chalk';
import { loadBuildingConfig } from '../../io/config-loader.js';
import { validateBuildingTopology } from '../../io/validator.js';
import { loadMissionOutput } from '../../io/output-formatter.js';

const validateCommand = new Command('validate')
  .description('Validate building configuration or mission results')
  .argument('<file>', 'File to validate (building config or mission results)')
  .option('-t, --type <type>', 'File type: building or mission (auto-detected if not specified)')
  .action(async (file, options) => {
    try {
      console.log(chalk.blue('Validating file...'));
      console.log();

      // Try to determine file type
      let fileType = options.type;
      if (!fileType) {
        // Auto-detect based on content
        try {
          const content = loadMissionOutput(file);
          if ('missionId' in content && 'makespan' in content) {
            fileType = 'mission';
          } else if ('nodes' in content && 'edges' in content && 'rooms' in content) {
            fileType = 'building';
          }
        } catch {
          fileType = 'building'; // Default
        }
      }

      if (fileType === 'building') {
        // Validate building configuration
        console.log(chalk.gray('Validating as building configuration...'));
        const building = loadBuildingConfig(file);
        console.log(chalk.green(`✓ Building ID: ${building.id}`));
        console.log(`  Nodes: ${building.nodes.length}`);
        console.log(`  Edges: ${building.edges.length}`);
        console.log(`  Rooms: ${building.rooms.length}`);

        const errors = validateBuildingTopology(building);

        if (errors.length === 0) {
          console.log();
          console.log(chalk.green('✓ Building configuration is valid!'));
        } else {
          console.log();
          console.error(chalk.red(`✗ Found ${errors.length} validation error(s):`));
          errors.forEach((err) => {
            console.error(chalk.red(`  - ${err.field}: ${err.message}`));
          });
          process.exit(1);
        }
      } else if (fileType === 'mission') {
        // Validate mission results
        console.log(chalk.gray('Validating as mission results...'));
        const results = loadMissionOutput(file) as any;

        console.log(chalk.green(`✓ Mission ID: ${results.missionId}`));
        console.log(`  Makespan: ${results.makespan}s`);
        console.log(`  Routes: ${results.routes?.length || 0}`);

        if (results.validation) {
          console.log();
          console.log(chalk.blue('Validation status:'));
          console.log(
            `  Overall: ${results.validation.valid ? chalk.green('✓ Valid') : chalk.red('✗ Invalid')}`
          );
          console.log(
            `  Coverage: ${results.validation.coverage?.allRoomsInspected ? chalk.green('✓') : chalk.red('✗')}`
          );
          console.log(
            `  Redundancy: ${results.validation.redundancy?.redundancySatisfied ? chalk.green('✓') : chalk.red('✗')}`
          );
          console.log(
            `  Conflicts: ${results.validation.conflicts?.noRoomConflicts ? chalk.green('✓') : chalk.red('✗')}`
          );

          if (results.validation.errors && results.validation.errors.length > 0) {
            console.log();
            console.error(chalk.red('Errors:'));
            results.validation.errors.forEach((err: string) => {
              console.error(chalk.red(`  - ${err}`));
            });
          }

          if (!results.validation.valid) {
            process.exit(1);
          }
        } else {
          console.log();
          console.log(chalk.yellow('⚠ No validation data found in results'));
        }
      } else {
        console.error(chalk.red(`Unknown file type: ${fileType}`));
        console.error('Use --type building or --type mission');
        process.exit(1);
      }
    } catch (error) {
      console.error();
      console.error(chalk.red('Error:'), error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  });

export default validateCommand;
