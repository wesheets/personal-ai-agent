/**
 * TrustScoreEvaluator.js
 * 
 * Core logic for scoring agents based on cognitive performance metrics:
 * - Summary realism
 * - Loop success
 * - Reflection clarity
 * - Contradiction frequency
 * - Revision rate
 * - Operator override history
 */

import { useState, useEffect, useCallback } from 'react';

// Default weights for different performance factors
const DEFAULT_WEIGHTS = {
  summary_realism: 0.15,
  loop_success: 0.20,
  reflection_clarity: 0.15,
  contradiction_frequency: 0.20,
  revision_rate: 0.15,
  operator_override: 0.15
};

// Default thresholds for trust score actions
const DEFAULT_THRESHOLDS = {
  demotion: 0.4,
  warning: 0.6,
  promotion: 0.85
};

// Default decay rate for trust scores (per loop)
const DEFAULT_DECAY_RATE = 0.02;

// Default persistence (number of loops that a trust change affects)
const DEFAULT_PERSISTENCE = 5;

/**
 * Generate a unique trust event ID
 * @returns {string} A unique ID for the trust event
 */
export const generateTrustEventId = () => {
  return `trust_${Date.now()}_${Math.floor(Math.random() * 10000)}`;
};

/**
 * Calculate a weighted trust score based on performance metrics
 * 
 * @param {Object} metrics - Performance metrics for an agent
 * @param {Object} weights - Weights for different metrics (optional)
 * @returns {number} Calculated trust score (0-1)
 */
export const calculateTrustScore = (metrics, weights = DEFAULT_WEIGHTS) => {
  // Ensure all required metrics are present
  const defaultMetrics = {
    summary_realism: 0.5,
    loop_success: 0.5,
    reflection_clarity: 0.5,
    contradiction_frequency: 0,
    revision_rate: 0,
    operator_override: 0
  };
  
  // Merge provided metrics with defaults
  const mergedMetrics = { ...defaultMetrics, ...metrics };
  
  // Calculate weighted score
  let weightedScore = 0;
  let totalWeight = 0;
  
  Object.keys(weights).forEach(key => {
    if (mergedMetrics[key] !== undefined) {
      // For negative factors (contradiction, revision, override), invert the scale
      const isNegativeFactor = ['contradiction_frequency', 'revision_rate', 'operator_override'].includes(key);
      const value = isNegativeFactor ? 1 - mergedMetrics[key] : mergedMetrics[key];
      
      weightedScore += value * weights[key];
      totalWeight += weights[key];
    }
  });
  
  // Normalize score if weights don't sum to 1
  if (totalWeight > 0 && totalWeight !== 1) {
    weightedScore = weightedScore / totalWeight;
  }
  
  // Ensure score is within 0-1 range
  return Math.max(0, Math.min(1, weightedScore));
};

/**
 * Calculate trust score delta based on previous score
 * 
 * @param {number} currentScore - Current trust score
 * @param {number} previousScore - Previous trust score
 * @returns {number} Trust score delta
 */
export const calculateTrustDelta = (currentScore, previousScore) => {
  return previousScore !== undefined ? currentScore - previousScore : 0;
};

/**
 * Determine reason for trust score change
 * 
 * @param {Object} metrics - Performance metrics for an agent
 * @param {number} delta - Trust score delta
 * @returns {string} Reason for trust score change
 */
export const determineTrustChangeReason = (metrics, delta) => {
  if (Math.abs(delta) < 0.01) {
    return 'no significant change';
  }
  
  // Find the metric with the largest contribution to change
  const contributingFactors = [];
  
  if (metrics.contradiction_frequency > 0.3) {
    contributingFactors.push('contradiction detected');
  }
  
  if (metrics.revision_rate > 0.3) {
    contributingFactors.push('high revision rate');
  }
  
  if (metrics.operator_override > 0.3) {
    contributingFactors.push('operator override');
  }
  
  if (metrics.summary_realism < 0.4) {
    contributingFactors.push('low summary realism');
  }
  
  if (metrics.loop_success < 0.4) {
    contributingFactors.push('loop failure');
  }
  
  if (metrics.reflection_clarity < 0.4) {
    contributingFactors.push('unclear reflection');
  }
  
  if (contributingFactors.length === 0) {
    return delta > 0 ? 'consistent performance' : 'performance decay';
  }
  
  return contributingFactors.join(' + ');
};

