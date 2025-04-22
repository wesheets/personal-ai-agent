/**
 * ContradictionDetector.js
 * 
 * Core comparison logic for detecting contradictions in Promethios reflections and belief states.
 * Runs asynchronously after each new reflection, belief update, or loop summary.
 * Compares against prior reflections in memory and current active belief state.
 * Flags logical opposites, conflicting intent, and divergent values.
 */

import { useState, useEffect, useCallback } from 'react';

/**
 * Types of contradictions that can be detected
 */
export const CONTRADICTION_TYPES = {
  LOGICAL_OPPOSITE: 'logical_opposite',
  CONFLICTING_INTENT: 'conflicting_intent',
  DIVERGENT_VALUES: 'divergent_values',
  SEMANTIC_CONFLICT: 'semantic_conflict',
  TEMPORAL_INCONSISTENCY: 'temporal_inconsistency'
};

/**
 * Default threshold for contradiction detection
 */
const DEFAULT_CONTRADICTION_THRESHOLD = 0.75;

/**
 * Generate a unique contradiction ID
 * @returns {string} A unique ID for the contradiction
 */
export const generateContradictionId = () => {
  return `contradiction_${Date.now()}_${Math.floor(Math.random() * 10000)}`;
};

/**
 * Hook for detecting contradictions in reflections and beliefs
 * 
 * @param {Object} options - Configuration options
 * @param {Array} options.beliefs - Current active beliefs to check against
 * @param {Array} options.reflections - Prior reflections to check against
 * @param {Array} options.summaries - Loop summaries to check against
 * @param {Function} options.onContradictionDetected - Callback when contradiction is detected
 * @param {Number} options.threshold - Threshold for contradiction detection (0-1)
 * @param {Boolean} options.enabled - Whether detection is enabled
 * @returns {Object} Detector state and control functions
 */
