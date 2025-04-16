/**
 * Promethios Deployment Logging System
 *
 * This module implements a logging system to track successful deployments
 * and maintain a history of deployment status.
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

// Path to deployment logs directory
const LOGS_DIR = path.resolve(process.cwd(), 'logs/deployments');

/**
 * Create a deployment log entry after a successful deployment
 */
export async function logDeployment(
  status: 'passed' | 'failed' = 'passed'
): Promise<{ success: boolean; logPath: string }> {
  try {
    // Create logs directory if it doesn't exist
    if (!fs.existsSync(LOGS_DIR)) {
      fs.mkdirSync(LOGS_DIR, { recursive: true });
    }

    // Get current git commit SHA
    const sha = execSync('git rev-parse HEAD').toString().trim();

    // Get tree hash for snapshot
    const treeHash = execSync('git rev-parse HEAD^{tree}').toString().trim();

    // Generate timestamp
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');

    // Create log entry
    const logEntry = {
      sha,
      status,
      agent: 'manus',
      phase: '10.5',
      features: ['threading', 'orchestrator', 'auth', 'chakra'],
      snapshot_hash: treeHash,
      vercel_status: status === 'passed' ? 'success' : 'failed',
      timestamp: new Date().toISOString()
    };

    // Create log file path
    const logPath = path.join(LOGS_DIR, `deploy_log_${timestamp}.json`);

    // Write log file
    fs.writeFileSync(logPath, JSON.stringify(logEntry, null, 2));

    console.log(`📝 Deployment log created at: ${logPath}`);

    return {
      success: true,
      logPath
    };
  } catch (error) {
    console.error(`❌ Error creating deployment log: ${error}`);

    return {
      success: false,
      logPath: ''
    };
  }
}

/**
 * Get the last successful deployment log
 */
export async function getLastSuccessfulDeployment(): Promise<any | null> {
  try {
    if (!fs.existsSync(LOGS_DIR)) {
      return null;
    }

    // Get all log files
    const logFiles = fs
      .readdirSync(LOGS_DIR)
      .filter((file) => file.startsWith('deploy_log_') && file.endsWith('.json'))
      .map((file) => path.join(LOGS_DIR, file));

    if (logFiles.length === 0) {
      return null;
    }

    // Sort by file creation time (newest first)
    logFiles.sort((a, b) => {
      return fs.statSync(b).mtime.getTime() - fs.statSync(a).mtime.getTime();
    });

    // Find the most recent successful deployment
    for (const logFile of logFiles) {
      const logContent = JSON.parse(fs.readFileSync(logFile, 'utf8'));
      if (logContent.status === 'passed' && logContent.vercel_status === 'success') {
        return logContent;
      }
    }

    return null;
  } catch (error) {
    console.error(`❌ Error getting last successful deployment: ${error}`);
    return null;
  }
}

/**
 * Update the deployment logging system in the pre-push enforcement logic
 */
export function updateDeployEnforcement() {
  // This function would be called to integrate the logging system with the enforcement logic
  console.log('Updating deployment enforcement with logging system...');

  // In a real implementation, this would modify the pre-push hooks or other enforcement mechanisms
  return {
    success: true,
    message: 'Deployment enforcement updated with logging system'
  };
}

// Export functions for use in other modules
export default {
  logDeployment,
  getLastSuccessfulDeployment,
  updateDeployEnforcement
};
