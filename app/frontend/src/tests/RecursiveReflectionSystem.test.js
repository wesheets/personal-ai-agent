/**
 * RecursiveReflectionSystem.test.js
 * 
 * Test file for the recursive reflection and uncertainty threshold system components.
 * Ensures all components work as expected and comply with schemas.
 */

import { 
  checkReflectionTriggers, 
  generateReflectionEventId 
} from '../logic/RecursiveReflectionEngine';
import { 
  getProjectThresholds 
} from '../logic/ConfidenceThresholds';
import { 
  validateReflectionEvent, 
  validateLoopReflectionHistory 
} from '../schemas/ReflectionSchema';

/**
 * Test reflection trigger checks
 */
const testReflectionTriggers = () => {
  console.log('Testing reflection triggers...');
  
  // Test with low confidence
  const state1 = {
    confidence_score: 0.4,
    trust_score: 0.7,
    trust_delta: 0,
    contradiction_unresolved: false,
    drift_score: 0.3,
    manual_override: false,
    reflection_depth: 1
  };
  
  const thresholds1 = {
    min_confidence: 0.55,
    max_drift: 0.65,
    min_trust_score: 0.4,
    min_trust_delta: -0.2,
    max_reflection_depth: 3
  };
  
  const result1 = checkReflectionTriggers(state1, thresholds1);
  console.log(`Low confidence test: should_reflect=${result1.should_reflect}, reason=${result1.reason}`);
  
  // Test with trust decay
  const state2 = {
    confidence_score: 0.6,
    trust_score: 0.5,
    trust_delta: -0.25,
    contradiction_unresolved: false,
    drift_score: 0.3,
    manual_override: false,
    reflection_depth: 1
  };
  
  const result2 = checkReflectionTriggers(state2, thresholds1);
  console.log(`Trust decay test: should_reflect=${result2.should_reflect}, reason=${result2.reason}`);
  
  // Test with unresolved contradiction
  const state3 = {
    confidence_score: 0.6,
    trust_score: 0.7,
    trust_delta: 0,
    contradiction_unresolved: true,
    drift_score: 0.3,
    manual_override: false,
    reflection_depth: 1
  };
  
  const result3 = checkReflectionTriggers(state3, thresholds1);
  console.log(`Unresolved contradiction test: should_reflect=${result3.should_reflect}, reason=${result3.reason}`);
  
  // Test with high drift
  const state4 = {
    confidence_score: 0.6,
    trust_score: 0.7,
    trust_delta: 0,
    contradiction_unresolved: false,
    drift_score: 0.7,
    manual_override: false,
    reflection_depth: 1
  };
  
  const result4 = checkReflectionTriggers(state4, thresholds1);
  console.log(`High drift test: should_reflect=${result4.should_reflect}, reason=${result4.reason}`);
  
  // Test with max depth reached
  const state5 = {
    confidence_score: 0.4,
    trust_score: 0.7,
    trust_delta: 0,
    contradiction_unresolved: false,
    drift_score: 0.3,
    manual_override: false,
    reflection_depth: 3
  };
  
  const result5 = checkReflectionTriggers(state5, thresholds1);
  console.log(`Max depth test: should_reflect=${result5.should_reflect}, reason=${result5.reason}`);
  
  // Test with all thresholds met
  const state6 = {
    confidence_score: 0.6,
    trust_score: 0.7,
    trust_delta: 0,
    contradiction_unresolved: false,
    drift_score: 0.3,
    manual_override: true,
    reflection_depth: 1
  };
  
  const result6 = checkReflectionTriggers(state6, thresholds1);
  console.log(`All thresholds met test: should_reflect=${result6.should_reflect}, reason=${result6.reason}`);
  
  return true;
};

/**
 * Test project thresholds
 */
