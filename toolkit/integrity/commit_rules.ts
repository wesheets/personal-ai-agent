/**
 * Promethios Commit Rules Enforcement
 *
 * This module implements the commit rules to ensure only clean,
 * verified builds are allowed to be committed.
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';
import { runAllValidators } from './validators';
import deploymentLogger from './deployment_logger';

// Git hooks directory
const GIT_HOOKS_DIR = path.resolve(process.cwd(), '.git/hooks');

/**
 * Install the pre-commit hook to enforce commit rules
 */
export async function installCommitRules(): Promise<{ success: boolean; message: string }> {
  try {
    // Create hooks directory if it doesn't exist
    if (!fs.existsSync(GIT_HOOKS_DIR)) {
      fs.mkdirSync(GIT_HOOKS_DIR, { recursive: true });
    }

    // Create pre-commit hook script
    const preCommitHookPath = path.join(GIT_HOOKS_DIR, 'pre-commit');
    const preCommitScript = `#!/bin/bash
echo "🛡️ Running Promethios Deployment Integrity Checks..."

# Run the validation script
node -e "
  const { runAllValidators } = require('${path.resolve(process.cwd(), 'toolkit/integrity/validators')}');
  
  async function validateCommit() {
    try {
      const results = await runAllValidators();
      
      if (!results.success) {
        console.error('❌ Deployment integrity checks failed!');
        console.error('\\nFailed Checks:');
        
        const failedChecks = results.results.filter(r => !r.success);
        failedChecks.forEach(result => {
          console.error(\`- \${result.name}: ❌ FAIL - \${result.message}\`);
        });
        
        console.error('\\n❌ Commit blocked due to failed integrity checks');
        process.exit(1);
      } else {
        console.log('✅ All deployment integrity checks passed!');
      }
    } catch (error) {
      console.error(\`❌ Error during validation: \${error}\`);
      process.exit(1);
    }
  }
  
  validateCommit();
"

if [ $? -ne 0 ]; then
  echo "❌ Commit blocked. Run '/tool/run report.failure.details' for more information."
  exit 1
fi

# Verify commit message format
commit_msg=$(cat "$1")
if [[ ! "$commit_msg" =~ ^fix:\ deploy\ verified\ build\ \|\ passed\ integrity\ checks\ \|\ phase:10\.5 ]]; then
  echo "❌ Invalid commit message format."
  echo "Commit message must be: 'fix: deploy verified build | passed integrity checks | phase:10.5'"
  exit 1
fi

# All checks passed
echo "✅ Commit allowed."
exit 0
`;

    // Write pre-commit hook script
    fs.writeFileSync(preCommitHookPath, preCommitScript);

    // Make pre-commit hook executable
    execSync(`chmod +x ${preCommitHookPath}`);

    console.log(`✅ Pre-commit hook installed at: ${preCommitHookPath}`);

    return {
      success: true,
      message: 'Commit rules installed successfully'
    };
  } catch (error) {
    console.error(`❌ Error installing commit rules: ${error}`);

    return {
      success: false,
      message: `Error installing commit rules: ${error}`
    };
  }
}

/**
 * Validate a commit against the commit rules
 */
export async function validateCommit(): Promise<{ success: boolean; message: string }> {
  try {
    console.log('🔍 Validating commit against deployment integrity rules...');

    // Run all validators
    const validationResults = await runAllValidators();

    if (!validationResults.success) {
      console.error('❌ Commit validation failed!');
      console.error('\nFailed Checks:');

      const failedChecks = validationResults.results.filter((result) => !result.success);
      failedChecks.forEach((result) => {
        console.error(`- ${result.name}: ❌ FAIL - ${result.message}`);
      });

      return {
        success: false,
        message: 'Commit validation failed. See logs for details.'
      };
    }

    console.log('✅ Commit validation passed!');

    // Log successful validation
    await deploymentLogger.logDeployment('passed');

    return {
      success: true,
      message: 'Commit validation passed'
    };
  } catch (error) {
    console.error(`❌ Error during commit validation: ${error}`);

    return {
      success: false,
      message: `Error during commit validation: ${error}`
    };
  }
}

/**
 * Verify commit message format
 */
export function verifyCommitMessage(message: string): { success: boolean; message: string } {
  const requiredFormat = 'fix: deploy verified build | passed integrity checks | phase:10.5';
  const isValid = message.trim() === requiredFormat;

  return {
    success: isValid,
    message: isValid
      ? 'Commit message format is valid'
      : `Invalid commit message format. Required format: "${requiredFormat}"`
  };
}

// Export functions for use in other modules
export default {
  installCommitRules,
  validateCommit,
  verifyCommitMessage
};
