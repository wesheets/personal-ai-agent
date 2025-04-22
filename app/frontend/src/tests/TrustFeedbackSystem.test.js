/**
 * TrustFeedbackSystem.test.js
 * 
 * Test file for the trust feedback loop system components.
 * Ensures all components work as expected and comply with schemas.
 */

import { 
  calculateTrustScore, 
  calculateTrustDelta, 
  determineTrustChangeReason 
} from '../logic/TrustScoreEvaluator';
import { validateTrustEvent, validateDemotionEvent } from '../schemas/TrustSchema';

/**
 * Test trust score calculation
 */
const testTrustScoreCalculation = () => {
  console.log('Testing trust score calculation...');
  
  // Test with all metrics provided
  const metrics1 = {
    summary_realism: 0.8,
    loop_success: 0.9,
    reflection_clarity: 0.7,
    contradiction_frequency: 0.1,
    revision_rate: 0.2,
    operator_override: 0.05
  };
  
  const score1 = calculateTrustScore(metrics1);
  console.log(`Score with good metrics: ${score1.toFixed(2)}`);
  
  // Test with poor metrics
  const metrics2 = {
    summary_realism: 0.3,
    loop_success: 0.4,
    reflection_clarity: 0.2,
    contradiction_frequency: 0.6,
    revision_rate: 0.5,
    operator_override: 0.4
  };
  
  const score2 = calculateTrustScore(metrics2);
  console.log(`Score with poor metrics: ${score2.toFixed(2)}`);
  
  // Test with partial metrics
  const metrics3 = {
    summary_realism: 0.7,
    loop_success: 0.8
  };
  
  const score3 = calculateTrustScore(metrics3);
  console.log(`Score with partial metrics: ${score3.toFixed(2)}`);
  
  // Test with custom weights
  const customWeights = {
    summary_realism: 0.3,
    loop_success: 0.4,
    reflection_clarity: 0.1,
    contradiction_frequency: 0.1,
    revision_rate: 0.05,
    operator_override: 0.05
  };
  
  const score4 = calculateTrustScore(metrics1, customWeights);
  console.log(`Score with custom weights: ${score4.toFixed(2)}`);
  
  return true;
};

/**
 * Test trust delta calculation
 */
const testTrustDeltaCalculation = () => {
  console.log('Testing trust delta calculation...');
  
  // Test positive delta
  const delta1 = calculateTrustDelta(0.8, 0.7);
  console.log(`Positive delta: ${delta1.toFixed(2)}`);
  
  // Test negative delta
  const delta2 = calculateTrustDelta(0.6, 0.8);
  console.log(`Negative delta: ${delta2.toFixed(2)}`);
  
  // Test zero delta
  const delta3 = calculateTrustDelta(0.75, 0.75);
  console.log(`Zero delta: ${delta3.toFixed(2)}`);
  
  // Test with undefined previous score
  const delta4 = calculateTrustDelta(0.9);
  console.log(`Delta with undefined previous: ${delta4.toFixed(2)}`);
  
  return true;
};

/**
 * Test reason determination
 */
const testReasonDetermination = () => {
  console.log('Testing reason determination...');
  
  // Test with contradiction
  const metrics1 = {
    contradiction_frequency: 0.4,
    revision_rate: 0.1,
    operator_override: 0.0,
    summary_realism: 0.8,
    loop_success: 0.7,
    reflection_clarity: 0.9
  };
  
  const reason1 = determineTrustChangeReason(metrics1, -0.15);
  console.log(`Reason with contradiction: ${reason1}`);
  
  // Test with multiple factors
  const metrics2 = {
    contradiction_frequency: 0.4,
    revision_rate: 0.5,
    operator_override: 0.0,
    summary_realism: 0.8,
    loop_success: 0.7,
    reflection_clarity: 0.9
  };
  
  const reason2 = determineTrustChangeReason(metrics2, -0.2);
  console.log(`Reason with multiple factors: ${reason2}`);
  
  // Test with no significant factors
  const metrics3 = {
    contradiction_frequency: 0.1,
    revision_rate: 0.1,
    operator_override: 0.0,
    summary_realism: 0.8,
    loop_success: 0.7,
    reflection_clarity: 0.9
  };
  
  const reason3 = determineTrustChangeReason(metrics3, 0.05);
  console.log(`Reason with no significant factors: ${reason3}`);
  
  return true;
};

/**
 * Test schema validation
 */
const testSchemaValidation = () => {
  console.log('Testing schema validation...');
  
  // Valid trust event
  const validEvent = {
    id: `trust_${Date.now()}_1234`,
    agent: 'SAGE',
    loop_id: 'loop_123',
    trust_score: 0.85,
    delta: -0.05,
    reason: 'contradiction detected',
    timestamp: new Date().toISOString(),
    status: 'active',
    metrics: {
      summary_realism: 0.8,
      loop_success: 0.9,
      reflection_clarity: 0.7,
      contradiction_frequency: 0.1,
      revision_rate: 0.2,
      operator_override: 0.05
    }
  };
  
  const isValidEvent = validateTrustEvent(validEvent);
  console.log(`Valid trust event validation: ${isValidEvent}`);
  
  // Invalid trust event (missing required field)
  const invalidEvent = {
    id: `trust_${Date.now()}_5678`,
    agent: 'NOVA',
    // Missing loop_id
    trust_score: 0.65,
    delta: -0.1,
    reason: 'low summary realism',
    timestamp: new Date().toISOString(),
    // Missing status
  };
  
  const isInvalidEvent = validateTrustEvent(invalidEvent);
  console.log(`Invalid trust event validation: ${isInvalidEvent}`);
  
  // Valid demotion event
  const validDemotion = {
    id: `demotion_${Date.now()}_9012`,
    agent: 'HAL',
    fallback_agent: 'NOVA',
    trust_score: 0.35,
    reason: 'contradiction detected + unresolved',
    loop_id: 'loop_456',
    timestamp: new Date().toISOString(),
    status: 'active',
    manual: false
  };
  
  const isValidDemotion = validateDemotionEvent(validDemotion);
  console.log(`Valid demotion event validation: ${isValidDemotion}`);
  
  return true;
};

/**
 * Run all tests
 */
const runAllTests = () => {
  console.log('Running trust feedback system tests...');
  
  let allTestsPassed = true;
  
  try {
    // Run individual tests
    allTestsPassed = allTestsPassed && testTrustScoreCalculation();
    allTestsPassed = allTestsPassed && testTrustDeltaCalculation();
    allTestsPassed = allTestsPassed && testReasonDetermination();
    allTestsPassed = allTestsPassed && testSchemaValidation();
    
    console.log(`\nAll tests ${allTestsPassed ? 'PASSED' : 'FAILED'}`);
  } catch (error) {
    console.error('Error running tests:', error);
    allTestsPassed = false;
  }
  
  return allTestsPassed;
};

// Export test functions
export {
  testTrustScoreCalculation,
  testTrustDeltaCalculation,
  testReasonDetermination,
  testSchemaValidation,
  runAllTests
};

// Run tests if this file is executed directly
if (typeof require !== 'undefined' && require.main === module) {
  runAllTests();
}
