/**
 * AutoRerouter.js
 * 
 * Monitors loop scorecard values and automatically triggers re-delegation
 * to secondary agents when certain conditions are met.
 * 
 * Conditions for rerouting:
 * - trust_delta < -0.5
 * - drift_score > 0.7
 * - agent has ≥3 recent loop fails
 */

import { createContext, useContext, useState, useEffect, useCallback } from 'react';

// Create context for AutoRerouter
const AutoRouterContext = createContext(null);

// Agent fallback mapping
const AGENT_FALLBACKS = {
  'ASH': 'SAGE',
  'NOVA': 'SAGE',
  'SKEPTIC': 'PHILOSOPHER',
  'HISTORIAN': 'LIBRARIAN',
  'DEFAULT': 'SAGE' // Default fallback
};

// Failure threshold for auto-rerouting
const FAILURE_THRESHOLD = 3;
// Trust delta threshold for auto-rerouting
const TRUST_DELTA_THRESHOLD = -0.5;
// Drift score threshold for auto-rerouting
const DRIFT_SCORE_THRESHOLD = 0.7;

/**
 * AutoRouter Provider Component
 * Provides auto-routing functionality to the application
 */
export const AutoRouterProvider = ({ children }) => {
  const [reroutes, setReroutes] = useState([]);
  const [isMonitoring, setIsMonitoring] = useState(true);
  const [agentFailureCounts, setAgentFailureCounts] = useState({});
  const [lastNotification, setLastNotification] = useState(null);

  // Fetch recent reroutes on mount
  useEffect(() => {
    const fetchRecentReroutes = async () => {
      try {
        const response = await fetch('/api/loop/reroutes');
        if (response.ok) {
          const data = await response.json();
          setReroutes(data.reroutes || []);
        }
      } catch (error) {
        console.error('Failed to fetch recent reroutes:', error);
      }
    };

    fetchRecentReroutes();
  }, []);

  // Monitor loop scorecards
  useEffect(() => {
    if (!isMonitoring) return;

    const monitorInterval = setInterval(async () => {
      try {
        const response = await fetch('/api/loop/scorecards/recent');
        if (response.ok) {
          const data = await response.json();
          
          // Process scorecards for potential rerouting
          data.scorecards.forEach(scorecard => {
            checkAndReroute(scorecard);
          });
        }
      } catch (error) {
        console.error('Failed to fetch recent scorecards:', error);
      }
    }, 10000); // Check every 10 seconds

    return () => clearInterval(monitorInterval);
  }, [isMonitoring, agentFailureCounts]);

  // Check if a loop needs rerouting and perform reroute if necessary
  const checkAndReroute = useCallback(async (scorecard) => {
    const { loop_id, agent_id, trust_delta, drift_score, status } = scorecard;
    
    // Skip if already rerouted
    if (scorecard.rerouted) return;
    
    // Update agent failure counts if this loop failed
    if (status === 'failed') {
      setAgentFailureCounts(prev => ({
        ...prev,
        [agent_id]: (prev[agent_id] || 0) + 1
      }));
    }
    
    // Check rerouting conditions
    const needsReroute = 
      (trust_delta !== undefined && trust_delta < TRUST_DELTA_THRESHOLD) ||
      (drift_score !== undefined && drift_score > DRIFT_SCORE_THRESHOLD) ||
      (agentFailureCounts[agent_id] >= FAILURE_THRESHOLD);
    
    if (needsReroute) {
      // Determine fallback agent
      const fallbackAgent = AGENT_FALLBACKS[agent_id] || AGENT_FALLBACKS.DEFAULT;
      
      // Perform reroute
      try {
        const reroute = {
          loop_id,
          original_agent: agent_id,
          fallback_agent: fallbackAgent,
          reason: getRerouteReason(scorecard, agentFailureCounts[agent_id]),
          timestamp: new Date().toISOString()
        };
        
        // Call reroute API
        const response = await fetch('/api/loop/reroute', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(reroute)
        });
        
        if (response.ok) {
          // Add to local reroutes list
          setReroutes(prev => [reroute, ...prev]);
          
          // Reset failure count for this agent
          setAgentFailureCounts(prev => ({
            ...prev,
            [agent_id]: 0
          }));
          
          // Notify operator
          notifyOperator(reroute);
          
          // Log to console
          console.log(`Auto-rerouted loop ${loop_id} from ${agent_id} to ${fallbackAgent}`);
          
          return true;
        }
      } catch (error) {
        console.error('Failed to reroute loop:', error);
      }
    }
    
    return false;
  }, [agentFailureCounts]);

  // Get reason for reroute based on scorecard values
  const getRerouteReason = (scorecard, failureCount) => {
    const { trust_delta, drift_score } = scorecard;
    
    if (failureCount >= FAILURE_THRESHOLD) {
      return `Agent has ${failureCount} recent failures`;
    }
    
    if (trust_delta !== undefined && trust_delta < TRUST_DELTA_THRESHOLD) {
      return `Trust delta (${trust_delta.toFixed(2)}) below threshold`;
    }
    
    if (drift_score !== undefined && drift_score > DRIFT_SCORE_THRESHOLD) {
      return `Drift score (${drift_score.toFixed(2)}) above threshold`;
    }
    
    return 'Multiple factors';
  };

  // Notify operator of reroute
  const notifyOperator = (reroute) => {
    // Avoid duplicate notifications within 5 seconds
    const now = Date.now();
    if (lastNotification && now - lastNotification < 5000) return;
    
    setLastNotification(now);
    
    // Send notification to chat
    try {
      fetch('/api/chat/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: `🔄 Auto-rerouted loop ${reroute.loop_id} from ${reroute.original_agent} to ${reroute.fallback_agent}. Reason: ${reroute.reason}`,
          sender: 'SYSTEM',
          type: 'notification'
        })
      });
    } catch (error) {
      console.error('Failed to send chat notification:', error);
    }
    
    // Trigger UI notification if available
    if (window.dispatchEvent) {
      window.dispatchEvent(new CustomEvent('promethios:notification', {
        detail: {
          title: 'Agent Auto-Rerouting',
          message: `Loop ${reroute.loop_id} rerouted from ${reroute.original_agent} to ${reroute.fallback_agent}`,
          type: 'info',
          duration: 5000
        }
      }));
    }
  };

  // Manually trigger reroute for a specific loop
  const manualReroute = async (loopId, originalAgent, fallbackAgent, reason) => {
    try {
      const reroute = {
        loop_id: loopId,
        original_agent: originalAgent,
        fallback_agent: fallbackAgent || AGENT_FALLBACKS[originalAgent] || AGENT_FALLBACKS.DEFAULT,
        reason: reason || 'Manual reroute by operator',
        timestamp: new Date().toISOString(),
        manual: true
      };
      
      // Call reroute API
      const response = await fetch('/api/loop/reroute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(reroute)
      });
      
      if (response.ok) {
        // Add to local reroutes list
        setReroutes(prev => [reroute, ...prev]);
        
        // Log to console
        console.log(`Manually rerouted loop ${loopId} from ${originalAgent} to ${reroute.fallback_agent}`);
        
        return true;
      }
    } catch (error) {
      console.error('Failed to manually reroute loop:', error);
    }
    
    return false;
  };

  // Toggle monitoring state
  const toggleMonitoring = () => {
    setIsMonitoring(prev => !prev);
  };

  // Clear failure count for a specific agent
  const clearFailureCount = (agentId) => {
    setAgentFailureCounts(prev => ({
      ...prev,
      [agentId]: 0
    }));
  };

  // Get recent reroutes
  const getRecentReroutes = (limit = 10) => {
    return reroutes.slice(0, limit);
  };

  // Context value
  const value = {
    reroutes,
    isMonitoring,
    agentFailureCounts,
    manualReroute,
    toggleMonitoring,
    clearFailureCount,
    getRecentReroutes
  };

  return (
    <AutoRouterContext.Provider value={value}>
      {children}
    </AutoRouterContext.Provider>
  );
};

