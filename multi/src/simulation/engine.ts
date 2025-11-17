// Simulation engine - orchestrates mission planning workflow

import { Mission, MissionConfig, MissionResult } from '../models/mission.js';
import { MissionPlanner } from './planner.js';

export class SimulationEngine {
  private planner: MissionPlanner;

  constructor() {
    this.planner = new MissionPlanner();
  }

  async executeMission(mission: Mission): Promise<Mission> {
    try {
      mission.status = 'PLANNING';

      const result = await this.planner.planMission(mission.config);

      mission.result = result;
      mission.status = 'COMPLETED';
      mission.completedAt = new Date();

      return mission;
    } catch (error) {
      mission.status = 'FAILED';
      mission.error = error instanceof Error ? error.message : String(error);
      mission.completedAt = new Date();

      throw error;
    }
  }

  async planFromConfig(config: MissionConfig): Promise<MissionResult> {
    return await this.planner.planMission(config);
  }
}