/**
 * Hook for evaluating and tracking agent trust scores
 * 
 * @param {Object} options - Configuration options
 * @param {Object} options.initialScores - Initial trust scores for agents
 * @param {Object} options.weights - Weights for different metrics
 * @param {Object} options.thresholds - Thresholds for trust score actions
 * @param {number} options.decayRate - Rate at which trust decays over time
 * @param {number} options.persistence - Number of loops that a trust change affects
 * @param {Function} options.onTrustChange - Callback when trust score changes
 * @param {Function} options.onAgentDemotion - Callback when agent is demoted
 * @returns {Object} Trust evaluation state and functions
 */
export const useTrustScoreEvaluator = ({
  initialScores = {},
  weights = DEFAULT_WEIGHTS,
  thresholds = DEFAULT_THRESHOLDS,
  decayRate = DEFAULT_DECAY_RATE,
  persistence = DEFAULT_PERSISTENCE,
  onTrustChange = () => {},
  onAgentDemotion = () => {}
}) => {
  // State for trust scores
  const [trustScores, setTrustScores] = useState(initialScores);
  const [trustHistory, setTrustHistory] = useState({});
  const [demotedAgents, setDemotedAgents] = useState({});
  
  /**
   * Evaluate trust for an agent based on performance metrics
   * 
   * @param {string} agent - Agent identifier
   * @param {Object} metrics - Performance metrics
   * @param {string} loopId - ID of the current loop
   * @returns {Object} Updated trust information
   */
  const evaluateTrust = useCallback((agent, metrics, loopId) => {
    // Get previous trust score
    const previousScore = trustScores[agent] || 0.7; // Default starting trust
    
    // Calculate new trust score
    const newScore = calculateTrustScore(metrics, weights);
    
    // Calculate delta
    const delta = calculateTrustDelta(newScore, previousScore);
    
    // Determine reason for change
    const reason = determineTrustChangeReason(metrics, delta);
    
    // Create trust event
    const trustEvent = {
      id: generateTrustEventId(),
      agent,
      loop_id: loopId,
      trust_score: newScore,
      delta,
      reason,
      timestamp: new Date().toISOString(),
      status: demotedAgents[agent] ? 'demoted' : 'active',
      metrics: { ...metrics }
    };
    
    // Update trust scores
    setTrustScores(prev => ({
      ...prev,
      [agent]: newScore
    }));
    
    // Update trust history
    setTrustHistory(prev => ({
      ...prev,
      [agent]: [...(prev[agent] || []), trustEvent]
    }));
    
    // Check for demotion
    if (newScore < thresholds.demotion && !demotedAgents[agent]) {
      setDemotedAgents(prev => ({
        ...prev,
        [agent]: {
          timestamp: new Date().toISOString(),
          reason,
          score: newScore
        }
      }));
      
      // Call demotion callback
      onAgentDemotion({
        agent,
        trust_score: newScore,
        reason,
        loop_id: loopId
      });
    }
    
    // Check for promotion (if previously demoted)
    if (newScore > thresholds.promotion && demotedAgents[agent]) {
      setDemotedAgents(prev => {
        const newDemoted = { ...prev };
        delete newDemoted[agent];
        return newDemoted;
      });
    }
    
    // Call trust change callback
    onTrustChange(trustEvent);
    
    return trustEvent;
  }, [trustScores, weights, thresholds, demotedAgents, onTrustChange, onAgentDemotion]);
  
  /**
   * Apply natural decay to trust scores
   * This simulates trust degradation over time without activity
   */
  const applyTrustDecay = useCallback(() => {
    setTrustScores(prev => {
      const newScores = { ...prev };
      
      Object.keys(newScores).forEach(agent => {
        // Apply decay
        newScores[agent] = Math.max(0.3, newScores[agent] - decayRate);
      });
      
      return newScores;
    });
  }, [decayRate]);
  
  /**
   * Get trust score for a specific agent
   * 
   * @param {string} agent - Agent identifier
   * @returns {number} Current trust score
   */
  const getTrustScore = useCallback((agent) => {
    return trustScores[agent] || 0.7; // Default starting trust
  }, [trustScores]);
  
  /**
   * Get trust history for a specific agent
   * 
   * @param {string} agent - Agent identifier
   * @returns {Array} Trust history events
   */
  const getTrustHistory = useCallback((agent) => {
    return trustHistory[agent] || [];
  }, [trustHistory]);
  
  /**
   * Check if an agent is currently demoted
   * 
   * @param {string} agent - Agent identifier
   * @returns {boolean} Whether agent is demoted
   */
  const isAgentDemoted = useCallback((agent) => {
    return !!demotedAgents[agent];
  }, [demotedAgents]);
  
  /**
   * Get all demoted agents
   * 
   * @returns {Object} Map of demoted agents
   */
  const getDemotedAgents = useCallback(() => {
    return demotedAgents;
  }, [demotedAgents]);
  
  /**
   * Reset trust score for a specific agent
   * 
   * @param {string} agent - Agent identifier
   * @param {number} score - New trust score
   */
  const resetTrustScore = useCallback((agent, score = 0.7) => {
    setTrustScores(prev => ({
      ...prev,
      [agent]: score
    }));
    
    // If agent was demoted, remove from demoted list
    if (demotedAgents[agent]) {
      setDemotedAgents(prev => {
        const newDemoted = { ...prev };
        delete newDemoted[agent];
        return newDemoted;
      });
    }
  }, [demotedAgents]);
  
  /**
   * Get trust status for an agent
   * 
   * @param {string} agent - Agent identifier
   * @returns {string} Trust status (active, warning, demoted)
   */
  const getTrustStatus = useCallback((agent) => {
    const score = getTrustScore(agent);
    
    if (isAgentDemoted(agent)) {
      return 'demoted';
    }
    
    if (score < thresholds.warning) {
      return 'warning';
    }
    
    return 'active';
  }, [getTrustScore, isAgentDemoted, thresholds]);
  
  /**
   * Get all trust scores
   * 
   * @returns {Object} Map of all trust scores
   */
  const getAllTrustScores = useCallback(() => {
    return trustScores;
  }, [trustScores]);
  
  /**
   * Get all trust history
   * 
   * @returns {Object} Map of all trust history
   */
  const getAllTrustHistory = useCallback(() => {
    return trustHistory;
  }, [trustHistory]);
  
  // Apply decay periodically
  useEffect(() => {
    const decayInterval = setInterval(() => {
      applyTrustDecay();
    }, 60000); // Apply decay every minute
    
    return () => clearInterval(decayInterval);
  }, [applyTrustDecay]);
  
  return {
    evaluateTrust,
    getTrustScore,
    getTrustHistory,
    isAgentDemoted,
    getDemotedAgents,
    resetTrustScore,
    getTrustStatus,
    getAllTrustScores,
    getAllTrustHistory,
    applyTrustDecay
  };
};