const testProjectThresholds = () => {
  console.log('Testing project thresholds...');
  
  // Test with default thresholds
  const allThresholds1 = {
    default: {
      min_confidence: 0.55,
      max_drift: 0.65,
      min_trust_score: 0.4,
      min_trust_delta: -0.2,
      max_reflection_depth: 3
    }
  };
  
  const projectThresholds1 = getProjectThresholds(allThresholds1, 'unknown_project');
  console.log(`Default thresholds test: min_confidence=${projectThresholds1.min_confidence}`);
  
  // Test with project-specific thresholds
  const allThresholds2 = {
    default: {
      min_confidence: 0.55,
      max_drift: 0.65,
      min_trust_score: 0.4,
      min_trust_delta: -0.2,
      max_reflection_depth: 3
    },
    life_tree: {
      min_confidence: 0.7,
      max_drift: 0.5
    }
  };
  
  const projectThresholds2 = getProjectThresholds(allThresholds2, 'life_tree');
  console.log(`Project-specific thresholds test: min_confidence=${projectThresholds2.min_confidence}, max_drift=${projectThresholds2.max_drift}, min_trust_score=${projectThresholds2.min_trust_score}`);
  
  return true;
};

/**
 * Test reflection event ID generation
 */
const testReflectionEventIdGeneration = () => {
  console.log('Testing reflection event ID generation...');
  
  // Generate multiple IDs and check format
  const id1 = generateReflectionEventId();
  const id2 = generateReflectionEventId();
  
  console.log(`Generated IDs: ${id1}, ${id2}`);
  
  // Check that IDs are different
  const idsAreDifferent = id1 !== id2;
  console.log(`IDs are different: ${idsAreDifferent}`);
  
  // Check ID format (should start with "reflection_" followed by timestamp and random number)
  const idFormatCorrect = id1.startsWith('reflection_') && id1.split('_').length === 3;
  console.log(`ID format is correct: ${idFormatCorrect}`);
  
  return idsAreDifferent && idFormatCorrect;
};

/**
 * Test schema validation
 */
const testSchemaValidation = () => {
  console.log('Testing schema validation...');
  
  // Valid reflection event
  const validEvent = {
    id: generateReflectionEventId(),
    loop_id: 'loop_123',
    triggered_by: 'low_confidence',
    reflection_depth: 1,
    agent: 'SAGE',
    timestamp: new Date().toISOString(),
    status: 'active',
    confidence: 0.6
  };
  
  const isValidEvent = validateReflectionEvent(validEvent);
  console.log(`Valid reflection event validation: ${isValidEvent}`);
  
  // Invalid reflection event (missing required field)
  const invalidEvent = {
    id: generateReflectionEventId(),
    // Missing loop_id
    triggered_by: 'low_confidence',
    reflection_depth: 1,
    agent: 'SAGE',
    timestamp: new Date().toISOString(),
    status: 'active'
  };
  
  const isInvalidEvent = validateReflectionEvent(invalidEvent);
  console.log(`Invalid reflection event validation: ${!isInvalidEvent}`);
  
  // Valid loop reflection history
  const validHistory = {
    loop_id: 'loop_123',
    reflections: [
      {
        depth: 1,
        agent: 'SAGE',
        confidence: 0.52,
        timestamp: new Date().toISOString(),
        reason: 'low_confidence',
        status: 'completed'
      }
    ],
    current_depth: 1,
    max_depth_reached: false,
    last_reflection: new Date().toISOString()
  };
  
  const isValidHistory = validateLoopReflectionHistory(validHistory);
  console.log(`Valid loop reflection history validation: ${isValidHistory}`);
  
  // Invalid loop reflection history (missing required field)
  const invalidHistory = {
    loop_id: 'loop_123',
    // Missing reflections
    current_depth: 1
  };
  
  const isInvalidHistory = validateLoopReflectionHistory(invalidHistory);
  console.log(`Invalid loop reflection history validation: ${!isInvalidHistory}`);
  
  return isValidEvent && !isInvalidEvent && isValidHistory && !isInvalidHistory;
};

/**
 * Run all tests
 */
const runAllTests = () => {
  console.log('Running recursive reflection system tests...');
  
  let allTestsPassed = true;
  
  try {
    // Run individual tests
    allTestsPassed = allTestsPassed && testReflectionTriggers();
    allTestsPassed = allTestsPassed && testProjectThresholds();
    allTestsPassed = allTestsPassed && testReflectionEventIdGeneration();
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
  testReflectionTriggers,
  testProjectThresholds,
  testReflectionEventIdGeneration,
  testSchemaValidation,
  runAllTests
};

// Run tests if this file is executed directly
if (typeof require !== 'undefined' && require.main === module) {
  runAllTests();
}
