/**
 * Agent Activity Service
 * 
 * Service for fetching agent-specific activity data
 */

/**
 * Get activity data for a specific agent
 * 
 * @param {string} agentId - The ID of the agent to fetch activity for
 * @returns {Promise<Object>} - Promise resolving to activity data
 */
export const getAgentActivity = async (agentId) => {
  try {
    if (!agentId) {
      throw new Error('Agent ID is required');
    }
    
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL || ''}/api/agent/${agentId}/activity`;
    const response = await fetch(apiUrl, {
      headers: {
        'Accept': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.warn(`Failed to fetch activity for agent ${agentId}:`, error);
    
    // Return mock data as fallback
    return {
      agentId,
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
        },
        {
          id: `act-${Date.now()}-3`,
          type: 'api_call',
          content: 'Called external API for data enrichment',
          timestamp: new Date(Date.now() - 4 * 60 * 60000).toISOString(),
          status: 'success'
        }
      ],
      metadata: {
        warning: 'Using mock data as API call failed'
      }
    };
  }
};

export default {
  getAgentActivity
};
