import { useParams, Navigate } from 'react-router-dom';
import AgentChat from '../AgentChat';
import { useState, useEffect } from 'react';

// List of valid agent IDs for validation
const validAgentIds = [
  'core-forge',
  'LifeTree',
  'SiteGen',
  'NEUREAL',
  'ReflectionAgent',
  'CADBuilderAgent',
  'DreamAgent',
  'hal9000',
  'ash-xenomorph',
  'OpsAgent',
  'ObserverAgent',
  'MemoryAgent'
];

export default function AgentRoute() {
  const { agentId } = useParams();
  const [isValidAgent, setIsValidAgent] = useState(true);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if agentId is in our list of valid agents
    const checkAgentValidity = async () => {
      setIsLoading(true);

      // First check against our static list
      if (validAgentIds.includes(agentId)) {
        setIsValidAgent(true);
        setIsLoading(false);
        return;
      }

      // If not in static list, try to verify with API
      try {
        const response = await fetch('/api/system/agents/manifest');
        if (response.ok) {
          const data = await response.json();
          if (data.agents && Array.isArray(data.agents)) {
            // Check if agent exists in the manifest
            const agentExists = data.agents.some(
              (agent) => agent.id === agentId || agent.name === agentId
            );
            setIsValidAgent(agentExists);
          } else {
            // Fallback to static validation if API doesn't return expected format
            setIsValidAgent(validAgentIds.includes(agentId));
          }
        } else {
          // API error, fallback to static validation
          setIsValidAgent(validAgentIds.includes(agentId));
        }
      } catch (error) {
        console.error('Error checking agent validity:', error);
        // API error, fallback to static validation
        setIsValidAgent(validAgentIds.includes(agentId));
      } finally {
        setIsLoading(false);
      }
    };

    if (agentId) {
      checkAgentValidity();
    } else {
      setIsValidAgent(false);
      setIsLoading(false);
    }
  }, [agentId]);

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex flex-col h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
        <p className="text-gray-600">Validating agent...</p>
      </div>
    );
  }

  // Redirect to dashboard if agent is invalid
  if (!isValidAgent) {
    return <Navigate to="/dashboard" replace />;
  }

  // Render AgentChat if agent is valid
  return <AgentChat agentId={agentId} />;
}