// Custom hook to use the AutoRouter context
export const useAutoRouter = () => {
  const context = useContext(AutoRouterContext);
  if (!context) {
    throw new Error('useAutoRouter must be used within an AutoRouterProvider');
  }
  return context;
};

// Standalone functions for use outside of React components

/**
 * Check if a loop needs rerouting based on its scorecard
 * @param {Object} scorecard - The loop scorecard
 * @param {Object} failureCounts - Map of agent IDs to failure counts
 * @returns {boolean} - Whether the loop needs rerouting
 */
export const checkNeedsReroute = (scorecard, failureCounts = {}) => {
  const { agent_id, trust_delta, drift_score } = scorecard;
  
  return (
    (trust_delta !== undefined && trust_delta < TRUST_DELTA_THRESHOLD) ||
    (drift_score !== undefined && drift_score > DRIFT_SCORE_THRESHOLD) ||
    (failureCounts[agent_id] >= FAILURE_THRESHOLD)
  );
};

/**
 * Get the fallback agent for a given agent
 * @param {string} agentId - The original agent ID
 * @returns {string} - The fallback agent ID
 */
export const getFallbackAgent = (agentId) => {
  return AGENT_FALLBACKS[agentId] || AGENT_FALLBACKS.DEFAULT;
};

export default {
  AutoRouterProvider,
  useAutoRouter,
  checkNeedsReroute,
  getFallbackAgent
};
