/**
 * FreezeSystem.test.js
 * 
 * Test file for the reflection freeze lock system components.
 * Ensures all components work as expected and comply with schemas.
 */

import { 
  checkFreezeTriggers, 
  generateFreezeEventId 
} from '../logic/LoopFreezeController';
import { 
  validateFreezeEvent, 
  validateFreezeStatus 
} from '../schemas/FreezeStatusSchema';
import {
  validateFreeze,
  validateStatus,
  validateFreezeLog
} from '../utils/FreezeSchemaValidator';
import freezeLogData from '../data/FreezeLog.json';

/**
 * Test freeze trigger checks
 */
const testFreezeTriggers = () => {
  console.log('Testing freeze triggers...');
  
  // Test with low confidence
  const state1 = {
    confidence_score: 0.4,
    trust_score: 0.7,
    reflection_depth: 1,
    contradictions_unresolved: 0,
    manual_override: false
  };
  
  const thresholds1 = {
    min_confidence: 0.6,
    min_trust_score: 0.5,
    max_contradictions: 0,
    require_manual_override: false
  };
  
  const result1 = checkFreezeTriggers(state1, thresholds1);
  console.log(`Low confidence test: should_freeze=${result1.should_freeze}, reason=${result1.reason_text}`);
  
  // Test with low trust
  const state2 = {
    confidence_score: 0.7,
    trust_score: 0.4,
    reflection_depth: 1,
    contradictions_unresolved: 0,
    manual_override: false
  };
  
  const result2 = checkFreezeTriggers(state2, thresholds1);
  console.log(`Low trust test: should_freeze=${result2.should_freeze}, reason=${result2.reason_text}`);
  
  // Test with unresolved contradictions
  const state3 = {
    confidence_score: 0.7,
    trust_score: 0.7,
    reflection_depth: 1,
    contradictions_unresolved: 2,
    manual_override: false
  };
  
  const result3 = checkFreezeTriggers(state3, thresholds1);
  console.log(`Unresolved contradictions test: should_freeze=${result3.should_freeze}, reason=${result3.reason_text}`);
  
  // Test with required manual override
  const state4 = {
    confidence_score: 0.7,
    trust_score: 0.7,
    reflection_depth: 1,
    contradictions_unresolved: 0,
    manual_override: false
  };
  
  const thresholds2 = {
    ...thresholds1,
    require_manual_override: true
  };
  
  const result4 = checkFreezeTriggers(state4, thresholds2);
  console.log(`Required manual override test: should_freeze=${result4.should_freeze}, reason=${result4.reason_text}`);
  
  // Test with all conditions met
  const state5 = {
    confidence_score: 0.7,
    trust_score: 0.7,
    reflection_depth: 1,
    contradictions_unresolved: 0,
    manual_override: true
  };
  
  const result5 = checkFreezeTriggers(state5, thresholds2);
  console.log(`All conditions met test: should_freeze=${result5.should_freeze}, reason=${result5.reason_text}`);
  
  // Verify results
  const allTestsPassed = 
    result1.should_freeze === true &&
    result2.should_freeze === true &&
    result3.should_freeze === true &&
    result4.should_freeze === true &&
    result5.should_freeze === false;
  
  console.log(`All freeze trigger tests passed: ${allTestsPassed}`);
  
  return allTestsPassed;
};

/**
 * Test freeze event ID generation
 */
const testFreezeEventIdGeneration = () => {
  console.log('Testing freeze event ID generation...');
  
  // Generate multiple IDs and check format
  const id1 = generateFreezeEventId();
  const id2 = generateFreezeEventId();
  
  console.log(`Generated IDs: ${id1}, ${id2}`);
  
  // Check that IDs are different
  const idsAreDifferent = id1 !== id2;
  console.log(`IDs are different: ${idsAreDifferent}`);
  
  // Check ID format (should start with "freeze_" followed by timestamp and random number)
  const idFormatCorrect = id1.startsWith('freeze_') && id1.split('_').length === 3;
  console.log(`ID format is correct: ${idFormatCorrect}`);
  
  return idsAreDifferent && idFormatCorrect;
};

/**
 * Test schema validation
 */
