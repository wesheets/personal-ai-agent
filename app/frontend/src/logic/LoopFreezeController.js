/**
 * LoopFreezeController.js
 * 
 * Core logic that monitors loop conditions and prevents execution when cognitive integrity is compromised.
 * Monitors confidence score, trust score, reflection depth, contradictions, and manual override.
 * If any condition is unmet, loop status is set to frozen and execution is prevented.
 */

import { useState, useEffect, useCallback } from 'react';
import { useRecursiveReflection } from './RecursiveReflectionEngine';
import { useTrust } from '../components/trust/TrustProvider';

// Default thresholds for freezing loops
const DEFAULT_FREEZE_THRESHOLDS = {
  min_confidence: 0.6,
  min_trust_score: 0.5,
  max_contradictions: 0,
  require_manual_override: false
};

/**
 * Generate a unique freeze event ID
 * @returns {string} A unique ID for the freeze event
 */
export const generateFreezeEventId = () => {
  return `freeze_${Date.now()}_${Math.floor(Math.random() * 10000)}`;
};

/**
 * Check if a loop should be frozen based on its state
 * 
 * @param {Object} loopState - Current state of the loop
 * @param {Object} thresholds - Thresholds for freezing
 * @returns {Object} Result with freeze status and reason
 */
export const checkFreezeTriggers = (loopState, thresholds = DEFAULT_FREEZE_THRESHOLDS) => {
  const {
    confidence_score = 0,
    trust_score = 0,
    reflection_depth = 0,
    contradictions_unresolved = 0,
    manual_override = false
  } = loopState;
  
  const reasons = [];
  
  // Check confidence score
  if (confidence_score < thresholds.min_confidence) {
    reasons.push('low_confidence');
  }
  
  // Check trust score
  if (trust_score < thresholds.min_trust_score) {
    reasons.push('low_trust');
  }
  
  // Check contradictions
  if (contradictions_unresolved > thresholds.max_contradictions) {
    reasons.push('unresolved_contradiction');
  }
  
  // Check manual override if required
  if (thresholds.require_manual_override && !manual_override) {
    reasons.push('no_manual_override');
  }
  
  // Determine if loop should be frozen
  const shouldFreeze = reasons.length > 0;
  
  // Determine required action
  let requiredAction = 'none';
  if (shouldFreeze) {
    if (reasons.includes('low_confidence') || reasons.includes('unresolved_contradiction')) {
      requiredAction = 're-reflect';
    } else if (reasons.includes('no_manual_override')) {
      requiredAction = 'operator_override';
    } else {
      requiredAction = 'operator_override';
    }
  }
  
  return {
    should_freeze: shouldFreeze,
    reasons: reasons,
    reason_text: reasons.join(' and '),
    required_action: requiredAction,
    details: shouldFreeze 
      ? `Loop frozen due to: ${reasons.join(', ')}`
      : 'Loop meets all execution criteria'
  };
};

/**
 * Hook for managing loop freezing
 * 
 * @param {Object} options - Configuration options
 * @param {Object} options.initialThresholds - Initial thresholds for freezing
 * @param {Function} options.onFreeze - Callback when a loop is frozen
 * @param {Function} options.onUnfreeze - Callback when a loop is unfrozen
 * @param {boolean} options.enabled - Whether freeze control is enabled
 * @returns {Object} Loop freeze state and functions
 */
