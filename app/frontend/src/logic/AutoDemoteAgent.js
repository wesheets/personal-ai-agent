/**
 * AutoDemoteAgent.js
 * 
 * Background hook that monitors trust scores and automatically:
 * - Temporarily removes agents with low trust from /agent/run rotations
 * - Replaces them with fallback agents
 * - Logs demotion events
 */

import { useState, useEffect, useCallback } from 'react';
import { useTrustScoreEvaluator } from './TrustScoreEvaluator';

// Default demotion threshold
const DEFAULT_DEMOTION_THRESHOLD = 0.4;

// Default fallback agent mapping
const DEFAULT_FALLBACK_MAPPING = {
  'NOVA': 'SAGE',
  'HAL': 'NOVA',
  'CRITIC': 'SAGE',
  // SAGE has no fallback as it's the most trusted baseline
};

/**
 * Hook for automatically demoting agents based on trust scores
 * 
 * @param {Object} options - Configuration options
 * @param {Object} options.initialScores - Initial trust scores for agents
 * @param {number} options.demotionThreshold - Trust score threshold for demotion
 * @param {Object} options.fallbackMapping - Mapping of agents to their fallbacks
 * @param {Function} options.onAgentDemotion - Callback when agent is demoted
 * @param {Function} options.onAgentPromotion - Callback when agent is promoted
 * @param {boolean} options.enabled - Whether auto-demotion is enabled
 * @returns {Object} Auto-demotion state and functions
 */
