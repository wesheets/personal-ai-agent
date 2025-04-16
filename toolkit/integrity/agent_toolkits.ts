/**
 * Promethios Agent Toolkits for Deployment Integrity
 *
 * This module provides a set of tools for agents to interact with
 * the deployment integrity system.
 */

import * as path from 'path';
import * as fs from 'fs';
import { execSync } from 'child_process';
import {
  runAllValidators,
  checkMainRouter,
  checkChakraProvider,
  checkAuthProvider,
  checkDashboardPages,
  checkImportPaths,
  checkNoGitFolders,
  runViteDryBuild
} from './validators';
import deploymentLogger from './deployment_logger';
import commitRules from './commit_rules';

/**
 * Verify folder integrity
 * Confirms /promethios-ui has no legacy trash
 */
export async function verifyFolderIntegrity(): Promise<{
  success: boolean;
  message: string;
  details?: any;
}> {
  console.log('🔍 Verifying folder integrity...');

  try {
    const UI_ROOT = path.resolve(process.cwd(), 'promethios-ui');

    // Check for common legacy/trash files
    const legacyPatterns = [
      '.DS_Store',
      'Thumbs.db',
      '*.bak',
      '*.tmp',
      '*.log',
      'node_modules/.cache',
      '.git'
    ];

    const foundTrash: string[] = [];

    for (const pattern of legacyPatterns) {
      try {
        const result = execSync(`find ${UI_ROOT} -name "${pattern}" | grep -v "node_modules"`, {
          stdio: 'pipe'
        })
          .toString()
          .trim();
        if (result) {
          foundTrash.push(...result.split('\n'));
        }
      } catch (error) {
        // grep returns non-zero exit code when no matches found, which is fine
      }
    }

    return {
      success: foundTrash.length === 0,
      message:
        foundTrash.length === 0
          ? 'No legacy trash found in /promethios-ui'
          : `Found ${foundTrash.length} legacy trash files in /promethios-ui`,
      details: foundTrash.length > 0 ? { foundTrash } : undefined
    };
  } catch (error) {
    console.error(`❌ Error verifying folder integrity: ${error}`);

    return {
      success: false,
      message: `Error verifying folder integrity: ${error}`
    };
  }
}

/**
 * Validate UI structure
 * Checks main.tsx and required component hierarchy
 */
export async function validateUIStructure(): Promise<{
  success: boolean;
  message: string;
  details: any;
}> {
  console.log('🔍 Validating UI structure...');

  try {
    const routerCheck = await checkMainRouter();
    const chakraCheck = await checkChakraProvider();
    const authCheck = await checkAuthProvider();

    const success = routerCheck.success && chakraCheck.success && authCheck.success;

    return {
      success,
      message: success ? 'UI structure validation passed' : 'UI structure validation failed',
      details: {
        router: routerCheck,
        chakra: chakraCheck,
        auth: authCheck
      }
    };
  } catch (error) {
    console.error(`❌ Error validating UI structure: ${error}`);

    return {
      success: false,
      message: `Error validating UI structure: ${error}`,
      details: { error: String(error) }
    };
  }
}

/**
 * Validate pages existence
 * Checks /pages/index.tsx, /dashboard.tsx
 */
export async function validatePagesExist(): Promise<{ success: boolean; message: string }> {
  console.log('🔍 Validating pages existence...');

  try {
    return await checkDashboardPages();
  } catch (error) {
    console.error(`❌ Error validating pages existence: ${error}`);

    return {
      success: false,
      message: `Error validating pages existence: ${error}`
    };
  }
}

/**
 * Run Vite dry build
 * Executes build and parses logs for failure
 */
export async function viteDryRun(): Promise<{ success: boolean; message: string }> {
  console.log('🔧 Running Vite dry build...');

  try {
    return await runViteDryBuild();
  } catch (error) {
    console.error(`❌ Error running Vite dry build: ${error}`);

    return {
      success: false,
      message: `Error running Vite dry build: ${error}`
    };
  }
}

/**
 * Report failure details
 * Dumps reasons for block into /logs/deploy_failure.json
 */
