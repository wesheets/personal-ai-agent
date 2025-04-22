/**
 * TrustProvider.jsx
 * 
 * Context provider for the trust feedback loop system.
 * Ensures schema compliance and provides a centralized access point for trust data.
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useTrustScoreEvaluator } from '../logic/TrustScoreEvaluator';
import { useAutoDemoteAgent } from '../logic/AutoDemoteAgent';
import { validateTrustEvent, validateDemotionEvent } from '../schemas/TrustSchema';

// Create context
const TrustContext = createContext(null);

/**
 * TrustProvider Component
 * 
 * Provides trust data and functions to all child components.
 */
export const TrustProvider = ({ children, initialScores = {} }) => {
  // Use trust evaluator and auto demotion hooks
  const trustEvaluator = useTrustScoreEvaluator({
    initialScores,
    onTrustChange: (event) => {
      // Validate event against schema
      if (!validateTrustEvent(event)) {
        console.error('Invalid trust event:', event);
      }
      
      // Log trust change to console
      console.log(`Trust change for ${event.agent}: ${event.trust_score.toFixed(2)} (${event.delta > 0 ? '+' : ''}${event.delta.toFixed(2)})`);
    }
  });
  
  const autoDemoter = useAutoDemoteAgent({
    onAgentDemotion: (event) => {
      // Validate event against schema
      if (!validateDemotionEvent(event)) {
        console.error('Invalid demotion event:', event);
      }
      
      // Log demotion to console
      console.log(`Agent ${event.agent} demoted. Using ${event.fallback_agent} instead.`);
    }
  });
  
  // Combine all trust-related functions and data
  const trustContextValue = {
    ...trustEvaluator,
    ...autoDemoter,
    // Add any additional functions or data here
  };
  
  return (
    <TrustContext.Provider value={trustContextValue}>
      {children}
    </TrustContext.Provider>
  );
};

/**
 * useTrust Hook
 * 
 * Custom hook for accessing trust data and functions.
 */
export const useTrust = () => {
  const context = useContext(TrustContext);
  
  if (!context) {
    throw new Error('useTrust must be used within a TrustProvider');
  }
  
  return context;
};

export default TrustProvider;
