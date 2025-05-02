/**
 * RecursiveReflectionEngine.js
 * 
 * Core logic that monitors loop resolution state and triggers new reflections when:
 * - Trust score decays
 * - Contradictions are unresolved
 * - Reflection confidence is low
 * - Operator hasn't explicitly approved
 * - Output plan fails schema or memory test
 */

import { useState, useEffect, useCallback } from 'react';
import { useTrust } from '../components/trust/TrustProvider';

// Default thresholds
const DEFAULT_THRESHOLDS = {
  min_confidence: 0.55,
  max_drift: 0.65,
  min_trust_score: 0.4,
  min_trust_delta: -0.2,
  max_reflection_depth: 3
};

/**
 * Generate a unique reflection event ID
 * @returns {string} A unique ID for the reflection event
 */
export const generateReflectionEventId = () => {
  return `reflection_${Date.now()}_${Math.floor(Math.random() * 10000)}`;
};

/**
 * Check if a loop needs additional reflection based on its state
 * 
 * @param {Object} loopState - Current state of the loop
 * @param {Object} thresholds - Thresholds for triggering reflection
 * @returns {Object} Result with trigger status and reason
 */
export const checkReflectionTriggers = (loopState, thresholds = DEFAULT_THRESHOLDS) => {
  const {
    confidence_score = 1,
    trust_score = 1,
    trust_delta = 0,
    contradiction_unresolved = false,
    drift_score = 0,
    manual_override = false,
    reflection_depth = 0
  } = loopState;
  
  // Check if we've reached max reflection depth
  if (reflection_depth >= thresholds.max_reflection_depth) {
    return {
      should_reflect: false,
      reason: 'max_depth_reached',
      details: `Maximum reflection depth (${thresholds.max_reflection_depth}) reached`
    };
  }
  
  // Check confidence score
  if (confidence_score < thresholds.min_confidence) {
    return {
      should_reflect: true,
      reason: 'low_confidence',
      details: `Confidence score (${confidence_score.toFixed(2)}) below threshold (${thresholds.min_confidence})`
    };
  }
  
  // Check trust delta
  if (trust_delta < thresholds.min_trust_delta) {
    return {
      should_reflect: true,
      reason: 'trust_decay',
      details: `Trust delta (${trust_delta.toFixed(2)}) below threshold (${thresholds.min_trust_delta})`
    };
  }
  
  // Check trust score
  if (trust_score < thresholds.min_trust_score) {
    return {
      should_reflect: true,
      reason: 'low_trust',
      details: `Trust score (${trust_score.toFixed(2)}) below threshold (${thresholds.min_trust_score})`
    };
  }
  
  // Check contradiction status
  if (contradiction_unresolved) {
    return {
      should_reflect: true,
      reason: 'unresolved_contradiction',
      details: 'Unresolved contradiction detected'
    };
  }
  
  // Check drift score
  if (drift_score > thresholds.max_drift) {
    return {
      should_reflect: true,
      reason: 'high_drift',
      details: `Drift score (${drift_score.toFixed(2)}) above threshold (${thresholds.max_drift})`
    };
  }
  
  // Check manual override
  if (!manual_override) {
    // Only trigger on lack of manual override if other factors are close to thresholds
    const confidenceMargin = thresholds.min_confidence + 0.1;
    const driftMargin = thresholds.max_drift - 0.1;
    
    if (confidence_score < confidenceMargin || drift_score > driftMargin) {
      return {
        should_reflect: true,
        reason: 'no_manual_override',
        details: 'No manual override with borderline metrics'
      };
    }
  }
  
  // No triggers found
  return {
    should_reflect: false,
    reason: 'all_thresholds_met',
    details: 'All thresholds met, no reflection needed'
  };
};

/**
 * Hook for managing recursive reflection
 * 
 * @param {Object} options - Configuration options
 * @param {Object} options.initialThresholds - Initial thresholds for triggering reflection
 * @param {Function} options.onReflectionTriggered - Callback when reflection is triggered
 * @param {Function} options.onReflectionComplete - Callback when reflection is complete
 * @param {boolean} options.enabled - Whether recursive reflection is enabled
 * @returns {Object} Recursive reflection state and functions
 */
