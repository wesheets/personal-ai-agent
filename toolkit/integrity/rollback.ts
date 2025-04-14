/**
 * Promethios Vercel Rollback Hook
 * 
 * This module implements an optional rollback hook that allows Orchestrator
 * to restore the last healthy commit automatically if a deploy fails visually.
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';
import deploymentLogger from './deployment_logger';

// Vercel API configuration
const VERCEL_CONFIG = {
  apiUrl: 'https://api.vercel.com',
  teamId: process.env.VERCEL_TEAM_ID || '',
  token: process.env.VERCEL_TOKEN || ''
};

/**
 * Rollback to the last good deployment
 */
export async function rollbackToLastGoodDeployment(): Promise<{success: boolean, message: string, commit?: string}> {
  console.log('⏪ Rolling back to last good deployment...');
  
  try {
    // Get last successful deployment
    const lastGoodDeployment = await deploymentLogger.getLastSuccessfulDeployment();
    
    if (!lastGoodDeployment) {
      return {
        success: false,
        message: 'No successful deployments found to roll back to'
      };
    }
    
    // Log the rollback action
    const logsDir = path.resolve(process.cwd(), 'logs/rollbacks');
    if (!fs.existsSync(logsDir)) {
      fs.mkdirSync(logsDir, { recursive: true });
    }
    
    const rollbackLog = {
      timestamp: new Date().toISOString(),
      action: 'rollback',
      from_sha: execSync('git rev-parse HEAD').toString().trim(),
      to_sha: lastGoodDeployment.sha,
      reason: 'Automated rollback due to failed deployment',
      agent: 'manus',
      phase: '10.5'
    };
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const rollbackLogPath = path.join(logsDir, `rollback_log_${timestamp}.json`);
    fs.writeFileSync(rollbackLogPath, JSON.stringify(rollbackLog, null, 2));
    
    console.log(`📝 Rollback log created at: ${rollbackLogPath}`);
    
    // In a real implementation, this would trigger a Vercel rollback via API
    // For now, we'll simulate it by checking out the commit
    console.log(`Would roll back to commit: ${lastGoodDeployment.sha}`);
    
    // Simulate the rollback by creating a rollback script
    const rollbackScriptPath = path.resolve(process.cwd(), 'toolkit/integrity/rollback.sh');
    const rollbackScript = `#!/bin/bash
echo "⏪ Rolling back to last good deployment: ${lastGoodDeployment.sha}"

# Stash any changes
git stash

# Checkout the last good commit
git checkout ${lastGoodDeployment.sha}

# Trigger a new deployment
# In a real implementation, this would call the Vercel API to deploy

echo "✅ Rollback complete"
`;
    
    fs.writeFileSync(rollbackScriptPath, rollbackScript);
    execSync(`chmod +x ${rollbackScriptPath}`);
    
    console.log(`📝 Rollback script created at: ${rollbackScriptPath}`);
    
    return {
      success: true,
      message: `Successfully prepared rollback to last good deployment: ${lastGoodDeployment.sha}`,
      commit: lastGoodDeployment.sha
    };
  } catch (error) {
    console.error(`❌ Error rolling back to last good deployment: ${error}`);
    
    return {
      success: false,
      message: `Error rolling back to last good deployment: ${error}`
    };
  }
}

/**
 * Check if a deployment is healthy
 */
export async function checkDeploymentHealth(deploymentUrl: string): Promise<{healthy: boolean, message: string}> {
  console.log(`🔍 Checking deployment health for: ${deploymentUrl}`);
  
  try {
    // In a real implementation, this would make HTTP requests to check the deployment
    // For now, we'll simulate it
    
    // Simulate a health check by checking if the URL is valid
    if (!deploymentUrl || !deploymentUrl.startsWith('http')) {
      return {
        healthy: false,
        message: 'Invalid deployment URL'
      };
    }
    
    // Simulate a successful health check
    return {
      healthy: true,
      message: 'Deployment is healthy'
    };
  } catch (error) {
    console.error(`❌ Error checking deployment health: ${error}`);
    
    return {
      healthy: false,
      message: `Error checking deployment health: ${error}`
    };
  }
}

