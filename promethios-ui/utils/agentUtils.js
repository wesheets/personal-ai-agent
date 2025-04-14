// Agent utilities for Promethios UI
const agentUtils = {
  // Format agent status for display
  formatStatus: (status) => {
    if (!status) return 'unknown';
    return status.toLowerCase();
  },
  
  // Get color for agent status
  getStatusColor: (status) => {
    if (!status) return 'gray.500';
    
    const statusMap = {
      active: 'green.500',
      thinking: 'blue.500',
      idle: 'gray.500',
      error: 'red.500',
      waiting: 'orange.500'
    };
    
    return statusMap[status.toLowerCase()] || 'gray.500';
  },
  
  // Format timestamp for display
  formatTimestamp: (timestamp) => {
    if (!timestamp) return '';
    
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    } catch (error) {
      console.log('Error formatting timestamp:', error);
      return '';
    }
  },
  
  // Truncate text with ellipsis
  truncateText: (text, maxLength = 100) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    
    return text.substring(0, maxLength) + '...';
  },
  
  // Safe JSON parse with fallback
  safeJsonParse: (jsonString, fallback = {}) => {
    if (!jsonString) return fallback;
    
    try {
      return JSON.parse(jsonString);
    } catch (error) {
      console.log('Error parsing JSON:', error);
      return fallback;
    }
  },
  
  // Get visible agents (mock implementation)
  getVisibleAgents: async (options = {}) => {
    // Mock implementation that returns sample agents
    const mockAgents = [
      {
        id: 'orchestrator',
        name: 'Orchestrator',
        type: 'system',
        description: 'System orchestration agent',
        icon: '🔄'
      },
      {
        id: 'hal',
        name: 'HAL',
        type: 'persona',
        description: 'Research and information agent',
        icon: '🔍',
        tone: 'analytical'
      },
      {
        id: 'builder',
        name: 'Builder',
        type: 'persona',
        description: 'Code and development agent',
        icon: '🛠️',
        tone: 'technical'
      },
      {
        id: 'ops',
        name: 'Ops',
        type: 'system',
        description: 'Operations and deployment agent',
        icon: '🚀'
      }
    ];
    
    // If includeInactive is false, filter out inactive agents
    if (!options.includeInactive) {
      return mockAgents.filter(agent => agent.status !== 'inactive');
    }
    
    return mockAgents;
  }
};

export default agentUtils;
export const { getVisibleAgents } = agentUtils;