export const useLoopFreezeController = ({
  initialThresholds = DEFAULT_FREEZE_THRESHOLDS,
  onFreeze = () => {},
  onUnfreeze = () => {},
  enabled = true
}) => {
  // State
  const [isEnabled, setIsEnabled] = useState(enabled);
  const [thresholds, setThresholds] = useState(initialThresholds);
  const [frozenLoops, setFrozenLoops] = useState({});
  const [freezeHistory, setFreezeHistory] = useState([]);
  
  // Get recursive reflection and trust data
  const { getActiveReflection } = useRecursiveReflection({});
  const { getTrustScore } = useTrust();
  
  /**
   * Check if a loop should be frozen
   * 
   * @param {string} loopId - ID of the loop to check
   * @param {Object} loopState - Current state of the loop
   * @returns {Object} Result with freeze status and reason
   */
  const checkLoopFreeze = useCallback((loopId, loopState) => {
    if (!isEnabled) {
      return {
        should_freeze: false,
        reasons: ['freeze_control_disabled'],
        reason_text: 'freeze control disabled',
        required_action: 'none',
        details: 'Loop freeze control is disabled'
      };
    }
    
    // Get active reflection
    const activeReflection = getActiveReflection(loopId);
    
    // Get trust score
    const agent = loopState.agent || 'SAGE';
    const trustScore = getTrustScore(agent);
    
    // Prepare complete loop state
    const completeLoopState = {
      ...loopState,
      trust_score: trustScore,
      reflection_depth: loopState.reflection_depth || 0,
      contradictions_unresolved: loopState.contradictions_unresolved || 0,
      // If there's an active reflection, the loop should be considered as having unresolved contradictions
      ...(activeReflection ? { contradictions_unresolved: 1 } : {})
    };
    
    // Check freeze triggers
    return checkFreezeTriggers(completeLoopState, thresholds);
  }, [isEnabled, thresholds, getActiveReflection, getTrustScore]);
  
  /**
   * Freeze a loop
   * 
   * @param {string} loopId - ID of the loop
   * @param {Object} loopState - Current state of the loop
   * @param {Array} reasons - Reasons for freezing
   * @param {string} requiredAction - Action required to unfreeze
   * @returns {Object} Freeze event
   */
  const freezeLoop = useCallback((loopId, loopState, reasons, requiredAction) => {
    // Skip if loop is already frozen
    if (frozenLoops[loopId]) {
      return frozenLoops[loopId];
    }
    
    // Create freeze event
    const freezeEvent = {
      id: generateFreezeEventId(),
      loop_id: loopId,
      status: 'frozen',
      reason: reasons.join(' and '),
      reasons: reasons,
      timestamp: new Date().toISOString(),
      required_action: requiredAction,
      agent: loopState.agent || 'SAGE',
      project_id: loopState.project_id || 'default',
      original_state: { ...loopState }
    };
    
    // Update frozen loops
    setFrozenLoops(prev => ({
      ...prev,
      [loopId]: freezeEvent
    }));
    
    // Update freeze history
    setFreezeHistory(prev => [...prev, freezeEvent]);
    
    // Call freeze callback
    onFreeze(freezeEvent);
    
    console.log(`Frozen loop ${loopId} due to ${reasons.join(', ')}. Required action: ${requiredAction}`);
    
    return freezeEvent;
  }, [frozenLoops, onFreeze]);
  
  /**
   * Unfreeze a loop
   * 
   * @param {string} loopId - ID of the loop
   * @param {string} reason - Reason for unfreezing
   * @param {boolean} isManualOverride - Whether this is a manual override
   * @returns {Object} Updated freeze event
   */
  const unfreezeLoop = useCallback((loopId, reason = 'conditions_met', isManualOverride = false) => {
    // Skip if loop is not frozen
    if (!frozenLoops[loopId]) {
      console.warn(`Loop ${loopId} is not frozen`);
      return null;
    }
    
    // Get frozen loop
    const frozenLoop = frozenLoops[loopId];
    
    // Create updated freeze event
    const updatedEvent = {
      ...frozenLoop,
      status: 'unfrozen',
      unfrozen_at: new Date().toISOString(),
      unfreeze_reason: reason,
      manual_override: isManualOverride
    };
    
    // Remove from frozen loops
    setFrozenLoops(prev => {
      const newFrozen = { ...prev };
      delete newFrozen[loopId];
      return newFrozen;
    });
    
    // Update freeze history
    setFreezeHistory(prev => 
      prev.map(event => 
        event.id === frozenLoop.id ? updatedEvent : event
      )
    );
    
    // Call unfreeze callback
    onUnfreeze(updatedEvent);
    
    console.log(`Unfrozen loop ${loopId} due to ${reason}. Manual override: ${isManualOverride}`);
    
    return updatedEvent;
  }, [frozenLoops, onUnfreeze]);
  
  /**
   * Process a loop state and freeze if needed
   * 
   * @param {string} loopId - ID of the loop
   * @param {Object} loopState - Current state of the loop
   * @returns {Object} Processing result
   */
  const processLoopState = useCallback((loopId, loopState) => {
    // Skip if loop is already frozen
    if (frozenLoops[loopId]) {
      return {
        action: 'frozen',
        freeze: frozenLoops[loopId],
        message: 'Loop already frozen'
      };
    }
    
    // Check if loop should be frozen
    const checkResult = checkLoopFreeze(loopId, loopState);
    
    if (checkResult.should_freeze) {
      // Freeze loop
      const freeze = freezeLoop(loopId, loopState, checkResult.reasons, checkResult.required_action);
      
      return {
        action: 'freeze',
        freeze,
        message: checkResult.details
      };
    }
    
    return {
      action: 'proceed',
      message: checkResult.details
    };
  }, [frozenLoops, checkLoopFreeze, freezeLoop]);
  
  /**
   * Check if a loop is frozen
   * 
   * @param {string} loopId - ID of the loop
   * @returns {boolean} Whether the loop is frozen
   */
  const isLoopFrozen = useCallback((loopId) => {
    return !!frozenLoops[loopId];
  }, [frozenLoops]);
  
  /**
   * Get freeze event for a loop
   * 
   * @param {string} loopId - ID of the loop
   * @returns {Object|null} Freeze event or null if not frozen
   */
  const getLoopFreezeEvent = useCallback((loopId) => {
    return frozenLoops[loopId] || null;
  }, [frozenLoops]);
  
  /**
   * Get freeze history for a loop
   * 
   * @param {string} loopId - ID of the loop
   * @returns {Array} Freeze history for the loop
   */
  const getLoopFreezeHistory = useCallback((loopId) => {
    return freezeHistory.filter(event => event.loop_id === loopId);
  }, [freezeHistory]);
  
  /**
   * Get all freeze history
   * 
   * @returns {Array} All freeze history
   */
  const getAllFreezeHistory = useCallback(() => {
    return freezeHistory;
  }, [freezeHistory]);
  
  /**
   * Update thresholds
   * 
   * @param {Object} newThresholds - New thresholds
   */
  const updateThresholds = useCallback((newThresholds) => {
    setThresholds(prev => ({
      ...prev,
      ...newThresholds
    }));
  }, []);
  
  /**
   * Enable freeze control
   */
  const enable = useCallback(() => {
    setIsEnabled(true);
  }, []);
  
  /**
   * Disable freeze control
   */
  const disable = useCallback(() => {
    setIsEnabled(false);
  }, []);
  
  /**
   * Override a frozen loop
   * 
   * @param {string} loopId - ID of the loop
   * @param {string} reason - Reason for override
   * @returns {Object} Updated freeze event
   */
  const overrideFreeze = useCallback((loopId, reason = 'manual_operator_override') => {
    return unfreezeLoop(loopId, reason, true);
  }, [unfreezeLoop]);
  
  /**
   * Check if a loop can execute
   * 
   * @param {string} loopId - ID of the loop
   * @param {Object} loopState - Current state of the loop
   * @returns {Object} Result with can_execute status and reason
   */
  const canLoopExecute = useCallback((loopId, loopState) => {
    // If loop is frozen, it cannot execute
    if (isLoopFrozen(loopId)) {
      const freezeEvent = getLoopFreezeEvent(loopId);
      return {
        can_execute: false,
        reason: freezeEvent.reason,
        required_action: freezeEvent.required_action,
        freeze_event: freezeEvent
      };
    }
    
    // Check if loop should be frozen
    const checkResult = checkLoopFreeze(loopId, loopState);
    
    if (checkResult.should_freeze) {
      // Freeze loop
      const freeze = freezeLoop(loopId, loopState, checkResult.reasons, checkResult.required_action);
      
      return {
        can_execute: false,
        reason: checkResult.reason_text,
        required_action: checkResult.required_action,
        freeze_event: freeze
      };
    }
    
    // Loop can execute
    return {
      can_execute: true,
      reason: 'all_conditions_met'
    };
  }, [isLoopFrozen, getLoopFreezeEvent, checkLoopFreeze, freezeLoop]);
  
  // Return public API
  return {
    isEnabled,
    thresholds,
    frozenLoops,
    freezeHistory,
    checkLoopFreeze,
    freezeLoop,
    unfreezeLoop,
    processLoopState,
    isLoopFrozen,
    getLoopFreezeEvent,
    getLoopFreezeHistory,
    getAllFreezeHistory,
    updateThresholds,
    enable,
    disable,
    overrideFreeze,
    canLoopExecute
  };
};

export default {
  useLoopFreezeController,
  checkFreezeTriggers,
  generateFreezeEventId,
  DEFAULT_FREEZE_THRESHOLDS
};
