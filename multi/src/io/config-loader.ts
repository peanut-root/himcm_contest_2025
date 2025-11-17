// Building configuration loader with JSON schema validation

import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import * as fs from 'fs';
import * as path from 'path';
import { Building } from '../models/building.js';

const ajv = new Ajv({ allErrors: true });
addFormats(ajv);

// Load JSON schema from contracts directory
function loadBuildingSchema() {
  const schemaPath = path.join(process.cwd(), 'specs/001-firefighter-patrol-optimization/contracts/building-schema.json');
  if (fs.existsSync(schemaPath)) {
    const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf-8'));
    return schema;
  }
  // Fallback inline schema if file doesn't exist
  return {
    type: 'object',
    required: ['id', 'nodes', 'edges', 'rooms', 'entrances', 'exits'],
    properties: {
      id: { type: 'string', minLength: 1 },
      nodes: { type: 'array', minItems: 1 },
      edges: { type: 'array', minItems: 1 },
      rooms: { type: 'array', minItems: 1 },
      entrances: { type: 'array', minItems: 1 },
      exits: { type: 'array', minItems: 1 },
      metadata: { type: 'object' },
    },
  };
}

const buildingSchema = loadBuildingSchema();
const validateBuilding = ajv.compile(buildingSchema);

export function loadBuildingConfig(filePath: string): Building {
  try {
    const fileContent = fs.readFileSync(filePath, 'utf-8');
    const buildingData = JSON.parse(fileContent);

    // Validate against schema
    const valid = validateBuilding(buildingData);
    if (!valid) {
      const errors = validateBuilding.errors?.map((err) => `${err.instancePath} ${err.message}`).join(', ');
      throw new Error(`Building configuration validation failed: ${errors}`);
    }

    return buildingData as Building;
  } catch (error) {
    if (error instanceof SyntaxError) {
      throw new Error(`Invalid JSON in building configuration file: ${error.message}`);
    }
    throw error;
  }
}

export function saveBuildingConfig(building: Building, filePath: string): void {
  const valid = validateBuilding(building);
  if (!valid) {
    const errors = validateBuilding.errors?.map((err) => `${err.instancePath} ${err.message}`).join(', ');
    throw new Error(`Building configuration validation failed: ${errors}`);
  }

  fs.writeFileSync(filePath, JSON.stringify(building, null, 2), 'utf-8');
}
