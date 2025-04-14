/**
 * Promethios Deployment Integrity Validators
 * 
 * This module contains validation functions that ensure deployment integrity
 * by checking for required components, configurations, and build status.
 */

import * as fs from 'fs';
import * as path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);
const UI_ROOT = path.resolve(process.cwd(), 'promethios-ui');

/**
 * Checks if BrowserRouter is properly configured in main.tsx
 */
export async function checkMainRouter(): Promise<{success: boolean, message: string}> {
  try {
    const mainTsxPath = path.join(UI_ROOT, 'main.tsx');
    if (!fs.existsSync(mainTsxPath)) {
      return { 
        success: false, 
        message: 'main.tsx file not found in promethios-ui directory' 
      };
    }

    const content = fs.readFileSync(mainTsxPath, 'utf8');
    const hasBrowserRouter = content.includes('BrowserRouter') || 
                             content.includes('Router') ||
                             content.includes('from \'react-router-dom\'');

    return {
      success: hasBrowserRouter,
      message: hasBrowserRouter 
        ? 'BrowserRouter is properly configured in main.tsx' 
        : 'BrowserRouter is missing from main.tsx'
    };
  } catch (error) {
    return {
      success: false,
      message: `Error checking BrowserRouter: ${error}`
    };
  }
}

/**
 * Checks if ChakraProvider is properly configured in main.tsx
 */
export async function checkChakraProvider(): Promise<{success: boolean, message: string}> {
  try {
    const mainTsxPath = path.join(UI_ROOT, 'main.tsx');
    if (!fs.existsSync(mainTsxPath)) {
      return { 
        success: false, 
        message: 'main.tsx file not found in promethios-ui directory' 
      };
    }

    const content = fs.readFileSync(mainTsxPath, 'utf8');
    const hasChakraProvider = content.includes('ChakraProvider') || 
                              content.includes('from \'@chakra-ui/react\'');

    return {
      success: hasChakraProvider,
      message: hasChakraProvider 
        ? 'ChakraProvider is properly configured in main.tsx' 
        : 'ChakraProvider is missing from main.tsx'
    };
  } catch (error) {
    return {
      success: false,
      message: `Error checking ChakraProvider: ${error}`
    };
  }
}

/**
 * Checks if AuthProvider is properly configured in main.tsx
 */
export async function checkAuthProvider(): Promise<{success: boolean, message: string}> {
  try {
    const mainTsxPath = path.join(UI_ROOT, 'main.tsx');
    if (!fs.existsSync(mainTsxPath)) {
      return { 
        success: false, 
        message: 'main.tsx file not found in promethios-ui directory' 
      };
    }

    const content = fs.readFileSync(mainTsxPath, 'utf8');
    const hasAuthProvider = content.includes('AuthProvider') || 
                            content.includes('from \'./context/AuthContext\'') ||
                            content.includes('from \'./context/auth\'');

    return {
      success: hasAuthProvider,
      message: hasAuthProvider 
        ? 'AuthProvider is properly configured in main.tsx' 
        : 'AuthProvider is missing from main.tsx'
    };
  } catch (error) {
    return {
      success: false,
      message: `Error checking AuthProvider: ${error}`
    };
  }
}

/**
 * Checks if dashboard pages exist
 */
export async function checkDashboardPages(): Promise<{success: boolean, message: string}> {
  try {
    const pagesDir = path.join(UI_ROOT, 'pages');
    const indexPath = path.join(pagesDir, 'index.tsx');
    const dashboardPath = path.join(pagesDir, 'dashboard.tsx');
    
    // Check for index.tsx or index.jsx
    const hasIndex = fs.existsSync(indexPath) || fs.existsSync(indexPath.replace('.tsx', '.jsx'));
    
    // Check for dashboard.tsx or dashboard.jsx
    const hasDashboard = fs.existsSync(dashboardPath) || 
                         fs.existsSync(dashboardPath.replace('.tsx', '.jsx')) ||
                         fs.existsSync(path.join(pagesDir, 'Dashboard.tsx')) ||
                         fs.existsSync(path.join(pagesDir, 'Dashboard.jsx'));

    return {
      success: hasIndex && hasDashboard,
      message: hasIndex && hasDashboard 
        ? 'Dashboard pages exist' 
        : `Missing required pages: ${!hasIndex ? 'index.tsx' : ''} ${!hasDashboard ? 'dashboard.tsx' : ''}`
    };
  } catch (error) {
    return {
      success: false,
      message: `Error checking dashboard pages: ${error}`
    };
  }
}

/**
 * Checks for unresolved imports in TypeScript files
 */
export async function checkImportPaths(): Promise<{success: boolean, message: string}> {
  try {
    const result = await execAsync('npx tsc --noEmit', { cwd: UI_ROOT });
    return {
      success: true,
      message: 'All import paths are valid'
    };
  } catch (error) {
    // TypeScript compilation errors
    return {
      success: false,
      message: `Found unresolved imports: ${error.stderr}`
    };
  }
}

/**
 * Checks for nested .git folders inside promethios-ui
 */
export async function checkNoGitFolders(): Promise<{success: boolean, message: string}> {
  try {
    const { stdout } = await execAsync('find . -type d -name ".git"', { cwd: UI_ROOT });
    const nestedGitFolders = stdout.trim();
    
    return {
      success: !nestedGitFolders,
      message: !nestedGitFolders 
        ? 'No nested .git folders found' 
        : `Found nested .git folders: ${nestedGitFolders}`
    };
  } catch (error) {
    return {
      success: false,
      message: `Error checking for nested .git folders: ${error}`
    };
  }
}

/**
 * Runs a dry build with Vite to check for build errors
 */
export async function runViteDryBuild(): Promise<{success: boolean, message: string}> {
  try {
    const { stdout, stderr } = await execAsync('npm run build', { cwd: UI_ROOT });
    
    // Check if build was successful
    if (stderr && stderr.includes('error')) {
      return {
        success: false,
        message: `Vite build failed: ${stderr}`
      };
    }
    
    return {
      success: true,
      message: 'Vite build completed successfully'
    };
  } catch (error) {
    return {
      success: false,
      message: `Vite build failed: ${error.message}`
    };
  }
}

/**
 * Runs all validators and returns a combined result
 */
export async function runAllValidators(): Promise<{
  success: boolean,
  results: Array<{name: string, success: boolean, message: string}>
}> {
  const validators = [
    { name: 'BrowserRouter', fn: checkMainRouter },
    { name: 'ChakraProvider', fn: checkChakraProvider },
    { name: 'AuthProvider', fn: checkAuthProvider },
    { name: 'Dashboard Pages', fn: checkDashboardPages },
    { name: 'Import Paths', fn: checkImportPaths },
    { name: 'No Git Folders', fn: checkNoGitFolders },
    { name: 'Vite Build', fn: runViteDryBuild }
  ];
  
  const results = await Promise.all(
    validators.map(async (validator) => {
      const result = await validator.fn();
      return {
        name: validator.name,
        success: result.success,
        message: result.message
      };
    })
  );
  
  const success = results.every(result => result.success);
  
  return {
    success,
    results
  };
}
