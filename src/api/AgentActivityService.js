/**
 * Agent Activity Service
 * 
 * Service for fetching agent-specific activity data
 */
import { safeFetch } from '../utils/safeFetch';

/**
 * Get activity data for a specific agent
 * 
 * @param {string} agentId - The ID of the agent to fetch activity for
 * @returns {Promise<Object>} - Promise resolving to activity data
 */
export const getAgentActivity = async (agentId) => {
  if (!agentId) {
    throw new Error('Agent ID is required');
  }
  
  return new Promise((resolve) => {
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL || ''}/api/agent/status`;
    
    safeFetch(
      apiUrl,
      (data) => {
        // Find the specific agent in the response
        const agentData = data.find(agent => agent.id === agentId);
        
        if (agentData) {
          resolve({
            agentId,
            status: agentData.status,
            activities: [
              {
                id: `act-${Date.now()}-1`,
                type: 'status_update',
                content: `Agent status: ${agentData.status}`,
                timestamp: new Date().toISOString(),
                status: 'success'
              }
            ],
            metadata: {
              source: 'api'
            }
          });
        } else {
          // Return fallback data if agent not found in response
          resolve(getFallbackActivityData(agentId));
        }
      },
      (hasError) => {
        if (hasError) {
          // Return fallback data on error
          resolve(getFallbackActivityData(agentId));
        }
      },
      8000 // 8 second timeout
    );
  });
};

/**
 * Get fallback activity data for an agent
 * 
 * @param {string} agentId - The ID of the agent
 * @returns {Object} - Fallback activity data
 */
const getFallbackActivityData = (agentId) => {
  return {
    agentId,
    status: 'unknown',
    activities: [
      {
        id: `act-${Date.now()}-1`,
        type: 'task_completion',
        content: 'Completed analysis of dataset',
        timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
        status: 'success'
      },
      {
        id: `act-${Date.now()}-2`,
        type: 'memory_access',
        content: 'Retrieved information from memory store',
        timestamp: new Date(Date.now() - 2 * 60 * 60000).toISOString(),
        status: 'success'
      }
    ],
    metadata: {
      warning: 'Using fallback data as API call failed',
      source: 'fallback'
    }
  };
};

export default {
  getAgentActivity
};
