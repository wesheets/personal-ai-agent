/**
 * Test script for Promethios Deployment Integrity Layer
 * 
 * This script tests all components of the deployment integrity layer
 * to ensure they work as expected.
 */

import * as validators from './validators';
import deploymentLogger from './deployment_logger';
import commitRules from './commit_rules';
import commitMessage from './commit_message';
import rollback from './rollback';
import agentToolkits from './agent_toolkits';

async function runTests() {
  console.log('🧪 Running tests for Promethios Deployment Integrity Layer...\n');
  
  // Test validators
  console.log('📋 Testing validators...');
  try {
    const validationResults = await validators.runAllValidators();
    console.log(`✅ Validators test ${validationResults.success ? 'passed' : 'failed'}`);
    console.log('Validation Results:');
    validationResults.results.forEach(result => {
      console.log(`- ${result.name}: ${result.success ? '✅ PASS' : '❌ FAIL'} - ${result.message}`);
    });
  } catch (error) {
    console.error(`❌ Validators test failed: ${error}`);
  }
  console.log('');
  
  // Test deployment logger
  console.log('📋 Testing deployment logger...');
  try {
    const logResult = await deploymentLogger.logDeployment('passed');
    console.log(`✅ Deployment logger test ${logResult.success ? 'passed' : 'failed'}`);
    if (logResult.success) {
      console.log(`Log created at: ${logResult.logPath}`);
    }
    
    const lastDeployment = await deploymentLogger.getLastSuccessfulDeployment();
    console.log(`Last successful deployment: ${lastDeployment ? 'Found' : 'Not found'}`);
    if (lastDeployment) {
      console.log(`- SHA: ${lastDeployment.sha}`);
      console.log(`- Status: ${lastDeployment.status}`);
    }
  } catch (error) {
    console.error(`❌ Deployment logger test failed: ${error}`);
  }
  console.log('');
  
  // Test commit rules
  console.log('📋 Testing commit rules...');
  try {
    const validateResult = await commitRules.validateCommit();
    console.log(`✅ Commit rules validation test ${validateResult.success ? 'passed' : 'failed'}`);
    console.log(`- Message: ${validateResult.message}`);
  } catch (error) {
    console.error(`❌ Commit rules test failed: ${error}`);
  }
  console.log('');
  
  // Test commit message
  console.log('📋 Testing commit message enforcement...');
  try {
    const validMessage = commitMessage.generateValidCommitMessage();
    const verifyResult = commitMessage.verifyCommitMessage(validMessage);
    console.log(`✅ Commit message verification test ${verifyResult.success ? 'passed' : 'failed'}`);
    console.log(`- Valid message: ${validMessage}`);
    console.log(`- Verification result: ${verifyResult.message}`);
    
    const invalidMessage = 'This is an invalid commit message';
    const invalidVerifyResult = commitMessage.verifyCommitMessage(invalidMessage);
    console.log(`✅ Invalid commit message test ${!invalidVerifyResult.success ? 'passed' : 'failed'}`);
    console.log(`- Invalid message: ${invalidMessage}`);
    console.log(`- Verification result: ${invalidVerifyResult.message}`);
  } catch (error) {
    console.error(`❌ Commit message test failed: ${error}`);
  }
  console.log('');
  
  // Test rollback
  console.log('📋 Testing rollback hook...');
  try {
    const setupResult = await rollback.setupVercelRollbackHook();
    console.log(`✅ Rollback hook setup test ${setupResult.success ? 'passed' : 'failed'}`);
    console.log(`- Message: ${setupResult.message}`);
    
    const healthCheckResult = await rollback.checkDeploymentHealth('https://example.com');
    console.log(`✅ Deployment health check test ${healthCheckResult.healthy ? 'passed' : 'failed'}`);
    console.log(`- Message: ${healthCheckResult.message}`);
  } catch (error) {
    console.error(`❌ Rollback test failed: ${error}`);
  }
  console.log('');
  
  // Test agent toolkits
  console.log('📋 Testing agent toolkits...');
  try {
    console.log('Available tools:');
    Object.keys(agentToolkits).forEach(tool => {
      console.log(`- ${tool}`);
    });
    
    const integrityResult = await agentToolkits['verify.deployment.integrity']();
    console.log(`✅ Verify deployment integrity test ${integrityResult.success ? 'passed' : 'failed'}`);
    
    const folderResult = await agentToolkits['verify.folder.integrity']();
    console.log(`✅ Verify folder integrity test ${folderResult.success ? 'passed' : 'failed'}`);
    
    const uiResult = await agentToolkits['validate.ui.structure']();
    console.log(`✅ Validate UI structure test ${uiResult.success ? 'passed' : 'failed'}`);
    
    const pagesResult = await agentToolkits['validate.pages.exists']();
    console.log(`✅ Validate pages exists test ${pagesResult.success ? 'passed' : 'failed'}`);
    
    const viteBuildResult = await agentToolkits['vite.dry.run']();
    console.log(`✅ Vite dry run test ${viteBuildResult.success ? 'passed' : 'failed'}`);
    
    const failureReportResult = await agentToolkits['report.failure.details']();
    console.log(`✅ Report failure details test ${failureReportResult.success ? 'passed' : 'failed'}`);
    
    const rollbackResult = await agentToolkits['vercel.rollback.last-good']();
    console.log(`✅ Vercel rollback test ${rollbackResult.success ? 'passed' : 'failed'}`);
  } catch (error) {
    console.error(`❌ Agent toolkits test failed: ${error}`);
  }
  console.log('');
  
  console.log('🎉 All tests completed!');
}

// Run the tests
runTests().catch(error => {
  console.error(`❌ Test execution failed: ${error}`);
});
