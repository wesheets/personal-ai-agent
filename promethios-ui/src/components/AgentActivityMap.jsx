import React, { useState, useEffect } from 'react';

/**
 * AgentActivityMap component
 *
 * Displays agent health status, uptime, response rate, and error percentage
 */
const AgentActivityMap = () => {
  const [agentStatus, setAgentStatus] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Fetch agent status data
  useEffect(() => {
    const fetchAgentStatus = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch('/api/agent/status');

        if (!response.ok) {
          throw new Error(`Failed to fetch agent status: ${response.status}`);
        }

        const data = await response.json();

        // Validate that the response contains clean JSON
        if (data && Array.isArray(data.agents)) {
          setAgentStatus(data.agents);
        } else if (Array.isArray(data)) {
          setAgentStatus(data);
        } else {
          throw new Error('Invalid agent status data format');
        }

        setLastUpdated(new Date());
      } catch (error) {
        console.error('Error fetching agent status:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAgentStatus();

    // Set up polling interval (every 60 seconds)
    const intervalId = setInterval(fetchAgentStatus, 60000);

    // Cleanup
    return () => clearInterval(intervalId);
  }, []);

  // Calculate status indicators
  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'online':
      case 'active':
      case 'healthy':
        return 'bg-green-500';
      case 'idle':
      case 'standby':
        return 'bg-blue-500';
      case 'busy':
      case 'processing':
        return 'bg-yellow-500';
      case 'error':
      case 'offline':
      case 'unavailable':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getErrorClass = (errorRate) => {
    if (errorRate === undefined || errorRate === null) return 'text-gray-600';
    if (errorRate < 1) return 'text-green-600';
    if (errorRate < 5) return 'text-yellow-600';
    if (errorRate < 10) return 'text-orange-600';
    return 'text-red-600';
  };

  // Render loading state
  if (loading && agentStatus.length === 0) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-md">
        <div className="flex flex-col items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-600">Loading agent activity data...</p>
        </div>
      </div>
    );
  }

  // Render error state
  if (error && !loading && agentStatus.length === 0) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-md">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> {error}</span>
        </div>
        <div className="flex justify-center">
          <button
            onClick={() => {
              setLoading(true);
              setError(null);
              // Trigger a new fetch
              fetch('/api/agent/status')
                .then((res) => res.json())
                .then((data) => {
                  if (data && Array.isArray(data.agents)) {
                    setAgentStatus(data.agents);
                  } else if (Array.isArray(data)) {
                    setAgentStatus(data);
                  } else {
                    throw new Error('Invalid agent status data format');
                  }
                  setLastUpdated(new Date());
                  setLoading(false);
                })
                .catch((err) => {
                  setError(err.message);
                  setLoading(false);
                });
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold">Agent Activity Map</h2>
        <div className="flex items-center">
          {loading && (
            <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-blue-500 mr-2"></div>
          )}
          <span className="text-sm text-gray-500">
            {lastUpdated ? `Last updated: ${lastUpdated.toLocaleTimeString()}` : 'Updating...'}
          </span>
        </div>
      </div>

      {agentStatus.length === 0 ? (
        <div className="text-center text-gray-500 py-8">No agent data available</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white">
            <thead className="bg-gray-100">
              <tr>
                <th className="py-2 px-4 text-left">Agent</th>
                <th className="py-2 px-4 text-left">Status</th>
                <th className="py-2 px-4 text-left">Uptime</th>
                <th className="py-2 px-4 text-left">Response Rate</th>
                <th className="py-2 px-4 text-left">Error %</th>
                <th className="py-2 px-4 text-left">Last Activity</th>
              </tr>
            </thead>
            <tbody>
              {agentStatus.map((agent, index) => (
                <tr key={agent.id || index} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                  <td className="py-3 px-4">
                    <div className="flex items-center">
                      <div
                        className={`w-3 h-3 rounded-full ${getStatusColor(agent.status)} mr-2`}
                      ></div>
                      <span className="font-medium">{agent.name || agent.id}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                        agent.status === 'online' || agent.status === 'active'
                          ? 'bg-green-100 text-green-800'
                          : agent.status === 'idle'
                            ? 'bg-blue-100 text-blue-800'
                            : agent.status === 'busy'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {agent.status || 'unknown'}
                    </span>
                  </td>
                  <td className="py-3 px-4">{agent.uptime ? `${agent.uptime} hrs` : 'N/A'}</td>
                  <td className="py-3 px-4">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2.5 mr-2">
                        <div
                          className="bg-blue-600 h-2.5 rounded-full"
                          style={{ width: `${agent.response_rate || 0}%` }}
                        ></div>
                      </div>
                      <span>{agent.response_rate || 0}%</span>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className={getErrorClass(agent.error_percentage)}>
                      {agent.error_percentage !== undefined ? `${agent.error_percentage}%` : 'N/A'}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-600">
                    {agent.last_activity ? new Date(agent.last_activity).toLocaleString() : 'Never'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default AgentActivityMap;
