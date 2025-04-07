import { createContext, useContext, useState, useEffect } from 'react';

const AgentContext = createContext();

export const AgentProvider = ({ children }) => {
  const [agents, setAgents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Fetch agents from API
  const fetchAgents = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Authentication required');
      }
      
      const response = await fetch('/api/agents', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch agents');
      }
      
      const data = await response.json();
      setAgents(data.agents || []);
    } catch (err) {
      console.error('Error fetching agents:', err);
      setError(err.message);
      setAgents([]);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Create a new agent
  const createAgent = async (agentData) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Authentication required');
      }
      
      const response = await fetch('/api/agents', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(agentData)
      });
      
      if (!response.ok) {
        throw new Error('Failed to create agent');
      }
      
      const data = await response.json();
      setAgents(prev => [...prev, data.agent]);
      return data.agent;
    } catch (err) {
      console.error('Error creating agent:', err);
      throw err;
    }
  };
  
  // Update an existing agent
  const updateAgent = async (agentId, agentData) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Authentication required');
      }
      
      const response = await fetch(`/api/agents/${agentId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(agentData)
      });
      
      if (!response.ok) {
        throw new Error('Failed to update agent');
      }
      
      const data = await response.json();
      setAgents(prev => prev.map(agent => 
        agent.id === agentId ? data.agent : agent
      ));
      return data.agent;
    } catch (err) {
      console.error('Error updating agent:', err);
      throw err;
    }
  };
  
  // Delete an agent
  const deleteAgent = async (agentId) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Authentication required');
      }
      
      const response = await fetch(`/api/agents/${agentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete agent');
      }
      
      setAgents(prev => prev.filter(agent => agent.id !== agentId));
      return true;
    } catch (err) {
      console.error('Error deleting agent:', err);
      throw err;
    }
  };
  
  // Get system agents (HAL and ASH)
  const getSystemAgents = () => {
    return agents.filter(agent => agent.isSystem);
  };
  
  // Get user agents (non-system agents)
  const getUserAgents = () => {
    return agents.filter(agent => !agent.isSystem);
  };
  
  // Get agent by ID
  const getAgentById = (agentId) => {
    return agents.find(agent => agent.id === agentId);
  };
  
  // Refresh agents list
  const refreshAgents = () => {
    fetchAgents();
  };
  
  // Context value
  const value = {
    agents,
    isLoading,
    error,
    fetchAgents,
    createAgent,
    updateAgent,
    deleteAgent,
    getSystemAgents,
    getUserAgents,
    getAgentById,
    refreshAgents
  };
  
  return (
    <AgentContext.Provider value={value}>
      {children}
    </AgentContext.Provider>
  );
};

export const useAgents = () => {
  const context = useContext(AgentContext);
  if (context === undefined) {
    throw new Error('useAgents must be used within an AgentProvider');
  }
  return context;
};

export default AgentContext;
