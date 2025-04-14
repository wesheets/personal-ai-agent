import React, { createContext, useContext, useState, useEffect } from 'react';
import { controlService } from '../api/ApiService';

// Define system status types
export const STATUS_TYPES = {
  STABLE: 'stable',
  DEGRADED: 'degraded',
  UNAVAILABLE: 'unavailable'
};

// Create context
const StatusContext = createContext();

/**
 * StatusProvider Component
 * 
 * Provides global access to system status information and notifications
 * Acts as the single source of truth for system health across the application
 */
export const StatusProvider = ({ children }) => {
  // System status state
  const [systemStatus, setSystemStatus] = useState({
    type: STATUS_TYPES.STABLE,
    message: 'System operational',
    timestamp: new Date().toISOString()
  });
  
  // Warnings collection
  const [warnings, setWarnings] = useState([]);
  
  // Memory fallback state
  const [memoryFallback, setMemoryFallback] = useState({
    active: false,
    reason: null,
    timestamp: null
  });
  
  // Control mode state
  const [controlMode, setControlMode] = useState({
    mode: 'normal',
    loadError: false,
    errorMessage: null
  });
  
  // Delegate endpoint state
  const [delegateStatus, setDelegateStatus] = useState({
    errors: [],
    lastSuccess: null
  });
  
  // Agent health pings
  const [agentHealthPings, setAgentHealthPings] = useState([]);
  
  // Status overlay visibility
  const [overlayVisible, setOverlayVisible] = useState(false);
  
  // Poll for system status
  useEffect(() => {
    let isMounted = true;
    
    const pollSystemStatus = async () => {
      try {
        // Get agent status
        const agentStatus = await controlService.getAgentStatus();
        
        if (isMounted) {
          // Update agent health pings
          if (agentStatus && agentStatus.agents) {
            setAgentHealthPings(agentStatus.agents.map(agent => ({
              id: agent.id,
              name: agent.name,
              status: agent.status,
              lastPing: agent.lastPing || new Date().toISOString()
            })));
          }
          
          // Update system status based on agent health
          const unavailableAgents = agentStatus?.agents?.filter(a => a.status === 'unavailable') || [];
          const degradedAgents = agentStatus?.agents?.filter(a => a.status === 'degraded') || [];
          
          if (unavailableAgents.length > 0) {
            setSystemStatus({
              type: STATUS_TYPES.DEGRADED,
              message: `${unavailableAgents.length} agents unavailable`,
              timestamp: new Date().toISOString()
            });
          } else if (degradedAgents.length > 0) {
            setSystemStatus({
              type: STATUS_TYPES.DEGRADED,
              message: `${degradedAgents.length} agents in degraded state`,
              timestamp: new Date().toISOString()
            });
          } else {
            setSystemStatus({
              type: STATUS_TYPES.STABLE,
              message: 'All agents operational',
              timestamp: new Date().toISOString()
            });
          }
        }
      } catch (error) {
        console.error('Error polling system status:', error);
        
        if (isMounted) {
          setSystemStatus({
            type: STATUS_TYPES.UNAVAILABLE,
            message: 'Error connecting to status API',
            timestamp: new Date().toISOString()
          });
        }
      }
    };
    
    // Poll immediately and then every 30 seconds
    pollSystemStatus();
    const interval = setInterval(pollSystemStatus, 30000);
    
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);
  
  // Check control mode status
  useEffect(() => {
    let isMounted = true;
    
    const checkControlMode = async () => {
      try {
        const response = await controlService.getControlMode();
        
        if (isMounted && response) {
          setControlMode({
            mode: response.mode || 'normal',
            loadError: false,
            errorMessage: null
          });
        }
      } catch (error) {
        console.error('Error loading control mode:', error);
        
        if (isMounted) {
          setControlMode({
            mode: 'unknown',
            loadError: true,
            errorMessage: error.message || 'Failed to load control mode'
          });
          
          // Add warning
          addWarning('Control mode load failure', 'Unable to determine system control mode');
        }
      }
    };
    
    checkControlMode();
    
    return () => {
      isMounted = false;
    };
  }, []);
  
  /**
   * Add a warning to the warnings collection
   * @param {string} title - Warning title
   * @param {string} message - Warning message
   * @param {string} source - Source of the warning
   */
  const addWarning = (title, message, source = 'system') => {
    const warning = {
      id: `warning-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      title,
      message,
      source,
      timestamp: new Date().toISOString()
    };
    
    setWarnings(prev => [warning, ...prev]);
    
    // Show overlay when warnings are added
    setOverlayVisible(true);
    
    return warning.id;
  };
  
  /**
   * Remove a warning from the warnings collection
   * @param {string} id - Warning ID to remove
   */
  const removeWarning = (id) => {
    setWarnings(prev => prev.filter(warning => warning.id !== id));
    
    // Hide overlay if no warnings left
    if (warnings.length <= 1) {
      setOverlayVisible(false);
    }
  };
  
  /**
   * Set memory fallback state
   * @param {boolean} active - Whether fallback is active
   * @param {string} reason - Reason for fallback
   */
  const setMemoryFallbackState = (active, reason = null) => {
    setMemoryFallback({
      active,
      reason,
      timestamp: new Date().toISOString()
    });
    
    if (active) {
      addWarning(
        'Memory Fallback Active', 
        reason || 'Vector memory is in fallback mode',
        'memory'
      );
    }
  };
  
  /**
   * Record delegate endpoint error
   * @param {string} error - Error message
   */
  const recordDelegateError = (error) => {
    setDelegateStatus(prev => ({
      ...prev,
      errors: [...prev.errors, {
        message: error,
        timestamp: new Date().toISOString()
      }]
    }));
    
    addWarning('Delegate Endpoint Error', error, 'delegate');
  };
  
  /**
   * Record delegate endpoint success
   */
  const recordDelegateSuccess = () => {
    setDelegateStatus(prev => ({
      ...prev,
      lastSuccess: new Date().toISOString()
    }));
  };
  
  /**
   * Update system status
   * @param {string} type - Status type (stable, degraded, unavailable)
   * @param {string} message - Status message
   */
  const updateSystemStatus = (type, message) => {
    setSystemStatus({
      type,
      message,
      timestamp: new Date().toISOString()
    });
    
    if (type !== STATUS_TYPES.STABLE) {
      setOverlayVisible(true);
    }
  };
  
  /**
   * Toggle overlay visibility
   */
  const toggleOverlay = () => {
    setOverlayVisible(prev => !prev);
  };
  
  // Context value
  const value = {
    systemStatus,
    warnings,
    memoryFallback,
    controlMode,
    delegateStatus,
    agentHealthPings,
    overlayVisible,
    addWarning,
    removeWarning,
    setMemoryFallbackState,
    recordDelegateError,
    recordDelegateSuccess,
    updateSystemStatus,
    toggleOverlay
  };
  
  return (
    <StatusContext.Provider value={value}>
      {children}
    </StatusContext.Provider>
  );
};

/**
 * Custom hook to use the status context
 */
export const useStatus = () => {
  const context = useContext(StatusContext);
  
  if (!context) {
    throw new Error('useStatus must be used within a StatusProvider');
  }
  
  return context;
};

export default StatusContext;