export const useContradictionDetector = ({
  beliefs = [],
  reflections = [],
  summaries = [],
  onContradictionDetected = () => {},
  threshold = DEFAULT_CONTRADICTION_THRESHOLD,
  enabled = true
}) => {
  // State for detector
  const [isDetecting, setIsDetecting] = useState(enabled);
  const [lastScan, setLastScan] = useState(null);
  const [contradictionLogs, setContradictionLogs] = useState([]);
  const [detectorConfig, setDetectorConfig] = useState({
    checkLogicalOpposites: true,
    checkConflictingIntent: true,
    checkDivergentValues: true,
    checkSemanticConflicts: true,
    checkTemporalInconsistencies: true
  });
  
  /**
   * Calculate semantic similarity between two text strings
   * In a real implementation, this would use embeddings or LLM API
   * 
   * @param {String} text1 - First text to compare
   * @param {String} text2 - Second text to compare
   * @returns {Number} Similarity score (0-1)
   */
  const calculateSimilarity = useCallback((text1, text2) => {
    // This is a placeholder implementation
    // In production, this would use:
    // 1. Embedding comparison (cosine similarity)
    // 2. LLM-based evaluation
    // 3. Specialized contradiction evaluation models
    
    // Mock implementation for development
    const mockScore = Math.random();
    console.log(`Calculated similarity between texts: ${mockScore.toFixed(2)}`);
    return mockScore;
  }, []);
  
  /**
   * Detect logical opposites between two statements
   * 
   * @param {String} statement1 - First statement
   * @param {String} statement2 - Second statement
   * @returns {Object|null} Contradiction details if detected, null otherwise
   */
  const detectLogicalOpposites = useCallback((statement1, statement2) => {
    if (!detectorConfig.checkLogicalOpposites) return null;
    
    // In a real implementation, this would use NLP techniques or an LLM
    // to identify logical opposites like "X is good" vs "X is bad"
    
    // For now, we'll use a simple mock implementation
    const similarity = calculateSimilarity(statement1, statement2);
    const contradictionScore = 1 - similarity;
    
    if (contradictionScore > threshold) {
      return {
        type: CONTRADICTION_TYPES.LOGICAL_OPPOSITE,
        score: contradictionScore,
        statement1,
        statement2
      };
    }
    
    return null;
  }, [calculateSimilarity, threshold, detectorConfig.checkLogicalOpposites]);
  
  /**
   * Detect conflicting intent between two statements
   * 
   * @param {String} statement1 - First statement
   * @param {String} statement2 - Second statement
   * @returns {Object|null} Contradiction details if detected, null otherwise
   */
  const detectConflictingIntent = useCallback((statement1, statement2) => {
    if (!detectorConfig.checkConflictingIntent) return null;
    
    // In a real implementation, this would analyze the intent behind statements
    // to identify conflicts like "We should do X" vs "We should avoid X"
    
    // For now, we'll use a simple mock implementation
    const similarity = calculateSimilarity(statement1, statement2);
    const contradictionScore = 1 - similarity;
    
    if (contradictionScore > threshold) {
      return {
        type: CONTRADICTION_TYPES.CONFLICTING_INTENT,
        score: contradictionScore,
        statement1,
        statement2
      };
    }
    
    return null;
  }, [calculateSimilarity, threshold, detectorConfig.checkConflictingIntent]);
  
  /**
   * Detect divergent values between two statements
   * 
   * @param {String} statement1 - First statement
   * @param {String} statement2 - Second statement
   * @returns {Object|null} Contradiction details if detected, null otherwise
   */
  const detectDivergentValues = useCallback((statement1, statement2) => {
    if (!detectorConfig.checkDivergentValues) return null;
    
    // In a real implementation, this would identify value-based contradictions
    // like "Privacy is paramount" vs "Data collection should be maximized"
    
    // For now, we'll use a simple mock implementation
    const similarity = calculateSimilarity(statement1, statement2);
    const contradictionScore = 1 - similarity;
    
    if (contradictionScore > threshold) {
      return {
        type: CONTRADICTION_TYPES.DIVERGENT_VALUES,
        score: contradictionScore,
        statement1,
        statement2
      };
    }
    
    return null;
  }, [calculateSimilarity, threshold, detectorConfig.checkDivergentValues]);
  
  /**
   * Detect semantic conflicts between two statements
   * 
   * @param {String} statement1 - First statement
   * @param {String} statement2 - Second statement
   * @returns {Object|null} Contradiction details if detected, null otherwise
   */
  const detectSemanticConflicts = useCallback((statement1, statement2) => {
    if (!detectorConfig.checkSemanticConflicts) return null;
    
    // In a real implementation, this would identify semantic contradictions
    // that aren't strictly logical opposites but still conflict in meaning
    
    // For now, we'll use a simple mock implementation
    const similarity = calculateSimilarity(statement1, statement2);
    const contradictionScore = 1 - similarity;
    
    if (contradictionScore > threshold) {
      return {
        type: CONTRADICTION_TYPES.SEMANTIC_CONFLICT,
        score: contradictionScore,
        statement1,
        statement2
      };
    }
    
    return null;
  }, [calculateSimilarity, threshold, detectorConfig.checkSemanticConflicts]);
  
  /**
   * Detect temporal inconsistencies between two statements
   * 
   * @param {String} statement1 - First statement
   * @param {Object} metadata1 - Metadata for first statement
   * @param {String} statement2 - Second statement
   * @param {Object} metadata2 - Metadata for second statement
   * @returns {Object|null} Contradiction details if detected, null otherwise
   */
  const detectTemporalInconsistencies = useCallback((statement1, metadata1, statement2, metadata2) => {
    if (!detectorConfig.checkTemporalInconsistencies) return null;
    
    // In a real implementation, this would identify inconsistencies over time
    // like "X will never happen" followed by "X is happening now"
    
    // For now, we'll use a simple mock implementation
    const similarity = calculateSimilarity(statement1, statement2);
    const contradictionScore = 1 - similarity;
    
    if (contradictionScore > threshold) {
      return {
        type: CONTRADICTION_TYPES.TEMPORAL_INCONSISTENCY,
        score: contradictionScore,
        statement1,
        statement2,
        metadata1,
        metadata2
      };
    }
    
    return null;
  }, [calculateSimilarity, threshold, detectorConfig.checkTemporalInconsistencies]);
  
  /**
   * Check for contradictions between a new statement and existing statements
   * 
   * @param {Object} newItem - New statement to check
   * @param {String} newItem.content - Content of the new statement
   * @param {String} newItem.type - Type of the new statement (belief, reflection, summary)
   * @param {String} newItem.agent - Agent that produced the statement
   * @param {String} newItem.loop_id - Loop ID where the statement was produced
   * @param {Object} newItem.metadata - Additional metadata
   * @returns {Array} Array of detected contradictions
   */
  const checkForContradictions = useCallback((newItem) => {
    if (!isDetecting || !newItem || !newItem.content) {
      return [];
    }
    
    const contradictions = [];
    
    // Check against beliefs
    beliefs.forEach(belief => {
      // Skip if same item
      if (belief.id === newItem.id) return;
      
      // Check for different types of contradictions
      const logicalContradiction = detectLogicalOpposites(newItem.content, belief.content);
      const intentContradiction = detectConflictingIntent(newItem.content, belief.content);
      const valueContradiction = detectDivergentValues(newItem.content, belief.content);
      const semanticContradiction = detectSemanticConflicts(newItem.content, belief.content);
      const temporalContradiction = detectTemporalInconsistencies(
        newItem.content, 
        newItem.metadata, 
        belief.content, 
        belief.metadata
      );
      
      // Add any detected contradictions
      [logicalContradiction, intentContradiction, valueContradiction, semanticContradiction, temporalContradiction]
        .filter(Boolean)
        .forEach(contradiction => {
          contradictions.push({
            contradiction_id: generateContradictionId(),
            loop_id: newItem.loop_id,
            agent: newItem.agent,
            belief_1: newItem.content,
            belief_2: belief.content,
            detected_at: new Date().toISOString(),
            resolution: 'unresolved',
            type: contradiction.type,
            score: contradiction.score,
            item1_type: newItem.type,
            item2_type: 'belief',
            item1_id: newItem.id,
            item2_id: belief.id
          });
        });
    });
    
    // Check against reflections
    reflections.forEach(reflection => {
      // Skip if same item
      if (reflection.id === newItem.id) return;
      
      // Check for different types of contradictions
      const logicalContradiction = detectLogicalOpposites(newItem.content, reflection.content);
      const intentContradiction = detectConflictingIntent(newItem.content, reflection.content);
      const valueContradiction = detectDivergentValues(newItem.content, reflection.content);
      const semanticContradiction = detectSemanticConflicts(newItem.content, reflection.content);
      const temporalContradiction = detectTemporalInconsistencies(
        newItem.content, 
        newItem.metadata, 
        reflection.content, 
        reflection.metadata
      );
      
      // Add any detected contradictions
      [logicalContradiction, intentContradiction, valueContradiction, semanticContradiction, temporalContradiction]
        .filter(Boolean)
        .forEach(contradiction => {
          contradictions.push({
            contradiction_id: generateContradictionId(),
            loop_id: newItem.loop_id,
            agent: newItem.agent,
            belief_1: newItem.content,
            belief_2: reflection.content,
            detected_at: new Date().toISOString(),
            resolution: 'unresolved',
            type: contradiction.type,
            score: contradiction.score,
            item1_type: newItem.type,
            item2_type: 'reflection',
            item1_id: newItem.id,
            item2_id: reflection.id
          });
        });
    });
    
    // Check against summaries
    summaries.forEach(summary => {
      // Skip if same item
      if (summary.id === newItem.id) return;
      
      // Check for different types of contradictions
      const logicalContradiction = detectLogicalOpposites(newItem.content, summary.content);
      const intentContradiction = detectConflictingIntent(newItem.content, summary.content);
      const valueContradiction = detectDivergentValues(newItem.content, summary.content);
      const semanticContradiction = detectSemanticConflicts(newItem.content, summary.content);
      const temporalContradiction = detectTemporalInconsistencies(
        newItem.content, 
        newItem.metadata, 
        summary.content, 
        summary.metadata
      );
      
      // Add any detected contradictions
      [logicalContradiction, intentContradiction, valueContradiction, semanticContradiction, temporalContradiction]
        .filter(Boolean)
        .forEach(contradiction => {
          contradictions.push({
            contradiction_id: generateContradictionId(),
            loop_id: newItem.loop_id,
            agent: newItem.agent,
            belief_1: newItem.content,
            belief_2: summary.content,
            detected_at: new Date().toISOString(),
            resolution: 'unresolved',
            type: contradiction.type,
            score: contradiction.score,
            item1_type: newItem.type,
            item2_type: 'summary',
            item1_id: newItem.id,
            item2_id: summary.id
          });
        });
    });
    
    return contradictions;
  }, [
    isDetecting, 
    beliefs, 
    reflections, 
    summaries, 
    detectLogicalOpposites, 
    detectConflictingIntent, 
    detectDivergentValues,
    detectSemanticConflicts,
    detectTemporalInconsistencies
  ]);
  
  /**
   * Process a new item and check for contradictions
   * 
   * @param {Object} item - Item to process
   * @returns {Array} Detected contradictions
   */
  const processItem = useCallback((item) => {
    if (!isDetecting || !item) return [];
    
    // Check for contradictions
    const contradictions = checkForContradictions(item);
    
    // If contradictions found, trigger callback and log
    if (contradictions.length > 0) {
      // Update logs
      setContradictionLogs(prev => [...prev, ...contradictions]);
      
      // Trigger callback for each contradiction
      contradictions.forEach(contradiction => {
        onContradictionDetected(contradiction);
        
        // Log to system (in a real implementation)
        logContradiction(contradiction);
      });
    }
    
    // Update last scan timestamp
    setLastScan(new Date());
    
    return contradictions;
  }, [isDetecting, checkForContradictions, onContradictionDetected]);
  
  /**
   * Log a contradiction to the system
   * 
   * @param {Object} contradiction - Contradiction to log
   */
  const logContradiction = useCallback((contradiction) => {
    // In a real implementation, this would send the contradiction to a logging system
    console.log('Logging contradiction:', contradiction);
    
    // Example API call (commented out)
    /*
    fetch('/api/contradiction/log', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(contradiction),
    });
    */
  }, []);
  
  /**
   * Start contradiction detection
   */
  const startDetection = useCallback(() => {
    if (isDetecting) return;
    
    setIsDetecting(true);
    console.log('Contradiction detection started');
  }, [isDetecting]);
  
  /**
   * Stop contradiction detection
   */
  const stopDetection = useCallback(() => {
    if (!isDetecting) return;
    
    setIsDetecting(false);
    console.log('Contradiction detection stopped');
  }, [isDetecting]);
  
  /**
   * Clear contradiction logs
   */
  const clearLogs = useCallback(() => {
    setContradictionLogs([]);
  }, []);
  
  /**
   * Update detector configuration
   * 
   * @param {Object} config - New configuration
   */
  const updateConfig = useCallback((config) => {
    setDetectorConfig(prev => ({
      ...prev,
      ...config
    }));
  }, []);
  
  /**
   * Set up event listeners for monitoring
   */
  useEffect(() => {
    if (!isDetecting) return;
    
    // Set up event listeners for various content sources
    const setupEventListeners = () => {
      // Listen for new reflections
      const reflectionListener = (event) => {
        if (event.detail && event.detail.reflection) {
          processItem({
            content: event.detail.reflection,
            type: 'reflection',
            agent: event.detail.agent,
            loop_id: event.detail.loop_id,
            id: event.detail.id,
            metadata: event.detail
          });
        }
      };
      document.addEventListener('newReflection', reflectionListener);
      
      // Listen for belief updates
      const beliefListener = (event) => {
        if (event.detail && event.detail.belief) {
          processItem({
            content: event.detail.belief,
            type: 'belief',
            agent: event.detail.agent,
            loop_id: event.detail.loop_id,
            id: event.detail.id,
            metadata: event.detail
          });
        }
      };
      document.addEventListener('beliefUpdated', beliefListener);
      
      // Listen for loop summaries
      const summaryListener = (event) => {
        if (event.detail && event.detail.summary) {
          processItem({
            content: event.detail.summary,
            type: 'summary',
            agent: event.detail.agent,
            loop_id: event.detail.loop_id,
            id: event.detail.id,
            metadata: event.detail
          });
        }
      };
      document.addEventListener('loopSummary', summaryListener);
      
      // Return cleanup function
      return () => {
        document.removeEventListener('newReflection', reflectionListener);
        document.removeEventListener('beliefUpdated', beliefListener);
        document.removeEventListener('loopSummary', summaryListener);
      };
    };
    
    // Set up listeners
    const cleanup = setupEventListeners();
    
    // Cleanup function
    return cleanup;
  }, [isDetecting, processItem]);
  
  // Update detection state when enabled prop changes
  useEffect(() => {
    if (enabled && !isDetecting) {
      startDetection();
    } else if (!enabled && isDetecting) {
      stopDetection();
    }
  }, [enabled, isDetecting, startDetection, stopDetection]);
  
  return {
    isDetecting,
    lastScan,
    contradictionLogs,
    startDetection,
    stopDetection,
    clearLogs,
    processItem,
    updateConfig,
    config: detectorConfig
  };
};

