import React, { useState, useEffect } from 'react';

/**
 * GPTUsageDebugPanel component
 * 
 * Displays GPT usage statistics including token use, agent ID, latency, and failures
 */
const GPTUsageDebugPanel = () => {
  const [usageData, setUsageData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  
  // Fetch GPT usage data
  useEffect(() => {
    const fetchUsageData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await fetch('/api/debug/gpt-usage');
        
        if (!response.ok) {
          throw new Error(`Failed to fetch GPT usage data: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (Array.isArray(data)) {
          setUsageData(data);
        } else if (data.usage && Array.isArray(data.usage)) {
          setUsageData(data.usage);
        } else {
          throw new Error('Invalid GPT usage data format');
        }
      } catch (error) {
        console.error('Error fetching GPT usage data:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchUsageData();
    
    // Set up polling interval (every 30 seconds)
    const intervalId = setInterval(fetchUsageData, 30000);
    
    // Cleanup
    return () => clearInterval(intervalId);
  }, []);
  
  // Filter usage data
  const filteredData = usageData.filter(item => {
    if (filter === 'all') return true;
    if (filter === 'failures') return item.status === 'failed' || item.error;
    if (filter === 'high-latency') return item.latency > 2000; // Over 2 seconds
    if (filter === 'high-tokens') return item.total_tokens > 1000;
    return true;
  });
  
  // Calculate summary statistics
  const calculateStats = () => {
    if (usageData.length === 0) return null;
    
    const totalRequests = usageData.length;
    const failedRequests = usageData.filter(item => item.status === 'failed' || item.error).length;
    const totalTokens = usageData.reduce((sum, item) => sum + (item.total_tokens || 0), 0);
    const avgTokens = Math.round(totalTokens / totalRequests);
    const avgLatency = Math.round(
      usageData.reduce((sum, item) => sum + (item.latency || 0), 0) / totalRequests
    );
    
    return {
      totalRequests,
      failedRequests,
      failureRate: Math.round((failedRequests / totalRequests) * 100),
      totalTokens,
      avgTokens,
      avgLatency
    };
  };
  
  const stats = calculateStats();
  
  // Render loading state
  if (loading && usageData.length === 0) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-md">
        <div className="flex flex-col items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-600">Loading GPT usage data...</p>
        </div>
      </div>
    );
  }
  
  // Render error state
  if (error && !loading && usageData.length === 0) {
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
              fetch('/api/debug/gpt-usage')
                .then(res => res.json())
                .then(data => {
                  if (Array.isArray(data)) {
                    setUsageData(data);
                  } else if (data.usage && Array.isArray(data.usage)) {
                    setUsageData(data.usage);
                  } else {
                    throw new Error('Invalid GPT usage data format');
                  }
                  setLoading(false);
                })
                .catch(err => {
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
      <h2 className="text-xl font-semibold mb-4">GPT Usage Debug</h2>
      
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
          <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
            <p className="text-sm text-gray-600">Total Requests</p>
            <p className="text-2xl font-bold">{stats.totalRequests}</p>
          </div>
          <div className="bg-red-50 p-3 rounded-lg border border-red-200">
            <p className="text-sm text-gray-600">Failed Requests</p>
            <p className="text-2xl font-bold text-red-700">{stats.failedRequests}</p>
          </div>
          <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-200">
            <p className="text-sm text-gray-600">Failure Rate</p>
            <p className="text-2xl font-bold">{stats.failureRate}%</p>
          </div>
          <div className="bg-green-50 p-3 rounded-lg border border-green-200">
            <p className="text-sm text-gray-600">Total Tokens</p>
            <p className="text-2xl font-bold">{stats.totalTokens.toLocaleString()}</p>
          </div>
          <div className="bg-purple-50 p-3 rounded-lg border border-purple-200">
            <p className="text-sm text-gray-600">Avg Tokens</p>
            <p className="text-2xl font-bold">{stats.avgTokens}</p>
          </div>
          <div className="bg-indigo-50 p-3 rounded-lg border border-indigo-200">
            <p className="text-sm text-gray-600">Avg Latency</p>
            <p className="text-2xl font-bold">{stats.avgLatency} ms</p>
          </div>
        </div>
      )}
      
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center">
          <label htmlFor="filter" className="mr-2 text-sm text-gray-600">Filter:</label>
          <select
            id="filter"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="border rounded px-2 py-1 text-sm"
          >
            <option value="all">All Requests</option>
            <option value="failures">Failures Only</option>
            <option value="high-latency">High Latency (>2s)</option>
            <option value="high-tokens">High Token Usage (>1000)</option>
          </select>
        </div>
        
        {loading && (
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-blue-500 mr-2"></div>
            <span className="text-sm text-gray-500">Updating...</span>
          </div>
        )}
      </div>
      
      {filteredData.length === 0 ? (
        <div className="text-center text-gray-500 py-8">No GPT usage data available</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white">
            <thead className="bg-gray-100">
              <tr>
                <th className="py-2 px-4 text-left">Timestamp</th>
                <th className="py-2 px-4 text-left">Agent ID</th>
                <th className="py-2 px-4 text-left">Status</th>
                <th className="py-2 px-4 text-left">Tokens</th>
                <th className="py-2 px-4 text-left">Latency</th>
                <th className="py-2 px-4 text-left">Details</th>
              </tr>
            </thead>
            <tbody>
              {filteredData.map((item, index) => (
                <tr key={item.id || index} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                  <td className="py-2 px-4 text-sm">
                    {item.timestamp ? new Date(item.timestamp).toLocaleString() : 'Unknown'}
                  </td>
                  <td className="py-2 px-4 font-medium">{item.agent_id || 'Unknown'}</td>
                  <td className="py-2 px-4">
                    <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                      item.status === 'success' ? 'bg-green-100 text-green-800' :
                      item.status === 'failed' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {item.status || 'unknown'}
                    </span>
                  </td>
                  <td className="py-2 px-4">
                    <div className="flex flex-col">
                      <span>{item.total_tokens || 0} total</span>
                      <span className="text-xs text-gray-500">
                        {item.prompt_tokens || 0} prompt / {item.completion_tokens || 0} completion
                      </span>
                    </div>
                  </td>
                  <td className="py-2 px-4">
                    <span className={
                      (item.latency || 0) > 3000 ? 'text-red-600' : 
                      (item.latency || 0) > 1000 ? 'text-yellow-600' : 
                      'text-green-600'
                    }>
                      {item.latency || 0} ms
                    </span>
                  </td>
                  <td className="py-2 px-4 text-sm">
                    {item.error ? (
                      <span className="text-red-600">{item.error}</span>
                    ) : (
                      <span className="text-gray-600">{item.model || 'No details'}</span>
                    )}
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

export default GPTUsageDebugPanel;