export const useRecursiveReflection = ({
  initialThresholds = DEFAULT_THRESHOLDS,
  onReflectionTriggered = () => {},
  onReflectionComplete = () => {},
  enabled = true
}) => {
  // State
  const [isEnabled, setIsEnabled] = useState(enabled);
  const [thresholds, setThresholds] = useState(initialThresholds);
  const [activeReflections, setActiveReflections] = useState({});
  const [reflectionHistory, setReflectionHistory] = useState([]);
  
  // Get trust data
  const { getTrustScore, getTrustHistory } = useTrust();
  
  /**
   * Check if a loop needs additional reflection
   * 
   * @param {string} loopId - ID of the loop to check
   * @param {Object} loopState - Current state of the loop
   * @returns {Object} Result with trigger status and reason
   */
  const checkLoopReflectionNeeded = useCallback((loopId, loopState) => {
    if (!isEnabled) {
      return {
        should_reflect: false,
        reason: 'reflection_disabled',
        details: 'Recursive reflection is disabled'
      };
    }
    
    // Get loop-specific thresholds
    const loopThresholds = {
      ...thresholds,
      ...(loopState.project_id && thresholds[loopState.project_id] ? thresholds[loopState.project_id] : {})
    };
    
    // Get trust score and history
    const agent = loopState.agent || 'SAGE';
    const trustScore = getTrustScore(agent);
    const trustHistory = getTrustHistory(agent);
    
    // Calculate trust delta
    let trustDelta = 0;
    if (trustHistory && trustHistory.length >= 2) {
      const latestTrust = trustHistory[trustHistory.length - 1];
      const previousTrust = trustHistory[trustHistory.length - 2];
      
      if (latestTrust && previousTrust) {
        trustDelta = latestTrust.trust_score - previousTrust.trust_score;
      }
    }
    
    // Prepare complete loop state
    const completeLoopState = {
      ...loopState,
      trust_score: trustScore,
      trust_delta: trustDelta,
      reflection_depth: loopState.reflection_depth || 0
    };
    
    // Check reflection triggers
    return checkReflectionTriggers(completeLoopState, loopThresholds);
  }, [isEnabled, thresholds, getTrustScore, getTrustHistory]);
  
  /**
   * Trigger a reflection for a loop
   * 
   * @param {string} loopId - ID of the loop
   * @param {Object} loopState - Current state of the loop
   * @param {string} reason - Reason for triggering reflection
   * @returns {Object} Reflection event
   */
  const triggerReflection = useCallback((loopId, loopState, reason) => {
    // Skip if reflection is already active for this loop
    if (activeReflections[loopId]) {
      return activeReflections[loopId];
    }
    
    // Create reflection event
    const reflectionEvent = {
      id: generateReflectionEventId(),
      loop_id: loopId,
      triggered_by: reason,
      reflection_depth: (loopState.reflection_depth || 0) + 1,
      agent: loopState.agent || 'SAGE',
      project_id: loopState.project_id || 'default',
      timestamp: new Date().toISOString(),
      status: 'active',
      original_state: { ...loopState }
    };
    
    // Update active reflections
    setActiveReflections(prev => ({
      ...prev,
      [loopId]: reflectionEvent
    }));
    
    // Update reflection history
    setReflectionHistory(prev => [...prev, reflectionEvent]);
    
    // Call reflection triggered callback
    onReflectionTriggered(reflectionEvent);
    
    console.log(`Triggered reflection for loop ${loopId} due to ${reason}. Depth: ${reflectionEvent.reflection_depth}`);
    
    return reflectionEvent;
  }, [activeReflections, onReflectionTriggered]);
  
  /**
   * Complete a reflection for a loop
   * 
   * @param {string} loopId - ID of the loop
   * @param {Object} reflectionResult - Result of the reflection
   * @returns {Object} Updated reflection event
   */
  const completeReflection = useCallback((loopId, reflectionResult) => {
    // Skip if no active reflection for this loop
    if (!activeReflections[loopId]) {
      console.warn(`No active reflection found for loop ${loopId}`);
      return null;
    }
    
    // Get active reflection
    const activeReflection = activeReflections[loopId];
    
    // Create updated reflection event
    const updatedReflection = {
      ...activeReflection,
      status: 'completed',
      completed_at: new Date().toISOString(),
      result: reflectionResult,
      confidence: reflectionResult.confidence_score || 0
    };
    
    // Remove from active reflections
    setActiveReflections(prev => {
      const newActive = { ...prev };
      delete newActive[loopId];
      return newActive;
    });
    
    // Update reflection history
    setReflectionHistory(prev => 
      prev.map(event => 
        event.id === activeReflection.id ? updatedReflection : event
      )
    );
    
    // Call reflection complete callback
    onReflectionComplete(updatedReflection);
    
    console.log(`Completed reflection for loop ${loopId}. New confidence: ${updatedReflection.confidence.toFixed(2)}`);
    
    return updatedReflection;
  }, [activeReflections, onReflectionComplete]);
  
  /**
   * Cancel a reflection for a loop
   * 
   * @param {string} loopId - ID of the loop
   * @param {string} reason - Reason for cancellation
   * @returns {Object} Updated reflection event
   */
  const cancelReflection = useCallback((loopId, reason = 'manual_cancellation') => {
    // Skip if no active reflection for this loop
    if (!activeReflections[loopId]) {
      console.warn(`No active reflection found for loop ${loopId}`);
      return null;
    }
    
    // Get active reflection
    const activeReflection = activeReflections[loopId];
    
    // Create updated reflection event
    const updatedReflection = {
      ...activeReflection,
      status: 'cancelled',
      cancelled_at: new Date().toISOString(),
      cancellation_reason: reason
    };
    
    // Remove from active reflections
    setActiveReflections(prev => {
      const newActive = { ...prev };
      delete newActive[loopId];
      return newActive;
    });
    
    // Update reflection history
    setReflectionHistory(prev => 
      prev.map(event => 
        event.id === activeReflection.id ? updatedReflection : event
      )
    );
    
    console.log(`Cancelled reflection for loop ${loopId} due to ${reason}`);
    
    return updatedReflection;
  }, [activeReflections]);
  
  /**
   * Process a loop state and trigger reflection if needed
   * 
   * @param {string} loopId - ID of the loop
   * @param {Object} loopState - Current state of the loop
   * @returns {Object} Processing result
   */
  const processLoopState = useCallback((loopId, loopState) => {
    // Skip if reflection is already active for this loop
    if (activeReflections[loopId]) {
      return {
        action: 'wait',
        reflection: activeReflections[loopId],
        message: 'Reflection already in progress'
      };
    }
    
    // Check if reflection is needed
    const checkResult = checkLoopReflectionNeeded(loopId, loopState);
    
    if (checkResult.should_reflect) {
      // Trigger reflection
      const reflection = triggerReflection(loopId, loopState, checkResult.reason);
      
      return {
        action: 'reflect',
        reflection,
        message: checkResult.details
      };
    }
    
    return {
      action: 'proceed',
      message: checkResult.details
    };
  }, [activeReflections, checkLoopReflectionNeeded, triggerReflection]);
  
  /**
   * Get active reflection for a loop
   * 
   * @param {string} loopId - ID of the loop
   * @returns {Object|null} Active reflection or null if none
   */
  const getActiveReflection = useCallback((loopId) => {
    return activeReflections[loopId] || null;
  }, [activeReflections]);
  
  /**
   * Get reflection history for a loop
   * 
   * @param {string} loopId - ID of the loop
   * @returns {Array} Reflection history for the loop
   */
  const getLoopReflectionHistory = useCallback((loopId) => {
    return reflectionHistory.filter(event => event.loop_id === loopId);
  }, [reflectionHistory]);
  
  /**
   * Get all reflection history
   * 
   * @returns {Array} All reflection history
   */
  const getAllReflectionHistory = useCallback(() => {
    return reflectionHistory;
  }, [reflectionHistory]);
  
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
   * Enable recursive reflection
   */
  const enable = useCallback(() => {
    setIsEnabled(true);
  }, []);
  
  /**
   * Disable recursive reflection
   */
  const disable = useCallback(() => {
    setIsEnabled(false);
  }, []);
  
  // Return public API
  return {
    isEnabled,
    thresholds,
    activeReflections,
    reflectionHistory,
    checkLoopReflectionNeeded,
    triggerReflection,
    completeReflection,
    cancelReflection,
    processLoopState,
    getActiveReflection,
    getLoopReflectionHistory,
    getAllReflectionHistory,
    updateThresholds,
    enable,
    disable
  };
};

export default {
  useRecursiveReflection,
  checkReflectionTriggers,
  generateReflectionEventId,
  DEFAULT_THRESHOLDS
};
