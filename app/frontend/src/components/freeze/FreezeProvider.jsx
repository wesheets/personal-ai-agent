/**
 * FreezeProvider.jsx
 * 
 * Context provider for the freeze lock system.
 * Provides access to freeze functionality throughout the application.
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useLoopFreezeController } from '../../logic/LoopFreezeController';
import freezeLogData from '../../data/FreezeLog.json';
import { validateFreezeEvent } from '../../schemas/FreezeStatusSchema';

// Create context
const FreezeContext = createContext(null);

/**
 * FreezeProvider Component
 * 
 * Provides freeze lock functionality to child components.
 */
export const FreezeProvider = ({ children, initialThresholds, onFreeze, onUnfreeze }) => {
  // Initialize freeze controller
  const freezeController = useLoopFreezeController({
    initialThresholds,
    onFreeze,
    onUnfreeze
  });
  
  // Load freeze log data
  const [freezeLog, setFreezeLog] = useState(freezeLogData);
  
  // Initialize freeze log
  useEffect(() => {
    // Validate freeze log data
    const validEvents = freezeLog.events.filter(event => validateFreezeEvent(event));
    
    if (validEvents.length !== freezeLog.events.length) {
      console.warn(`Some freeze events failed validation (${freezeLog.events.length - validEvents.length} invalid events)`);
    }
    
    // Update freeze log meta
    setFreezeLog({
      ...freezeLog,
      meta: {
        ...freezeLog.meta,
        last_updated: new Date().toISOString()
      }
    });
  }, []);
  
  // Provide context value
  const contextValue = {
    ...freezeController,
    freezeLog
  };
  
  return (
    <FreezeContext.Provider value={contextValue}>
      {children}
    </FreezeContext.Provider>
  );
};

/**
 * useFreeze Hook
 * 
 * Custom hook for accessing freeze functionality.
 */
export const useFreeze = () => {
  const context = useContext(FreezeContext);
  
  if (!context) {
    throw new Error('useFreeze must be used within a FreezeProvider');
  }
  
  return context;
};

export default FreezeProvider;
