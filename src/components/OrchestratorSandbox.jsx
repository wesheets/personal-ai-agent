import { useState, useEffect } from 'react';
import SendToAgentsButton from './SendToAgentsButton';

function OrchestratorSandbox({ orchestratorData, onPlanConfirm, pendingConfirmation, executionStarted }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);
  
  // Toggle expanded state
  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };
  
  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };
    
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);
  
  // Format timestamp for display
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  // Agent color mapping
  const agentColors = {
    hal: "text-blue-400",
    nova: "text-purple-400",
    critic: "text-yellow-400",
    ash: "text-teal-400",
    operator: "text-cyan-400",
    cto: "text-red-400",
    orchestrator: "text-gray-400"
  };
  
  // Mock data for when no real data is available
  const mockOrchestratorData = {
    loop: 22,
    last_agent: "critic",
    next_agent: "hal",
    reason: "Critic validated the structure. Moving to HAL to implement the next component.",
    timestamp: new Date().toISOString()
  };
  
  // Use provided data or mock data
  const data = orchestratorData || mockOrchestratorData;
  
  // Determine if we should use compact mode for small screens
  const isCompactMode = windowWidth < 768;
  
  return (
    <div className="fixed bottom-4 right-4 z-10">
      {/* Collapsed view */}
      {!isExpanded && (
        <div className="flex flex-col">
          <div 
            className="bg-gray-800 border border-gray-700 rounded-lg shadow-lg p-3 w-64 cursor-pointer hover:border-gray-600 transition-colors"
            onClick={toggleExpanded}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center">
                <span className="text-cyan-400 mr-1">🧠</span>
                <h3 className="text-sm font-medium text-white">Orchestrator</h3>
              </div>
              <span className="text-cyan-400 text-xs px-1.5 py-0.5 bg-gray-700 rounded">
                Loop {data.loop}
              </span>
            </div>
            
            <div className="text-xs">
              <div className="flex justify-between mb-1">
                <span className="text-gray-500">Last:</span>
                <span className={`${agentColors[data.last_agent.toLowerCase()] || 'text-gray-400'}`}>
                  {data.last_agent}
                </span>
              </div>
              <div className="flex justify-between mb-1">
                <span className="text-gray-500">Next:</span>
                <span className={`${agentColors[data.next_agent.toLowerCase()] || 'text-gray-400'}`}>
                  {data.next_agent}
                </span>
              </div>
              <div className="text-gray-400 text-xs mt-2 line-clamp-2">
                {data.reason}
              </div>
              
              {/* Show planning indicator if loop_plan exists */}
              {data.loop_plan && (
                <div className="mt-2 pt-2 border-t border-gray-700">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">Planning:</span>
                    <span className="text-cyan-400 text-xs">
                      {data.loop_plan.agents.length} agents
                    </span>
                  </div>
                  <div className="text-gray-400 text-xs mt-1">
                    {data.loop_plan.planned_files.length} files planned
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* SendToAgentsButton beneath OrchestratorSandbox */}
          {pendingConfirmation && !executionStarted && data.loop_plan && (
            <div className="mt-2">
              <SendToAgentsButton 
                loopId={data.loop}
                onConfirm={onPlanConfirm}
                visible={true}
              />
            </div>
          )}
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
                  <span className="text-cyan-400 font-medium">{data.loop}</span>
                </div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400">Last Agent:</span>
                  <span className={`${agentColors[data.last_agent.toLowerCase()] || 'text-gray-300'} font-medium`}>
                    {data.last_agent}
                  </span>
                </div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400">Next Agent:</span>
                  <span className={`${agentColors[data.next_agent.toLowerCase()] || 'text-gray-300'} font-medium`}>
                    {data.next_agent}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Timestamp:</span>
                  <span className="text-gray-300">{formatTime(data.timestamp)}</span>
                </div>
              </div>
              
              <div className="mb-4">
                <h3 className="text-sm font-medium text-gray-300 mb-2">Reasoning:</h3>
                <div className="bg-gray-900 p-3 rounded font-mono text-sm text-gray-300">
                  {data.reason}
                </div>
              </div>
              
              {/* Loop plan details if available */}
              {data.loop_plan && (
                <>
                  <div className="mb-4">
                    <h3 className="text-sm font-medium text-gray-300 mb-2">Loop Plan:</h3>
                    <div className="bg-gray-900 p-3 rounded font-mono text-sm">
                      <div className="mb-2">
                        <span className="text-gray-500">Agents: </span>
                        {data.loop_plan.agents.map((agent, i) => (
                          <span key={i} className={`${
                            agent.toLowerCase() === 'hal' ? 'text-blue-400' :
                            agent.toLowerCase() === 'nova' ? 'text-purple-400' :
                            agent.toLowerCase() === 'critic' ? 'text-yellow-400' :
                            agent.toLowerCase() === 'ash' ? 'text-teal-400' :
                            'text-gray-300'
                          } ${i < data.loop_plan.agents.length - 1 ? 'mr-1' : ''}`}>
                            {agent}{i < data.loop_plan.agents.length - 1 ? ' → ' : ''}
                          </span>
                        ))}
                      </div>
                      <div className="mb-2">
                        <span className="text-gray-500">Goals: </span>
                        {data.loop_plan.goals.map((goal, i) => (
                          <span key={i} className="text-gray-300">
                            {goal}{i < data.loop_plan.goals.length - 1 ? ', ' : ''}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  {/* File proposal preview */}
                  <div className="mb-4">
                    <h3 className="text-sm font-medium text-gray-300 mb-2">File Proposal:</h3>
                    <div className="bg-gray-900 p-3 rounded font-mono text-sm">
                      {data.loop_plan.planned_files.map((file, i) => (
                        <div key={i} className="mb-1 last:mb-0">
                          <span className={`${agentColors[data.loop_plan.agents[0].toLowerCase()] || 'text-gray-300'}`}>
                            {data.loop_plan.agents[0]}
                          </span> 
                          <span className="text-gray-300"> is preparing: </span>
                          <span className="text-cyan-300">{file}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}
              
              {/* Agent flow visualization */}
              <div>
                <h3 className="text-sm font-medium text-gray-300 mb-2">Agent Flow:</h3>
                <div className="bg-gray-900 p-3 rounded flex flex-wrap items-center justify-between">
                  {data.loop_plan ? (
                    data.loop_plan.agents.map((agent, i) => (
                      <div key={i} className="flex items-center">
                        <div className="flex flex-col items-center mb-2 sm:mb-0">
                          <span className={`${agentColors[agent.toLowerCase()] || 'text-gray-300'} mb-1`}>
                            {agent.toUpperCase()}
                          </span>
                          <span className="text-gray-500 text-xs">
                            {data.loop_plan.goals[i] || 'Process'}
                          </span>
                        </div>
                        {i < data.loop_plan.agents.length - 1 && (
                          <span className="text-gray-600 mx-2 hidden sm:block">→</span>
                        )}
                      </div>
                    ))
                  ) : (
                    <>
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
                    </>
                  )}
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