const testSchemaValidation = () => {
  console.log('Testing schema validation...');
  
  // Valid freeze event
  const validEvent = {
    id: generateFreezeEventId(),
    loop_id: 'loop_123',
    status: 'frozen',
    reason: 'low confidence',
    reasons: ['low_confidence'],
    timestamp: new Date().toISOString(),
    required_action: 're-reflect',
    agent: 'SAGE',
    project_id: 'life_tree',
    original_state: {
      confidence_score: 0.4,
      trust_score: 0.7,
      reflection_depth: 1,
      contradictions_unresolved: 0,
      manual_override: false
    }
  };
  
  const isValidEvent = validateFreezeEvent(validEvent);
  console.log(`Valid freeze event validation: ${isValidEvent}`);
  
  // Invalid freeze event (missing required field)
  const invalidEvent = {
    id: generateFreezeEventId(),
    // Missing loop_id
    status: 'frozen',
    reason: 'low confidence',
    timestamp: new Date().toISOString(),
    required_action: 're-reflect'
  };
  
  const isInvalidEvent = validateFreezeEvent(invalidEvent);
  console.log(`Invalid freeze event validation: ${!isInvalidEvent}`);
  
  // Valid freeze status
  const validStatus = {
    loop_id: 'loop_123',
    status: 'frozen',
    reason: 'low confidence',
    timestamp: new Date().toISOString(),
    required_action: 're-reflect'
  };
  
  const isValidStatus = validateFreezeStatus(validStatus);
  console.log(`Valid freeze status validation: ${isValidStatus}`);
  
  // Invalid freeze status (missing required field)
  const invalidStatus = {
    loop_id: 'loop_123',
    // Missing status
    reason: 'low confidence',
    timestamp: new Date().toISOString()
  };
  
  const isInvalidStatus = validateFreezeStatus(invalidStatus);
  console.log(`Invalid freeze status validation: ${!isInvalidStatus}`);
  
  return isValidEvent && !isInvalidEvent && isValidStatus && !isInvalidStatus;
};

/**
 * Test freeze log validation
 */
const testFreezeLogValidation = () => {
  console.log('Testing freeze log validation...');
  
  // Validate freeze log data
  const logValidation = validateFreezeLog(freezeLogData);
  
  console.log(`Freeze log validation: isValid=${logValidation.isValid}, validEvents=${logValidation.validEvents.length}, invalidEvents=${logValidation.invalidEvents.length}`);
  
  if (logValidation.invalidEvents.length > 0) {
    console.log('Invalid events:');
    logValidation.invalidEvents.forEach(({ event, errors }) => {
      console.log(`- Event ID ${event.id}: ${errors.join(', ')}`);
    });
  }
  
  if (logValidation.errors.length > 0) {
    console.log('Log errors:');
    logValidation.errors.forEach(error => {
      console.log(`- ${error}`);
    });
  }
  
  return logValidation.isValid;
};

/**
 * Test utility functions
 */
const testUtilityFunctions = () => {
  console.log('Testing utility functions...');
  
  // Test validateFreeze
  const validEvent = {
    id: generateFreezeEventId(),
    loop_id: 'loop_123',
    status: 'frozen',
    reason: 'low confidence',
    reasons: ['low_confidence'],
    timestamp: new Date().toISOString(),
    required_action: 're-reflect',
    agent: 'SAGE',
    project_id: 'life_tree',
    original_state: {
      confidence_score: 0.4,
      trust_score: 0.7,
      reflection_depth: 1,
      contradictions_unresolved: 0,
      manual_override: false
    }
  };
  
  const freezeValidation = validateFreeze(validEvent);
  console.log(`validateFreeze: isValid=${freezeValidation.isValid}, errors=${freezeValidation.errors.length}`);
  
  // Test validateStatus
  const validStatus = {
    loop_id: 'loop_123',
    status: 'frozen',
    reason: 'low confidence',
    timestamp: new Date().toISOString(),
    required_action: 're-reflect'
  };
  
  const statusValidation = validateStatus(validStatus);
  console.log(`validateStatus: isValid=${statusValidation.isValid}, errors=${statusValidation.errors.length}`);
  
  return freezeValidation.isValid && statusValidation.isValid;
};

/**
 * Run all tests
 */
const runAllTests = () => {
  console.log('Running freeze lock system tests...');
  
  let allTestsPassed = true;
  
  try {
    // Run individual tests
    allTestsPassed = allTestsPassed && testFreezeTriggers();
    allTestsPassed = allTestsPassed && testFreezeEventIdGeneration();
    allTestsPassed = allTestsPassed && testSchemaValidation();
    allTestsPassed = allTestsPassed && testFreezeLogValidation();
    allTestsPassed = allTestsPassed && testUtilityFunctions();
    
    console.log(`\nAll tests ${allTestsPassed ? 'PASSED' : 'FAILED'}`);
  } catch (error) {
    console.error('Error running tests:', error);
    allTestsPassed = false;
  }
  
  return allTestsPassed;
};

// Export test functions
export {
  testFreezeTriggers,
  testFreezeEventIdGeneration,
  testSchemaValidation,
  testFreezeLogValidation,
  testUtilityFunctions,
  runAllTests
};

// Run tests if this file is executed directly
if (typeof require !== 'undefined' && require.main === module) {
  runAllTests();
}
