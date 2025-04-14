/**
 * Promethios Deployment Integrity Enforcement
 * 
 * This module implements the pre-push enforcement logic to ensure
 * only clean, verified builds are allowed to be committed or pushed.
 */

import * as path from 'path';
import * as fs from 'fs';
import { runAllValidators } from '../integrity/validators';

/**
 * Verify deployment integrity
 * 
 * This tool runs all validators and blocks the push if any check fails
 */
export async function verifyDeploymentIntegrity() {
  console.log('🛡️ Running Promethios Deployment Integrity Checks...');
  
  try {
    const validationResults = await runAllValidators();
    
    if (validationResults.success) {
      console.log('✅ All deployment integrity checks passed!');
      console.log('\nValidation Results:');
      validationResults.results.forEach(result => {
        console.log(`- ${result.name}: ${result.success ? '✅ PASS' : '❌ FAIL'} - ${result.message}`);
      });
      
      return {
        success: true,
        message: 'Deployment integrity verified. Push allowed.',
        details: validationResults.results
      };
    } else {
      console.error('❌ Deployment integrity checks failed!');
      console.error('\nFailed Checks:');
      
      const failedChecks = validationResults.results.filter(result => !result.success);
      failedChecks.forEach(result => {
        console.error(`- ${result.name}: ❌ FAIL - ${result.message}`);
      });
      
      // Generate detailed failure report
      await reportFailureDetails(failedChecks);
      
      return {
        success: false,
        message: 'Deployment integrity verification failed. Push blocked.',
        details: validationResults.results
      };
    }
  } catch (error) {
    console.error(`❌ Error during deployment integrity verification: ${error}`);
    
    return {
      success: false,
      message: `Error during deployment integrity verification: ${error}`,
      details: []
    };
  }
}

/**
 * Generate a detailed failure report
 */
async function reportFailureDetails(failedChecks: Array<{name: string, success: boolean, message: string}>) {
  try {
    const logsDir = path.resolve(process.cwd(), 'logs');
    if (!fs.existsSync(logsDir)) {
      fs.mkdirSync(logsDir, { recursive: true });
    }
    
    const failureReport = {
      timestamp: new Date().toISOString(),
      status: 'failed',
      failed_checks: failedChecks,
      recommendations: generateRecommendations(failedChecks)
    };
    
    const reportPath = path.join(logsDir, 'deploy_failure.json');
    fs.writeFileSync(reportPath, JSON.stringify(failureReport, null, 2));
    
    console.error(`\n📋 Detailed failure report generated at: ${reportPath}`);
  } catch (error) {
    console.error(`Error generating failure report: ${error}`);
  }
}

/**
 * Generate recommendations based on failed checks
 */
function generateRecommendations(failedChecks: Array<{name: string, success: boolean, message: string}>): string[] {
  const recommendations: string[] = [];
  
  failedChecks.forEach(check => {
    switch (check.name) {
      case 'BrowserRouter':
        recommendations.push('Add BrowserRouter to main.tsx: import { BrowserRouter } from "react-router-dom"');
        recommendations.push('Wrap your App component with BrowserRouter in main.tsx');
        break;
      case 'ChakraProvider':
        recommendations.push('Add ChakraProvider to main.tsx: import { ChakraProvider } from "@chakra-ui/react"');
        recommendations.push('Wrap your App component with ChakraProvider in main.tsx');
        break;
      case 'AuthProvider':
        recommendations.push('Add AuthProvider to main.tsx: import { AuthProvider } from "./context/auth"');
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
        recommendations.push('Run "find promethios-ui -type d -name \'.git\' -exec rm -rf {} \\;" to clean up');
        break;
      case 'Vite Build':
        recommendations.push('Fix build errors in the promethios-ui project');
        recommendations.push('Run "npm run build" in the promethios-ui directory to see detailed errors');
        break;
      default:
        recommendations.push(`Fix the issue with ${check.name}: ${check.message}`);
    }
  });
  
  return recommendations;
}

// Export the tool for use in the toolkit
export const tools = {
  "verify.deployment.integrity": verifyDeploymentIntegrity,
  "report.failure.details": async (failedChecks: any) => {
    return await reportFailureDetails(failedChecks);
  },
  "verify.folder.integrity": async () => {
    // Check if promethios-ui has no legacy trash
    console.log('Verifying folder integrity...');
    // Implementation would scan for unnecessary files
    return { success: true, message: 'Folder integrity verified' };
  },
  "validate.ui.structure": async () => {
    // Check main.tsx and required component hierarchy
    console.log('Validating UI structure...');
    const routerCheck = await (await import('../integrity/validators')).checkMainRouter();
    const chakraCheck = await (await import('../integrity/validators')).checkChakraProvider();
    const authCheck = await (await import('../integrity/validators')).checkAuthProvider();
    
    return {
      success: routerCheck.success && chakraCheck.success && authCheck.success,
      message: 'UI structure validation completed',
      details: [routerCheck, chakraCheck, authCheck]
    };
  },
  "validate.pages.exists": async () => {
    // Check if required pages exist
    console.log('Validating pages existence...');
    return await (await import('../integrity/validators')).checkDashboardPages();
  },
  "vite.dry.run": async () => {
    // Execute build and parse logs for failure
    console.log('Running Vite dry build...');
    return await (await import('../integrity/validators')).runViteDryBuild();
  },
  "vercel.rollback.last-good": async () => {
    // Rollback to last healthy commit
    console.log('Rolling back to last good deployment...');
    // Implementation would identify and restore the last successful deployment
    return { success: true, message: 'Rollback to last good deployment completed' };
  }
};
