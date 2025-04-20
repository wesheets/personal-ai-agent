import { useState, useEffect } from 'react';

function OverrideControls() {
  const [selectedAgent, setSelectedAgent] = useState('');
  const [loopComplete, setLoopComplete] = useState(false);
  const [actionStatus, setActionStatus] = useState(null);
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  // Handle window resize for responsive design
  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // List of available agents
  const agents = [
    { id: 'hal', name: 'HAL', color: 'blue' },
    { id: 'nova', name: 'NOVA', color: 'purple' },
    { id: 'critic', name: 'CRITIC', color: 'yellow' },
    { id: 'ash', name: 'ASH', color: 'teal' },
    { id: 'sage', name: 'SAGE', color: 'green' },
    { id: 'orchestrator', name: 'ORCHESTRATOR', color: 'gray' }
  ];

  // Handle setting next agent
  const handleSetNextAgent = () => {
    if (!selectedAgent) {
      setActionStatus({
        type: 'error',
        message: 'Please select an agent first'
      });
      return;
    }

    // Mock API call
    console.log(`POST to /api/operator/override/next-agent with agent: ${selectedAgent}`);
    
    // Show success message
    setActionStatus({
      type: 'success',
      message: `Next agent set to ${agents.find(a => a.id === selectedAgent).name}`
    });

    // Reset selection after successful action
    setTimeout(() => {
      setSelectedAgent('');
      setActionStatus(null);
    }, 3000);
  };

  // Handle marking loop as complete
  const handleLoopComplete = () => {
    // Mock API call
    console.log(`POST to /api/operator/override/loop-complete with status: ${loopComplete}`);
    
    // Show success message
    setActionStatus({
      type: 'success',
      message: loopComplete ? 'Loop marked as complete' : 'Loop marked as incomplete'
    });

    // Reset status after successful action
    setTimeout(() => {
      setActionStatus(null);
    }, 3000);
  };

  // Handle running system diagnostic
  const handleRunDiagnostic = () => {
    // Mock API call
    console.log('POST to /api/debug/cto/system-health/{project_id}');
    
    // Show success message
    setActionStatus({
      type: 'success',
      message: 'System diagnostic initiated'
    });

    // Reset status after successful action
    setTimeout(() => {
      setActionStatus(null);
    }, 3000);
  };

  // Handle resetting frozen agent
  const handleResetFrozenAgent = () => {
    // Mock API call
    console.log('POST to /api/debug/agent/reset/{project_id}');
    
    // Show success message
    setActionStatus({
      type: 'success',
      message: 'Frozen agent reset initiated'
    });

    // Reset status after successful action
    setTimeout(() => {
      setActionStatus(null);
    }, 3000);
  };

  // Get color class for agent
  const getAgentColorClass = (agentId) => {
    const agent = agents.find(a => a.id === agentId);
    if (!agent) return 'text-white';
    
    switch (agent.color) {
      case 'blue': return 'text-blue-400';
      case 'purple': return 'text-purple-400';
      case 'yellow': return 'text-yellow-400';
      case 'teal': return 'text-teal-400';
      case 'green': return 'text-green-400';
      case 'gray': return 'text-gray-400';
      default: return 'text-white';
    }
  };

  // Determine if we should use compact mode for small screens
  const isCompactMode = windowWidth < 768;

  return (
    <div className="bg-gray-900 rounded-lg p-4 md:p-6 border border-gray-800 w-full max-w-2xl mx-auto">
      <div className="border-b border-gray-800 pb-4 mb-4 md:mb-6">
        <h2 className={`${isCompactMode ? 'text-base' : 'text-lg'} font-semibold text-white flex items-center`}>
          <span className="mr-2">🔧</span>
          Operator Override Controls
        </h2>
      </div>

      {/* Status message */}
      {actionStatus && (
        <div className={`mb-4 md:mb-6 p-2 md:p-3 rounded-md ${
          actionStatus.type === 'success' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
        }`}>
          {actionStatus.message}
        </div>
      )}

      {/* Set Next Agent */}
      <div className="mb-4 md:mb-6">
        <label className={`block text-gray-400 mb-1 md:mb-2 ${isCompactMode ? 'text-sm' : 'font-medium'}`}>
          🔁 Set Next Agent
        </label>
        <div className={`${isCompactMode ? 'flex flex-col space-y-2' : 'flex space-x-2'}`}>
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            className="bg-gray-800 text-white border border-gray-700 rounded-md px-3 py-2 flex-grow focus:outline-none focus:ring-2 focus:ring-cyan-500"
          >
            <option value="">Select agent...</option>
            {agents.map(agent => (
              <option 
                key={agent.id} 
                value={agent.id}
                className={getAgentColorClass(agent.id)}
              >
                {agent.name}
              </option>
            ))}
          </select>
          <button
            onClick={handleSetNextAgent}
            className={`bg-gray-800 hover:bg-gray-700 text-cyan-400 px-4 py-2 rounded-md transition-colors ${
              isCompactMode ? 'w-full' : ''
            }`}
          >
            Set
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          Override the Orchestrator's next agent selection
        </p>
      </div>

      {/* Mark Loop Complete */}
      <div className="mb-4 md:mb-6">
        <label className={`block text-gray-400 mb-1 md:mb-2 ${isCompactMode ? 'text-sm' : 'font-medium'}`}>
          ✅ Mark Loop Complete
        </label>
        <div className={`${isCompactMode ? 'flex flex-col space-y-2' : 'flex items-center space-x-2'}`}>
          <div className="flex items-center">
            <input
              type="checkbox"
              id="loop-complete"
              checked={loopComplete}
              onChange={(e) => setLoopComplete(e.target.checked)}
              className="h-4 w-4 text-cyan-500 focus:ring-cyan-500 border-gray-700 rounded"
            />
            <label htmlFor="loop-complete" className="ml-2 text-white">
              {loopComplete ? 'Complete' : 'Incomplete'}
            </label>
          </div>
          <button
            onClick={handleLoopComplete}
            className={`bg-gray-800 hover:bg-gray-700 text-cyan-400 px-4 py-2 rounded-md transition-colors ${
              isCompactMode ? 'w-full' : ''
            }`}
          >
            Update
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          Manually mark the current loop as complete
        </p>
      </div>

      {/* Run Diagnostic */}
      <div className="mb-4 md:mb-6">
        <label className={`block text-gray-400 mb-1 md:mb-2 ${isCompactMode ? 'text-sm' : 'font-medium'}`}>
          🧠 Run Diagnostic
        </label>
        <button
          onClick={handleRunDiagnostic}
          className="w-full bg-gray-800 hover:bg-gray-700 text-cyan-400 py-2 rounded-md transition-colors"
        >
          Run System Diagnostic
        </button>
        <p className="text-xs text-gray-500 mt-1">
          Trigger a full system health check and cognitive integrity scan
        </p>
      </div>

      {/* Reset Frozen Agent */}
      <div className="mb-4 md:mb-6">
        <label className={`block text-gray-400 mb-1 md:mb-2 ${isCompactMode ? 'text-sm' : 'font-medium'}`}>
          🛑 Reset Frozen Agent
        </label>
        <button
          onClick={handleResetFrozenAgent}
          className="w-full bg-red-900 hover:bg-red-800 text-white py-2 rounded-md transition-colors"
        >
          Reset Frozen Agent
        </button>
        <p className="text-xs text-gray-500 mt-1">
          Emergency reset for stalled or unresponsive agents
        </p>
      </div>

      <div className="border-t border-gray-800 pt-3 md:pt-4 mt-4 md:mt-6">
        <p className="text-xs text-gray-500">
          These controls allow direct operator intervention in the cognitive loop.
          Use with caution as they override the Orchestrator's planning.
        </p>
      </div>
    </div>
  );
}

export default OverrideControls;