/**
 * Standalone function to check for contradictions between two statements
 * 
 * @param {String} statement1 - First statement
 * @param {String} statement2 - Second statement
 * @param {Object} options - Options for contradiction detection
 * @param {Number} options.threshold - Threshold for contradiction detection
 * @param {Array} options.types - Types of contradictions to check for
 * @returns {Object} Check result with contradiction details
 */
export const checkContradiction = async (statement1, statement2, options = {}) => {
  const {
    threshold = DEFAULT_CONTRADICTION_THRESHOLD,
    types = Object.values(CONTRADICTION_TYPES)
  } = options;
  
  // In a real implementation, this would use an API or embedding model
  // For now, we'll use a mock implementation
  
  // Calculate mock contradiction score
  const contradictionScore = Math.random();
  
  // Determine if there's a contradiction
  const isContradiction = contradictionScore > threshold;
  
  // If there's a contradiction, determine the type
  let contradictionType = null;
  if (isContradiction) {
    // Randomly select a type from the provided types
    contradictionType = types[Math.floor(Math.random() * types.length)];
  }
  
  return {
    statement1,
    statement2,
    isContradiction,
    score: contradictionScore,
    threshold,
    type: contradictionType,
    timestamp: new Date().toISOString()
  };
};

export default {
  useContradictionDetector,
  checkContradiction,
  generateContradictionId,
  CONTRADICTION_TYPES
};
