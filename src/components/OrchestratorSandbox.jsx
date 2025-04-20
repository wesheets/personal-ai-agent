import { useState, useEffect } from 'react';

// Mock data for orchestrator decisions
const mockOrchestratorData = {
  loop: 23,
  last_agent: "nova",
  next_agent: "critic",
  reason: "HAL created structure, NOVA added logic. CRITIC will validate.",
  timestamp: "2025-04-20T16:02:14Z"
};

function OrchestratorSandbox() {
  const [isExpanded, setIsExpanded] = useState(false);
  const [orchestratorData, setOrchestratorData] = useState(mockOrchestratorData);

  // Toggle expanded state
  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  // Format timestamp
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Agent color mapping
  const agentColors = {
    hal: "text-blue-400",
    nova: "text-purple-400",
    critic: "text-yellow-400",
    planner: "text-green-400",
    researcher: "text-red-400",
    writer: "text-indigo-400"
  };

  // Simulate API fetch (in real implementation, this would fetch from /api/project/state)
  useEffect(() => {
    // This would be replaced with actual API call in Phase 11.1
    const fetchData = async () => {
      try {
        // Simulating API response delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        // In real implementation: const response = await fetch('/api/project/state?project_id=...');
        // const data = await response.json();
        setOrchestratorData(mockOrchestratorData);
      } catch (error) {
        console.error('Error fetching orchestrator data:', error);
      }
    };

    fetchData();
    // Set up polling interval (every 10 seconds)
    const intervalId = setInterval(fetchData, 10000);
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="w-full">
      {/* Collapsed view */}
      {!isExpanded && (
        <div className="bg-gray-800 rounded-lg shadow-md border border-gray-700 overflow-hidden">
          {/* Header with expand button */}
          <div 
            className="flex items-center justify-between px-3 py-2 border-t-2 border-cyan-500 cursor-pointer"
            onClick={toggleExpanded}
          >
            <div className="flex items-center">
              <span className="text-xs text-cyan-400 mr-1">🧠</span>
              <h3 className="text-sm font-medium text-gray-300">Orchestrator Thinking</h3>
            </div>
            <div className="flex items-center">
              <span className="text-xs text-gray-500 mr-2">Loop {orchestratorData.loop}</span>
              <button 
                className="text-gray-400 hover:text-cyan-400 text-xs"
                aria-label="Expand"
                title="Expand"
              >
                ↕
              </button>
            </div>
          </div>
          
          {/* Content */}
          <div className="px-3 py-2 text-xs font-mono">
            <div className="flex justify-between mb-1">
              <span className="text-gray-500">Last:</span>
              <span className={`${agentColors[orchestratorData.last_agent.toLowerCase()] || 'text-gray-400'}`}>
                {orchestratorData.last_agent}
              </span>
            </div>
            <div className="flex justify-between mb-1">
              <span className="text-gray-500">Next:</span>
              <span className={`${agentColors[orchestratorData.next_agent.toLowerCase()] || 'text-gray-400'}`}>
                {orchestratorData.next_agent}
              </span>
            </div>
            <div className="text-gray-400 text-xs mt-2 line-clamp-2">
              {orchestratorData.reason}
            </div>
          </div>
        </div>
      )}
      
      {/* Expanded modal view */}
      {isExpanded && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg shadow-xl border border-gray-700 w-full max-w-2xl max-h-[80vh] overflow-hidden">
            {/* Modal header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700">
              <div className="flex items-center">
                <span className="text-cyan-400 mr-2">🧠</span>
                <h2 className="text-lg font-medium text-white">Orchestrator Thinking</h2>
              </div>
              <button 
                onClick={toggleExpanded}
                className="text-gray-400 hover:text-white"
                aria-label="Close"
              >
                ✕
              </button>
            </div>
            
            {/* Modal content */}
            <div className="p-4 overflow-y-auto max-h-[calc(80vh-4rem)]">
              <div className="mb-4 pb-3 border-b border-gray-700">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400">Loop:</span>
                  <span className="text-cyan-400 font-medium">{orchestratorData.loop}</span>
                </div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400">Last Agent:</span>
                  <span className={`${agentColors[orchestratorData.last_agent.toLowerCase()] || 'text-gray-300'} font-medium`}>
                    {orchestratorData.last_agent}
                  </span>
                </div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400">Next Agent:</span>
                  <span className={`${agentColors[orchestratorData.next_agent.toLowerCase()] || 'text-gray-300'} font-medium`}>
                    {orchestratorData.next_agent}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Timestamp:</span>
                  <span className="text-gray-300">{formatTime(orchestratorData.timestamp)}</span>
                </div>
              </div>
              
              <div className="mb-4">
                <h3 className="text-sm font-medium text-gray-300 mb-2">Reasoning:</h3>
                <div className="bg-gray-900 p-3 rounded font-mono text-sm text-gray-300">
                  {orchestratorData.reason}
                </div>
              </div>
              
              {/* Optional file proposal preview */}
              <div className="mb-4">
                <h3 className="text-sm font-medium text-gray-300 mb-2">File Proposal:</h3>
                <div className="bg-gray-900 p-3 rounded font-mono text-sm">
                  <span className="text-cyan-400">HAL</span> <span className="text-gray-300">is preparing: </span>
                  <span className="text-yellow-300">MemoryTimeline.jsx</span>
                </div>
              </div>
              
              {/* Agent flow visualization (placeholder) */}
              <div>
                <h3 className="text-sm font-medium text-gray-300 mb-2">Agent Flow:</h3>
                <div className="bg-gray-900 p-3 rounded flex flex-wrap items-center justify-between">
                  <div className="flex flex-col items-center mb-2 sm:mb-0">
                    <span className="text-blue-400 mb-1">HAL</span>
                    <span className="text-gray-500 text-xs">Structure</span>
                  </div>
                  <span className="text-gray-600 hidden sm:block">→</span>
                  <div className="flex flex-col items-center mb-2 sm:mb-0">
                    <span className="text-purple-400 mb-1">NOVA</span>
                    <span className="text-gray-500 text-xs">Logic</span>
                  </div>
                  <span className="text-gray-600 hidden sm:block">→</span>
                  <div className="flex flex-col items-center">
                    <span className="text-yellow-400 mb-1">CRITIC</span>
                    <span className="text-gray-500 text-xs">Validate</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default OrchestratorSandbox;
