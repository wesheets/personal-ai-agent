import { useState, useEffect } from 'react';

// Mock API data - would be replaced with actual API call
const mockApiData = {
  loop_count: 22,
  completed_steps: ["hal", "nova"],
  next_recommended_agent: "critic",
  loop_complete: false,
  project_id: "lifetree_001"
};

// Agent color mapping
const agentColors = {
  hal: "bg-blue-500",
  nova: "bg-purple-500",
  critic: "bg-yellow-500",
  planner: "bg-green-500",
  researcher: "bg-red-500",
  writer: "bg-indigo-500"
};

function LoopStatusPanel() {
  const [loopData, setLoopData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API fetch
    const fetchData = async () => {
      try {
        // In a real implementation, this would be:
        // const response = await fetch(`/api/project/state?project_id=${projectId}`);
        // const data = await response.json();
        
        // Using mock data for now
        setTimeout(() => {
          setLoopData(mockApiData);
          setLoading(false);
        }, 500);
      } catch (error) {
        console.error("Error fetching loop data:", error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 mb-4 shadow-md border border-gray-700">
        <div className="animate-pulse flex flex-col space-y-3">
          <div className="h-6 bg-gray-700 rounded w-3/4"></div>
          <div className="h-4 bg-gray-700 rounded w-1/2"></div>
          <div className="h-10 bg-gray-700 rounded"></div>
          <div className="h-4 bg-gray-700 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  if (!loopData) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 mb-4 shadow-md border border-gray-700">
        <p className="text-gray-400">No loop data available</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-4 mb-4 shadow-md border border-gray-700">
      {/* Loop Header */}
      <div className="flex items-center justify-between mb-3 border-b border-gray-700 pb-2">
        <h3 className="text-lg font-semibold flex items-center">
          <span className="text-cyan-400 mr-2">Loop {loopData.loop_count}</span>
          {loopData.loop_complete ? (
            <span className="text-green-500 text-xl" title="Loop Complete">✅</span>
          ) : (
            <span className="text-cyan-500 animate-spin text-xl" title="Loop In Progress">🔄</span>
          )}
        </h3>
        <span className="text-xs text-gray-500">Project: {loopData.project_id}</span>
      </div>

      {/* Completed Agents */}
      <div className="mb-3">
        <h4 className="text-sm text-gray-400 mb-2">Completed Agents:</h4>
        <div className="flex flex-wrap gap-2">
          {loopData.completed_steps.length > 0 ? (
            loopData.completed_steps.map((agent) => (
              <span 
                key={agent}
                className={`${agentColors[agent] || 'bg-gray-600'} px-2 py-1 rounded text-xs font-medium uppercase`}
              >
                {agent}
              </span>
            ))
          ) : (
            <span className="text-gray-500 text-sm">No agents completed yet</span>
          )}
        </div>
      </div>

      {/* Current/Next Agent */}
      <div className="mb-3">
        <h4 className="text-sm text-gray-400 mb-2">Next Agent:</h4>
        <div className="flex items-center">
          <span 
            className={`${agentColors[loopData.next_recommended_agent] || 'bg-gray-600'} 
                      px-3 py-1.5 rounded text-sm font-medium uppercase
                      animate-pulse shadow-lg shadow-cyan-500/20`}
          >
            {loopData.next_recommended_agent}
          </span>
        </div>
      </div>

      {/* Health Status (Optional) */}
      {Math.random() > 0.5 && (
        <div className="mt-4 pt-3 border-t border-gray-700">
          <div className="flex items-center">
            <span className="bg-yellow-500/20 text-yellow-300 text-xs px-2 py-1 rounded-full">
              Health Tip: Consider reviewing agent sequence
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default LoopStatusPanel;
