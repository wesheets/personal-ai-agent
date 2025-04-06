/**
 * Agent Utilities
 * 
 * Centralized utilities for agent management and status retrieval
 */
import { controlService } from '../api/ApiService';

/**
 * Get visible agents from the agent status API
 * Single source of truth for agent dropdown across the application
 * 
 * @param {Object} options - Configuration options
 * @param {boolean} options.includeInactive - Whether to include inactive agents (default: false)
 * @param {string[]} options.filterTypes - Filter agents by type (default: include all types)
 * @returns {Promise<Array>} - Array of agent objects with id, name, icon, and status
 */
export const getVisibleAgents = async (options = {}) => {
  const { includeInactive = false, filterTypes = null } = options;
  
  try {
    // Fetch agents from the status API
    const response = await controlService.getAgentStatus();
    
    if (!response || !Array.isArray(response.agents)) {
      console.error('Invalid response from agent status API:', response);
      return getFallbackAgents();
    }
    
    // Filter agents based on options
    let visibleAgents = response.agents;
    
    // Filter out inactive agents if not explicitly included
    if (!includeInactive) {
      visibleAgents = visibleAgents.filter(agent => agent.status === 'active');
    }
    
    // Filter by agent types if specified
    if (filterTypes && Array.isArray(filterTypes) && filterTypes.length > 0) {
      visibleAgents = visibleAgents.filter(agent => 
        agent.type && filterTypes.includes(agent.type)
      );
    }
    
    console.log(`Retrieved ${visibleAgents.length} agents from status API`);
    return visibleAgents;
  } catch (error) {
    console.error('Error fetching agents from status API:', error);
    return getFallbackAgents();
  }
};

/**
 * Get fallback agents when API fails
 * This ensures the UI remains functional even when the API is unavailable
 * 
 * @returns {Array} - Array of fallback agent objects
 */
const getFallbackAgents = () => {
  console.warn('Using fallback agents due to API failure');
  return [
    { id: 'hal9000', name: 'HAL 9000', icon: '🔴', status: 'active', type: 'system' },
    { id: 'ash-xenomorph', name: 'Ash', icon: '🧬', status: 'active', type: 'persona' }
  ];
};

export default {
  getVisibleAgents
};
