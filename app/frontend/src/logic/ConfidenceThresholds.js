/**
 * ConfidenceThresholds.js
 * 
 * Configurable thresholds per loop/project for the recursive reflection system.
 * Determines when additional reflection is needed based on confidence scores,
 * trust metrics, drift, and other factors.
 */

import { useState, useEffect, useCallback } from 'react';

// Default thresholds for all projects
const DEFAULT_GLOBAL_THRESHOLDS = {
  default: {
    min_confidence: 0.55,
    max_drift: 0.65,
    min_trust_score: 0.4,
    min_trust_delta: -0.2,
    max_reflection_depth: 3
  }
};

// Example project-specific thresholds
const EXAMPLE_PROJECT_THRESHOLDS = {
  default: {
    min_confidence: 0.55,
    max_drift: 0.65,
    min_trust_score: 0.4,
    min_trust_delta: -0.2,
    max_reflection_depth: 3
  },
  life_tree: {
    min_confidence: 0.7,
    max_drift: 0.5,
    min_trust_score: 0.5
  },
  critical_systems: {
    min_confidence: 0.8,
    max_drift: 0.3,
    min_trust_score: 0.6,
    max_reflection_depth: 5
  }
};

/**
 * Load thresholds from storage
 * 
 * @returns {Object} Loaded thresholds or defaults if none found
 */
export const loadThresholds = () => {
  try {
    const storedThresholds = localStorage.getItem('confidence_thresholds');
    return storedThresholds ? JSON.parse(storedThresholds) : DEFAULT_GLOBAL_THRESHOLDS;
  } catch (error) {
    console.error('Error loading thresholds from storage:', error);
    return DEFAULT_GLOBAL_THRESHOLDS;
  }
};

/**
 * Save thresholds to storage
 * 
 * @param {Object} thresholds - Thresholds to save
 */
export const saveThresholds = (thresholds) => {
  try {
    localStorage.setItem('confidence_thresholds', JSON.stringify(thresholds));
  } catch (error) {
    console.error('Error saving thresholds to storage:', error);
  }
};

/**
 * Get thresholds for a specific project
 * 
 * @param {Object} allThresholds - All thresholds
 * @param {string} projectId - Project ID
 * @returns {Object} Thresholds for the project
 */
export const getProjectThresholds = (allThresholds, projectId) => {
  // If project-specific thresholds exist, merge with defaults
  if (projectId && allThresholds[projectId]) {
    return {
      ...allThresholds.default,
      ...allThresholds[projectId]
    };
  }
  
  // Otherwise, return default thresholds
  return allThresholds.default;
};

/**
 * Hook for managing confidence thresholds
 * 
 * @param {Object} options - Configuration options
 * @param {Object} options.initialThresholds - Initial thresholds
 * @param {boolean} options.persistToStorage - Whether to persist thresholds to storage
 * @returns {Object} Threshold management state and functions
 */
export const useConfidenceThresholds = ({
  initialThresholds = DEFAULT_GLOBAL_THRESHOLDS,
  persistToStorage = true
}) => {
  // State for thresholds
  const [thresholds, setThresholds] = useState(initialThresholds);
  
  // Load thresholds from storage on mount
  useEffect(() => {
    if (persistToStorage) {
      const loadedThresholds = loadThresholds();
      setThresholds(loadedThresholds);
    }
  }, [persistToStorage]);
  
  // Save thresholds to storage when they change
  useEffect(() => {
    if (persistToStorage) {
      saveThresholds(thresholds);
    }
  }, [thresholds, persistToStorage]);
  
  /**
   * Update thresholds for a specific project
   * 
   * @param {string} projectId - Project ID
   * @param {Object} projectThresholds - New thresholds for the project
   */
  const updateProjectThresholds = useCallback((projectId, projectThresholds) => {
    setThresholds(prev => ({
      ...prev,
      [projectId]: {
        ...(prev[projectId] || {}),
        ...projectThresholds
      }
    }));
  }, []);
  
  /**
   * Reset thresholds for a specific project to defaults
   * 
   * @param {string} projectId - Project ID
   */
  const resetProjectThresholds = useCallback((projectId) => {
    setThresholds(prev => {
      // If it's the default project, reset to system defaults
      if (projectId === 'default') {
        return {
          ...prev,
          default: { ...DEFAULT_GLOBAL_THRESHOLDS.default }
        };
      }
      
      // Otherwise, remove project-specific thresholds
      const newThresholds = { ...prev };
      delete newThresholds[projectId];
      return newThresholds;
    });
  }, []);
  
  /**
   * Reset all thresholds to defaults
   */
  const resetAllThresholds = useCallback(() => {
    setThresholds(DEFAULT_GLOBAL_THRESHOLDS);
  }, []);
  
  /**
   * Get thresholds for a specific project
   * 
   * @param {string} projectId - Project ID
   * @returns {Object} Thresholds for the project
   */
  const getThresholds = useCallback((projectId = 'default') => {
    return getProjectThresholds(thresholds, projectId);
  }, [thresholds]);
  
  /**
   * Check if a value meets the threshold for a specific metric
   * 
   * @param {string} metric - Metric name
   * @param {number} value - Value to check
   * @param {string} projectId - Project ID
   * @returns {boolean} Whether the value meets the threshold
   */
  const meetsThreshold = useCallback((metric, value, projectId = 'default') => {
    const projectThresholds = getThresholds(projectId);
    
    switch (metric) {
      case 'confidence':
        return value >= projectThresholds.min_confidence;
      case 'trust_score':
        return value >= projectThresholds.min_trust_score;
      case 'trust_delta':
        return value >= projectThresholds.min_trust_delta;
      case 'drift':
        return value <= projectThresholds.max_drift;
      case 'reflection_depth':
        return value <= projectThresholds.max_reflection_depth;
      default:
        console.warn(`Unknown metric: ${metric}`);
        return true;
    }
  }, [getThresholds]);
  
  /**
   * Get all projects with custom thresholds
   * 
   * @returns {Array} List of project IDs
   */
  const getProjectsWithCustomThresholds = useCallback(() => {
    return Object.keys(thresholds).filter(id => id !== 'default');
  }, [thresholds]);
  
  // Return public API
  return {
    thresholds,
    updateProjectThresholds,
    resetProjectThresholds,
    resetAllThresholds,
    getThresholds,
    meetsThreshold,
    getProjectsWithCustomThresholds
  };
};

export default {
  useConfidenceThresholds,
  getProjectThresholds,
  loadThresholds,
  saveThresholds,
  DEFAULT_GLOBAL_THRESHOLDS,
  EXAMPLE_PROJECT_THRESHOLDS
};
