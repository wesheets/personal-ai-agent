import { useState, useEffect } from 'react';

// Mock system health data
const mockSystemHealthData = {
  system_health_score: 0.83,
  reflection_avg: 0.72,
  drift_count: 2,
  last_drift_at: "2025-04-21T09:20:00Z",
  cto_warnings: [
    {
      timestamp: "2025-04-21T09:25:00Z",
      issue: "Reflection score below threshold for 3 loops"
    }
  ],
  recent_reroutes: 2
};

function SystemIntegrityPanel() {
  const [expandedSections, setExpandedSections] = useState({
    health: true,
    reflection: true,
    drift: true,
    warnings: true,
    reroutes: true
  });
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  // Handle window resize for responsive design
  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Toggle section expansion
  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // Format timestamp for display
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString([], {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Get color class based on score
  const getHealthScoreColor = (score) => {
    if (score >= 0.8) return "bg-green-500";
    if (score >= 0.6) return "bg-yellow-500";
    return "bg-red-500";
  };

  // Get text color class based on score
  const getHealthScoreTextColor = (score) => {
    if (score >= 0.8) return "text-green-500";
    if (score >= 0.6) return "text-yellow-500";
    return "text-red-500";
  };

  // Flash animation class for critical health
  const getFlashClass = (score) => {
    return score < 0.5 ? "animate-pulse" : "";
  };

  // Determine if we should use compact mode for small screens
  const isCompactMode = windowWidth < 768;

  return (
    <div className="h-full bg-gray-900 w-full p-4 flex flex-col overflow-y-auto">
      <div className="border-b border-gray-800 pb-4 mb-4">
        <h2 className="text-lg font-semibold flex items-center">
          <span className="mr-2">❤️</span>
          System Health
        </h2>
      </div>

      {/* System Health Score */}
      <div className={`mb-6 ${getFlashClass(mockSystemHealthData.system_health_score)}`}>
        <div 
          className="flex justify-between items-center cursor-pointer"
          onClick={() => toggleSection('health')}
        >
          <h3 className={`${isCompactMode ? 'text-sm' : 'text-md'} font-medium text-gray-300 mb-2 flex items-center`}>
            <span className="mr-2">📊</span>
            System Health Score
            <span className="ml-2 text-xs text-gray-500">
              {expandedSections.health ? '▼' : '▶'}
            </span>
          </h3>
          <span className={`${isCompactMode ? 'text-base' : 'text-lg'} font-bold ${getHealthScoreTextColor(mockSystemHealthData.system_health_score)}`}>
            {(mockSystemHealthData.system_health_score * 100).toFixed(0)}%
          </span>
        </div>
        
        {expandedSections.health && (
          <div className="mt-2">
            <div className="w-full bg-gray-700 rounded-full h-4 mb-2">
              <div 
                className={`h-4 rounded-full ${getHealthScoreColor(mockSystemHealthData.system_health_score)}`}
                style={{ width: `${mockSystemHealthData.system_health_score * 100}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-400">
              Overall system cognitive integrity based on reflection, schema, and agent performance.
            </p>
          </div>
        )}
      </div>

      {/* Reflection Confidence */}
      <div className="mb-6">
        <div 
          className="flex justify-between items-center cursor-pointer"
          onClick={() => toggleSection('reflection')}
        >
          <h3 className={`${isCompactMode ? 'text-sm' : 'text-md'} font-medium text-gray-300 mb-2 flex items-center`}>
            <span className="mr-2">🧠</span>
            Reflection Confidence
            <span className="ml-2 text-xs text-gray-500">
              {expandedSections.reflection ? '▼' : '▶'}
            </span>
          </h3>
          <span className={`${isCompactMode ? 'text-base' : 'text-lg'} font-bold ${getHealthScoreTextColor(mockSystemHealthData.reflection_avg)}`}>
            {(mockSystemHealthData.reflection_avg * 100).toFixed(0)}%
          </span>
        </div>
        
        {expandedSections.reflection && (
          <div className="mt-2">
            <div className="w-full bg-gray-700 rounded-full h-4 mb-2">
              <div 
                className={`h-4 rounded-full ${getHealthScoreColor(mockSystemHealthData.reflection_avg)}`}
                style={{ width: `${mockSystemHealthData.reflection_avg * 100}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-400">
              Average confidence score from agent reflection processes.
            </p>
          </div>
        )}
      </div>

      {/* Schema Drift Logs */}
      <div className="mb-6">
        <div 
          className="flex justify-between items-center cursor-pointer"
          onClick={() => toggleSection('drift')}
        >
          <h3 className={`${isCompactMode ? 'text-sm' : 'text-md'} font-medium text-gray-300 mb-2 flex items-center`}>
            <span className="mr-2">📈</span>
            Schema Drift Logs
            <span className="ml-2 text-xs text-gray-500">
              {expandedSections.drift ? '▼' : '▶'}
            </span>
          </h3>
          <span className={`px-2 py-1 rounded-md text-xs font-medium ${
            mockSystemHealthData.drift_count > 0 ? 'bg-yellow-900 text-yellow-300' : 'bg-green-900 text-green-300'
          }`}>
            {mockSystemHealthData.drift_count} detected
          </span>
        </div>
        
        {expandedSections.drift && (
          <div className="mt-2">
            <div className="bg-gray-800 rounded-md p-3 border border-gray-700">
              <div className={`${isCompactMode ? 'flex-col' : 'flex justify-between items-center'} mb-2`}>
                <span className="text-sm text-gray-300">Last drift detected:</span>
                <span className="text-xs text-cyan-400">
                  {formatTime(mockSystemHealthData.last_drift_at)}
                </span>
              </div>
              <p className="text-xs text-gray-400">
                Schema drift occurs when the system's internal model diverges from expected patterns.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* CTO Warnings */}
      <div className="mb-6">
        <div 
          className="flex justify-between items-center cursor-pointer"
          onClick={() => toggleSection('warnings')}
        >
          <h3 className={`${isCompactMode ? 'text-sm' : 'text-md'} font-medium text-gray-300 mb-2 flex items-center`}>
            <span className="mr-2">⚠️</span>
            CTO Warnings
            <span className="ml-2 text-xs text-gray-500">
              {expandedSections.warnings ? '▼' : '▶'}
            </span>
          </h3>
          <span className={`px-2 py-1 rounded-md text-xs font-medium ${
            mockSystemHealthData.cto_warnings.length > 0 ? 'bg-red-900 text-red-300' : 'bg-green-900 text-green-300'
          }`}>
            {mockSystemHealthData.cto_warnings.length} active
          </span>
        </div>
        
        {expandedSections.warnings && (
          <div className="mt-2">
            {mockSystemHealthData.cto_warnings.length > 0 ? (
              <div className="bg-gray-800 rounded-md border border-red-800 p-3 font-mono">
                {mockSystemHealthData.cto_warnings.map((warning, index) => (
                  <div key={index} className="mb-2 last:mb-0">
                    <div className={`${isCompactMode ? 'flex-col' : 'flex justify-between items-center'} mb-1`}>
                      <span className="text-red-400 text-xs">WARNING:</span>
                      <span className="text-xs text-gray-400">
                        {formatTime(warning.timestamp)}
                      </span>
                    </div>
                    <p className={`${isCompactMode ? 'text-xs' : 'text-sm'} text-white break-words`}>
                      {warning.issue}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-gray-800 rounded-md p-3 border border-green-800">
                <p className="text-sm text-green-400">No active CTO warnings</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Loop Deviation Tracker */}
      <div className="mb-6">
        <div 
          className="flex justify-between items-center cursor-pointer"
          onClick={() => toggleSection('reroutes')}
        >
          <h3 className={`${isCompactMode ? 'text-sm' : 'text-md'} font-medium text-gray-300 mb-2 flex items-center`}>
            <span className="mr-2">🔄</span>
            Loop Deviation Tracker
            <span className="ml-2 text-xs text-gray-500">
              {expandedSections.reroutes ? '▼' : '▶'}
            </span>
          </h3>
          <span className={`px-2 py-1 rounded-md text-xs font-medium ${
            mockSystemHealthData.recent_reroutes > 0 ? 'bg-yellow-900 text-yellow-300' : 'bg-green-900 text-green-300'
          }`}>
            {mockSystemHealthData.recent_reroutes} reroutes
          </span>
        </div>
        
        {expandedSections.reroutes && (
          <div className="mt-2">
            <div className="bg-gray-800 rounded-md p-3 border border-gray-700">
              <div className={`${isCompactMode ? 'flex-col space-y-2' : 'flex items-center justify-between'} mb-2`}>
                <span className="text-sm text-gray-300">Recent loop reroutes:</span>
                <div className="flex">
                  {[...Array(5)].map((_, i) => (
                    <div 
                      key={i} 
                      className={`w-3 h-3 rounded-full mx-1 ${
                        i < mockSystemHealthData.recent_reroutes ? 'bg-yellow-500' : 'bg-gray-600'
                      }`}
                    ></div>
                  ))}
                </div>
              </div>
              <p className="text-xs text-gray-400">
                Count of agent reroutes from last 5 loops. Reroutes occur when the orchestrator changes the planned agent sequence.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* System Actions */}
      <div className="mt-auto pt-4 border-t border-gray-800">
        <button className="w-full bg-gray-800 hover:bg-gray-700 text-cyan-400 py-2 rounded-md text-sm font-medium transition-colors">
          Run System Diagnostic
        </button>
      </div>
    </div>
  );
}

export default SystemIntegrityPanel;