/**
 * Standalone function to evaluate trust for an agent
 * 
 * @param {string} agent - Agent identifier
 * @param {Object} metrics - Performance metrics
 * @param {Object} options - Evaluation options
 * @returns {Object} Trust evaluation result
 */
export const evaluateAgentTrust = (agent, metrics, options = {}) => {
  const {
    previousScore = 0.7,
    weights = DEFAULT_WEIGHTS,
    loopId = `loop_${Date.now()}`
  } = options;
  
  // Calculate new trust score
  const newScore = calculateTrustScore(metrics, weights);
  
  // Calculate delta
  const delta = calculateTrustDelta(newScore, previousScore);
  
  // Determine reason for change
  const reason = determineTrustChangeReason(metrics, delta);
  
  return {
    agent,
    trust_score: newScore,
    delta,
    loop_id: loopId,
    reason,
    timestamp: new Date().toISOString(),
    status: newScore < DEFAULT_THRESHOLDS.demotion ? 'demoted' : 'active'
  };
};

export default {
  useTrustScoreEvaluator,
  evaluateAgentTrust,
  calculateTrustScore,
  calculateTrustDelta,
  determineTrustChangeReason,
  generateTrustEventId,
  DEFAULT_WEIGHTS,
  DEFAULT_THRESHOLDS,
  DEFAULT_DECAY_RATE,
  DEFAULT_PERSISTENCE
};