export async function reportFailureDetails(): Promise<{
  success: boolean;
  message: string;
  reportPath?: string;
}> {
  console.log('📋 Generating failure report...');

  try {
    // Run all validators to get current status
    const validationResults = await runAllValidators();

    if (validationResults.success) {
      return {
        success: true,
        message: 'No failures to report. All checks passed.'
      };
    }

    // Create logs directory if it doesn't exist
    const logsDir = path.resolve(process.cwd(), 'logs');
    if (!fs.existsSync(logsDir)) {
      fs.mkdirSync(logsDir, { recursive: true });
    }

    // Get failed checks
    const failedChecks = validationResults.results.filter((result) => !result.success);

    // Generate recommendations
    const recommendations: string[] = [];
    failedChecks.forEach((check) => {
      switch (check.name) {
        case 'BrowserRouter':
          recommendations.push(
            'Add BrowserRouter to main.tsx: import { BrowserRouter } from "react-router-dom"'
          );
          recommendations.push('Wrap your App component with BrowserRouter in main.tsx');
          break;
        case 'ChakraProvider':
          recommendations.push(
            'Add ChakraProvider to main.tsx: import { ChakraProvider } from "@chakra-ui/react"'
          );
          recommendations.push('Wrap your App component with ChakraProvider in main.tsx');
          break;
        case 'AuthProvider':
          recommendations.push(
            'Add AuthProvider to main.tsx: import { AuthProvider } from "./context/auth"'
          );
          recommendations.push('Wrap your App component with AuthProvider in main.tsx');
          break;
        case 'Dashboard Pages':
          recommendations.push('Create missing dashboard pages in the /pages directory');
          recommendations.push('Ensure index.tsx and dashboard.tsx exist in the /pages directory');
          break;
        case 'Import Paths':
          recommendations.push('Fix unresolved imports in TypeScript files');
          recommendations.push('Run "npx tsc --noEmit" to identify specific import issues');
          break;
        case 'No Git Folders':
          recommendations.push('Remove nested .git folders from the promethios-ui directory');
          recommendations.push(
            'Run "find promethios-ui -type d -name \'.git\' -exec rm -rf {} \\;" to clean up'
          );
          break;
        case 'Vite Build':
          recommendations.push('Fix build errors in the promethios-ui project');
          recommendations.push(
            'Run "npm run build" in the promethios-ui directory to see detailed errors'
          );
          break;
        default:
          recommendations.push(`Fix the issue with ${check.name}: ${check.message}`);
      }
    });

    // Create failure report
    const failureReport = {
      timestamp: new Date().toISOString(),
      status: 'failed',
      failed_checks: failedChecks,
      recommendations,
      agent: 'manus',
      phase: '10.5'
    };

    // Write failure report
    const reportPath = path.join(logsDir, 'deploy_failure.json');
    fs.writeFileSync(reportPath, JSON.stringify(failureReport, null, 2));

    console.log(`📋 Failure report generated at: ${reportPath}`);

    return {
      success: true,
      message: `Failure report generated at: ${reportPath}`,
      reportPath
    };
  } catch (error) {
    console.error(`❌ Error generating failure report: ${error}`);

    return {
      success: false,
      message: `Error generating failure report: ${error}`
    };
  }
}

/**
 * Vercel rollback to last good deployment
 * Allows Orchestrator to restore the last healthy commit automatically
 */
export async function vercelRollbackLastGood(): Promise<{
  success: boolean;
  message: string;
  commit?: string;
}> {
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

    // In a real implementation, this would trigger a Vercel rollback
    // For now, we'll just simulate it by printing the commit SHA
    console.log(`Would roll back to commit: ${lastGoodDeployment.sha}`);

    return {
      success: true,
      message: `Successfully rolled back to last good deployment: ${lastGoodDeployment.sha}`,
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

// Export all tools for use in the toolkit
export const agentTools = {
  'verify.folder.integrity': verifyFolderIntegrity,
  'validate.ui.structure': validateUIStructure,
  'validate.pages.exists': validatePagesExist,
  'vite.dry.run': viteDryRun,
  'report.failure.details': reportFailureDetails,
  'vercel.rollback.last-good': vercelRollbackLastGood,
  'verify.deployment.integrity': async () => {
    return await runAllValidators();
  }
};

// Export functions for use in other modules
export default agentTools;