export const useAutoDemoteAgent = ({
  initialScores = {},
  demotionThreshold = DEFAULT_DEMOTION_THRESHOLD,
  fallbackMapping = DEFAULT_FALLBACK_MAPPING,
  onAgentDemotion = () => {},
  onAgentPromotion = () => {},
  enabled = true
}) => {
  // State for demoted agents
  const [demotedAgents, setDemotedAgents] = useState({});
  const [isMonitoring, setIsMonitoring] = useState(enabled);
  const [demotionHistory, setDemotionHistory] = useState([]);
  
  // Use trust score evaluator
  const {
    getTrustScore,
    getTrustHistory,
    isAgentDemoted,
    resetTrustScore
  } = useTrustScoreEvaluator({
    initialScores,
    onAgentDemotion: (demotionData) => {
      if (isMonitoring) {
        handleAgentDemotion(demotionData);
      }
    }
  });
  
  /**
   * Handle agent demotion
   * 
   * @param {Object} demotionData - Data about the demotion
   */
  const handleAgentDemotion = useCallback((demotionData) => {
    const { agent, trust_score, reason, loop_id } = demotionData;
    
    // Skip if agent is already demoted
    if (demotedAgents[agent]) return;
    
    // Skip if agent has no fallback
    if (!fallbackMapping[agent]) return;
    
    // Create demotion event
    const demotionEvent = {
      id: `demotion_${Date.now()}_${Math.floor(Math.random() * 10000)}`,
      agent,
      fallback_agent: fallbackMapping[agent],
      trust_score,
      reason,
      loop_id,
      timestamp: new Date().toISOString(),
      status: 'active'
    };
    
    // Update demoted agents
    setDemotedAgents(prev => ({
      ...prev,
      [agent]: demotionEvent
    }));
    
    // Update demotion history
    setDemotionHistory(prev => [...prev, demotionEvent]);
    
    // Call demotion callback
    onAgentDemotion(demotionEvent);
    
    console.log(`Agent ${agent} demoted due to low trust score (${trust_score.toFixed(2)}). Replaced with ${fallbackMapping[agent]}.`);
  }, [demotedAgents, fallbackMapping, onAgentDemotion]);
  
  /**
   * Check for agents that should be demoted
   */
  const checkForDemotions = useCallback(() => {
    if (!isMonitoring) return;
    
    // Check each agent's trust score
    Object.keys(fallbackMapping).forEach(agent => {
      const trustScore = getTrustScore(agent);
      
      // If trust score is below threshold and agent is not already demoted
      if (trustScore < demotionThreshold && !demotedAgents[agent]) {
        // Get latest trust history event for this agent
        const history = getTrustHistory(agent);
        const latestEvent = history.length > 0 ? history[history.length - 1] : null;
        
        // Create demotion data
        const demotionData = {
          agent,
          trust_score: trustScore,
          reason: latestEvent ? latestEvent.reason : 'low trust score',
          loop_id: latestEvent ? latestEvent.loop_id : `loop_${Date.now()}`
        };
        
        // Handle demotion
        handleAgentDemotion(demotionData);
      }
    });
  }, [isMonitoring, fallbackMapping, getTrustScore, demotionThreshold, demotedAgents, getTrustHistory, handleAgentDemotion]);
  
  /**
   * Check for agents that should be promoted (restored)
   */
  const checkForPromotions = useCallback(() => {
    if (!isMonitoring) return;
    
    // Check each demoted agent's trust score
    Object.keys(demotedAgents).forEach(agent => {
      const trustScore = getTrustScore(agent);
      
      // If trust score is above promotion threshold
      if (trustScore >= demotionThreshold + 0.1) {
        // Create promotion event
        const promotionEvent = {
          id: `promotion_${Date.now()}_${Math.floor(Math.random() * 10000)}`,
          agent,
          trust_score: trustScore,
          reason: 'trust score recovery',
          previous_demotion: demotedAgents[agent],
          timestamp: new Date().toISOString()
        };
        
        // Remove from demoted agents
        setDemotedAgents(prev => {
          const newDemoted = { ...prev };
          delete newDemoted[agent];
          return newDemoted;
        });
        
        // Update demotion history (mark as restored)
        setDemotionHistory(prev => 
          prev.map(event => 
            event.id === demotedAgents[agent].id
              ? { ...event, status: 'restored' }
              : event
          )
        );
        
        // Call promotion callback
        onAgentPromotion(promotionEvent);
        
        console.log(`Agent ${agent} promoted due to trust score recovery (${trustScore.toFixed(2)}).`);
      }
    });
  }, [isMonitoring, demotedAgents, getTrustScore, demotionThreshold, onAgentPromotion]);
  
  /**
   * Get fallback agent for a given agent
   * 
   * @param {string} agent - Agent identifier
   * @returns {string|null} Fallback agent or null if none
   */
  const getFallbackAgent = useCallback((agent) => {
    // If agent is demoted, return its fallback
    if (demotedAgents[agent]) {
      return fallbackMapping[agent] || null;
    }
    
    // If agent is a fallback for any demoted agent, check if it's also demoted
    const isFallbackFor = Object.entries(demotedAgents).find(([_, demotion]) => 
      demotion.fallback_agent === agent
    );
    
    if (isFallbackFor && demotedAgents[agent]) {
      // Fallback agent is also demoted, get its fallback
      return fallbackMapping[agent] || null;
    }
    
    // Agent is not demoted and not a fallback for a demoted agent
    return null;
  }, [demotedAgents, fallbackMapping]);
  
  /**
   * Get effective agent to use (considering demotions)
   * 
   * @param {string} requestedAgent - Requested agent identifier
   * @returns {string} Effective agent to use
   */
  const getEffectiveAgent = useCallback((requestedAgent) => {
    let currentAgent = requestedAgent;
    let visited = new Set();
    
    // Follow fallback chain until we find an active agent
    while (true) {
      // Prevent infinite loops
      if (visited.has(currentAgent)) {
        console.warn(`Circular fallback detected for agent ${requestedAgent}`);
        return 'SAGE'; // Default to SAGE as a last resort
      }
      
      visited.add(currentAgent);
      
      // Get fallback for current agent
      const fallback = getFallbackAgent(currentAgent);
      
      // If no fallback or fallback is the same as current, return current
      if (!fallback || fallback === currentAgent) {
        return currentAgent;
      }
      
      // Move to fallback agent
      currentAgent = fallback;
    }
  }, [getFallbackAgent]);
  
  /**
   * Manually demote an agent
   * 
   * @param {string} agent - Agent to demote
   * @param {string} reason - Reason for demotion
   * @returns {Object} Demotion event
   */
  const demoteAgent = useCallback((agent, reason = 'manual demotion') => {
    // Skip if agent has no fallback
    if (!fallbackMapping[agent]) {
      console.warn(`Cannot demote agent ${agent}: no fallback defined`);
      return null;
    }
    
    // Create demotion event
    const demotionEvent = {
      id: `demotion_${Date.now()}_${Math.floor(Math.random() * 10000)}`,
      agent,
      fallback_agent: fallbackMapping[agent],
      trust_score: getTrustScore(agent),
      reason,
      loop_id: `loop_${Date.now()}`,
      timestamp: new Date().toISOString(),
      status: 'active',
      manual: true
    };
    
    // Update demoted agents
    setDemotedAgents(prev => ({
      ...prev,
      [agent]: demotionEvent
    }));
    
    // Update demotion history
    setDemotionHistory(prev => [...prev, demotionEvent]);
    
    // Call demotion callback
    onAgentDemotion(demotionEvent);
    
    console.log(`Agent ${agent} manually demoted. Replaced with ${fallbackMapping[agent]}.`);
    
    return demotionEvent;
  }, [fallbackMapping, getTrustScore, onAgentDemotion]);
  
  /**
   * Manually promote (restore) a demoted agent
   * 
   * @param {string} agent - Agent to promote
   * @param {string} reason - Reason for promotion
   * @returns {Object} Promotion event
   */
  const promoteAgent = useCallback((agent, reason = 'manual promotion') => {
    // Skip if agent is not demoted
    if (!demotedAgents[agent]) {
      console.warn(`Cannot promote agent ${agent}: not currently demoted`);
      return null;
    }
    
    // Create promotion event
    const promotionEvent = {
      id: `promotion_${Date.now()}_${Math.floor(Math.random() * 10000)}`,
      agent,
      trust_score: getTrustScore(agent),
      reason,
      previous_demotion: demotedAgents[agent],
      timestamp: new Date().toISOString(),
      manual: true
    };
    
    // Remove from demoted agents
    setDemotedAgents(prev => {
      const newDemoted = { ...prev };
      delete newDemoted[agent];
      return newDemoted;
    });
    
    // Update demotion history (mark as restored)
    setDemotionHistory(prev => 
      prev.map(event => 
        event.id === demotedAgents[agent].id
          ? { ...event, status: 'restored' }
          : event
      )
    );
    
    // Call promotion callback
    onAgentPromotion(promotionEvent);
    
    console.log(`Agent ${agent} manually promoted.`);
    
    return promotionEvent;
  }, [demotedAgents, getTrustScore, onAgentPromotion]);
  
  /**
   * Start monitoring
   */
  const startMonitoring = useCallback(() => {
    setIsMonitoring(true);
  }, []);
  
  /**
   * Stop monitoring
   */
  const stopMonitoring = useCallback(() => {
    setIsMonitoring(false);
  }, []);
  
  /**
   * Reset all demotions
   */
  const resetAllDemotions = useCallback(() => {
    // Update demotion history (mark all as reset)
    setDemotionHistory(prev => 
      prev.map(event => 
        event.status === 'active'
          ? { ...event, status: 'reset' }
          : event
      )
    );
    
    // Clear demoted agents
    setDemotedAgents({});
    
    console.log('All agent demotions have been reset.');
  }, []);
  
  /**
   * Get all demoted agents
   * 
   * @returns {Object} Map of demoted agents
   */
  const getDemotedAgents = useCallback(() => {
    return demotedAgents;
  }, [demotedAgents]);
  
  /**
   * Get demotion history
   * 
   * @returns {Array} Demotion history events
   */
  const getDemotionHistory = useCallback(() => {
    return demotionHistory;
  }, [demotionHistory]);
  
  /**
   * Check if an agent is currently demoted
   * 
   * @param {string} agent - Agent identifier
   * @returns {boolean} Whether agent is demoted
   */
  const isAgentCurrentlyDemoted = useCallback((agent) => {
    return !!demotedAgents[agent];
  }, [demotedAgents]);
  
  // Run checks periodically
  useEffect(() => {
    if (!isMonitoring) return;
    
    // Initial check
    checkForDemotions();
    checkForPromotions();
    
    // Set up interval for periodic checks
    const checkInterval = setInterval(() => {
      checkForDemotions();
      checkForPromotions();
    }, 30000); // Check every 30 seconds
    
    return () => clearInterval(checkInterval);
  }, [isMonitoring, checkForDemotions, checkForPromotions]);
  
  // Update monitoring state when enabled prop changes
  useEffect(() => {
    if (enabled && !isMonitoring) {
      startMonitoring();
    } else if (!enabled && isMonitoring) {
      stopMonitoring();
    }
  }, [enabled, isMonitoring, startMonitoring, stopMonitoring]);
  
  return {
    demotedAgents,
    demotionHistory,
    isMonitoring,
    getFallbackAgent,
    getEffectiveAgent,
    demoteAgent,
    promoteAgent,
    startMonitoring,
    stopMonitoring,
    resetAllDemotions,
    getDemotedAgents,
    getDemotionHistory,
    isAgentDemoted: isAgentCurrentlyDemoted
  };
};

export default {
  useAutoDemoteAgent,
  DEFAULT_DEMOTION_THRESHOLD,
  DEFAULT_FALLBACK_MAPPING
};