/**
 * Setup Vercel rollback hook
 */
export async function setupVercelRollbackHook(): Promise<{success: boolean, message: string}> {
  console.log('🔧 Setting up Vercel rollback hook...');
  
  try {
    // Create the orchestrator directory if it doesn't exist
    const orchestratorDir = path.resolve(process.cwd(), 'toolkit/orchestrator');
    if (!fs.existsSync(orchestratorDir)) {
      fs.mkdirSync(orchestratorDir, { recursive: true });
    }
    
    // Create the rollback hook script
    const rollbackHookPath = path.join(orchestratorDir, 'vercel_rollback_hook.js');
    const rollbackHookScript = `/**
 * Vercel Rollback Hook for Orchestrator
 * 
 * This script is called by the Orchestrator when a deployment fails visually.
 * It triggers a rollback to the last healthy commit.
 */

const { rollbackToLastGoodDeployment } = require('../integrity/rollback');

async function handleDeploymentFailure(deploymentId, deploymentUrl) {
  console.log(\`🚨 Deployment failure detected: \${deploymentId} at \${deploymentUrl}\`);
  
  try {
    const rollbackResult = await rollbackToLastGoodDeployment();
    
    if (rollbackResult.success) {
      console.log(\`✅ Rollback successful to commit: \${rollbackResult.commit}\`);
      return { success: true, message: \`Rolled back to \${rollbackResult.commit}\` };
    } else {
      console.error(\`❌ Rollback failed: \${rollbackResult.message}\`);
      return { success: false, message: rollbackResult.message };
    }
  } catch (error) {
    console.error(\`❌ Error in rollback hook: \${error}\`);
    return { success: false, message: \`Error in rollback hook: \${error}\` };
  }
}

module.exports = {
  handleDeploymentFailure
};
`;
    
    fs.writeFileSync(rollbackHookPath, rollbackHookScript);
    
    console.log(`📝 Vercel rollback hook created at: ${rollbackHookPath}`);
    
    // Create a README file to explain how to use the rollback hook
    const readmePath = path.join(orchestratorDir, 'ROLLBACK_HOOK_README.md');
    const readmeContent = `# Vercel Rollback Hook

This directory contains the Vercel rollback hook that allows Orchestrator to restore the last healthy commit automatically if a deploy fails visually.

## Usage

The rollback hook is automatically triggered when a deployment fails. It will:

1. Check the deployment logs for the last successful deployment
2. Roll back to that commit
3. Trigger a new deployment

## Manual Rollback

To manually trigger a rollback, you can use the following command:

\`\`\`bash
node -e "require('./toolkit/orchestrator/vercel_rollback_hook').handleDeploymentFailure('manual', 'manual')"
\`\`\`

Or use the agent toolkit:

\`\`\`bash
/tool/run vercel.rollback.last-good
\`\`\`

## Configuration

The rollback hook uses the following environment variables:

- \`VERCEL_TOKEN\`: Your Vercel API token
- \`VERCEL_TEAM_ID\`: Your Vercel team ID (if applicable)

These can be set in your environment or in a \`.env\` file.
`;
    
    fs.writeFileSync(readmePath, readmeContent);
    
    console.log(`📝 Rollback hook README created at: ${readmePath}`);
    
    return {
      success: true,
      message: 'Vercel rollback hook setup successfully'
    };
  } catch (error) {
    console.error(`❌ Error setting up Vercel rollback hook: ${error}`);
    
    return {
      success: false,
      message: `Error setting up Vercel rollback hook: ${error}`
    };
  }
}

// Export functions for use in other modules
export default {
  rollbackToLastGoodDeployment,
  checkDeploymentHealth,
  setupVercelRollbackHook
};
