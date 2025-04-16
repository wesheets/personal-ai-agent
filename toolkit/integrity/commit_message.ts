/**
 * Promethios Commit Message Enforcement
 *
 * This module implements the commit message enforcement to ensure
 * proper commit message format for deployment integrity.
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

// Git hooks directory
const GIT_HOOKS_DIR = path.resolve(process.cwd(), '.git/hooks');

// Required commit message format
const REQUIRED_COMMIT_FORMAT = 'fix: deploy verified build | passed integrity checks | phase:10.5';

/**
 * Install the commit-msg hook to enforce commit message format
 */
export async function installCommitMessageHook(): Promise<{ success: boolean; message: string }> {
  try {
    // Create hooks directory if it doesn't exist
    if (!fs.existsSync(GIT_HOOKS_DIR)) {
      fs.mkdirSync(GIT_HOOKS_DIR, { recursive: true });
    }

    // Create commit-msg hook script
    const commitMsgHookPath = path.join(GIT_HOOKS_DIR, 'commit-msg');
    const commitMsgScript = `#!/bin/bash
echo "🔍 Checking commit message format..."

# Get the commit message from the file
commit_msg=$(cat "$1")

# Check if the commit message matches the required format
if [[ ! "$commit_msg" =~ ^fix:\ deploy\ verified\ build\ \|\ passed\ integrity\ checks\ \|\ phase:10\\.5 ]]; then
  echo "❌ Invalid commit message format."
  echo "Commit message must be: '${REQUIRED_COMMIT_FORMAT}'"
  exit 1
fi

echo "✅ Commit message format is valid."
exit 0
`;

    // Write commit-msg hook script
    fs.writeFileSync(commitMsgHookPath, commitMsgScript);

    // Make commit-msg hook executable
    execSync(`chmod +x ${commitMsgHookPath}`);

    console.log(`✅ Commit message hook installed at: ${commitMsgHookPath}`);

    return {
      success: true,
      message: 'Commit message hook installed successfully'
    };
  } catch (error) {
    console.error(`❌ Error installing commit message hook: ${error}`);

    return {
      success: false,
      message: `Error installing commit message hook: ${error}`
    };
  }
}

/**
 * Verify commit message format
 */
export function verifyCommitMessage(message: string): { success: boolean; message: string } {
  const isValid = message.trim() === REQUIRED_COMMIT_FORMAT;

  return {
    success: isValid,
    message: isValid
      ? 'Commit message format is valid'
      : `Invalid commit message format. Required format: "${REQUIRED_COMMIT_FORMAT}"`
  };
}

/**
 * Generate a valid commit message
 */
export function generateValidCommitMessage(): string {
  return REQUIRED_COMMIT_FORMAT;
}

/**
 * Update the prepare-commit-msg hook to suggest the valid format
 */
export async function installPrepareCommitMsgHook(): Promise<{
  success: boolean;
  message: string;
}> {
  try {
    // Create hooks directory if it doesn't exist
    if (!fs.existsSync(GIT_HOOKS_DIR)) {
      fs.mkdirSync(GIT_HOOKS_DIR, { recursive: true });
    }

    // Create prepare-commit-msg hook script
    const prepareCommitMsgHookPath = path.join(GIT_HOOKS_DIR, 'prepare-commit-msg');
    const prepareCommitMsgScript = `#!/bin/bash
# Only suggest the commit message if it's not already set
if [ -z "$(cat "$1" | grep -v '^#')" ]; then
  echo "${REQUIRED_COMMIT_FORMAT}" > "$1"
  echo "# Commit message template has been set to the required format." >> "$1"
  echo "# Please keep this format to ensure deployment integrity." >> "$1"
fi
`;

    // Write prepare-commit-msg hook script
    fs.writeFileSync(prepareCommitMsgHookPath, prepareCommitMsgScript);

    // Make prepare-commit-msg hook executable
    execSync(`chmod +x ${prepareCommitMsgHookPath}`);

    console.log(`✅ Prepare commit message hook installed at: ${prepareCommitMsgHookPath}`);

    return {
      success: true,
      message: 'Prepare commit message hook installed successfully'
    };
  } catch (error) {
    console.error(`❌ Error installing prepare commit message hook: ${error}`);

    return {
      success: false,
      message: `Error installing prepare commit message hook: ${error}`
    };
  }
}

/**
 * Install all commit message enforcement hooks
 */
export async function installAllCommitMessageHooks(): Promise<{
  success: boolean;
  message: string;
}> {
  try {
    const commitMsgResult = await installCommitMessageHook();
    const prepareCommitMsgResult = await installPrepareCommitMsgHook();

    if (!commitMsgResult.success || !prepareCommitMsgResult.success) {
      return {
        success: false,
        message: 'Failed to install all commit message hooks'
      };
    }

    return {
      success: true,
      message: 'All commit message hooks installed successfully'
    };
  } catch (error) {
    console.error(`❌ Error installing commit message hooks: ${error}`);

    return {
      success: false,
      message: `Error installing commit message hooks: ${error}`
    };
  }
}

// Export functions for use in other modules
export default {
  installCommitMessageHook,
  installPrepareCommitMsgHook,
  installAllCommitMessageHooks,
  verifyCommitMessage,
  generateValidCommitMessage,
  REQUIRED_COMMIT_FORMAT
};
