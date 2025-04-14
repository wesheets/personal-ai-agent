import React, { useState, useEffect } from 'react';

/**
 * DashboardView component
 * 
 * Displays system metrics with loading states and throttled API calls
 */
const DashboardView = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  
  // Fetch system metrics with throttling
  useEffect(() => {
    let isMounted = true;
    let timeoutId = null;
    
    const fetchMetrics = async () => {
      if (!isMounted) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const response = await fetch('/api/system/metrics');
        
        if (!response.ok) {
          throw new Error(`Failed to fetch metrics: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (isMounted) {
          setMetrics(data);
          setLastUpdated(new Date());
          setLoading(false);
        }
      } catch (error) {
        console.error('Error fetching metrics:', error);
        if (isMounted) {
          setError(error.message);
          setLoading(false);
        }
      }
    };
    
    // Initial fetch
    fetchMetrics();
    
    // Set up polling with throttling (every 30 seconds)
    const setupNextFetch = () => {
      if (isMounted) {
        timeoutId = setTimeout(async () => {
          await fetchMetrics();
          setupNextFetch();
        }, 30000); // 30 seconds throttle
      }
    };
    
    setupNextFetch();
    
    // Cleanup
    return () => {
      isMounted = false;
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, []);
  
  // Render loading state
  if (loading && !metrics) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-md">
        <div className="flex flex-col items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-600">Loading system metrics...</p>
        </div>
      </div>
    );
  }
  
  // Render error state
  if (error && !loading && !metrics) {
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
              fetch('/api/system/metrics')
                .then(res => res.json())
                .then(data => {
                  setMetrics(data);
                  setLastUpdated(new Date());
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
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold">System Metrics</h2>
        <div className="flex items-center">
          {loading && (
            <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-blue-500 mr-2"></div>
          )}
          <span className="text-sm text-gray-500">
            {lastUpdated ? `Last updated: ${lastUpdated.toLocaleTimeString()}` : 'Updating...'}
          </span>
        </div>
      </div>
      
      {metrics ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* System Health */}
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
            <h3 className="text-lg font-medium text-blue-800 mb-2">System Health</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Status</span>
                <span className={`font-medium ${metrics.status === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
                  {metrics.status || 'Unknown'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Uptime</span>
                <span className="font-medium">{metrics.uptime || '0'} hours</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">CPU Usage</span>
                <span className="font-medium">{metrics.cpu_usage || '0'}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Memory Usage</span>
                <span className="font-medium">{metrics.memory_usage || '0'}%</span>
              </div>
            </div>
          </div>
          
          {/* Agent Statistics */}
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200">
            <h3 className="text-lg font-medium text-purple-800 mb-2">Agent Statistics</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Agents</span>
                <span className="font-medium">{metrics.total_agents || '0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Active Agents</span>
                <span className="font-medium">{metrics.active_agents || '0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Response Rate</span>
                <span className="font-medium">{metrics.response_rate || '0'}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Error Rate</span>
                <span className={`font-medium ${(metrics.error_rate || 0) > 5 ? 'text-red-600' : 'text-green-600'}`}>
                  {metrics.error_rate || '0'}%
                </span>
              </div>
            </div>
          </div>
          
          {/* Memory Usage */}
          <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
            <h3 className="text-lg font-medium text-green-800 mb-2">Memory Usage</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Entries</span>
                <span className="font-medium">{metrics.memory_entries || '0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Storage Used</span>
                <span className="font-medium">{metrics.memory_storage || '0'} MB</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Retrieval Rate</span>
                <span className="font-medium">{metrics.memory_retrieval_rate || '0'}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Cache Hit Rate</span>
                <span className="font-medium">{metrics.memory_cache_hit_rate || '0'}%</span>
              </div>
            </div>
          </div>
          
          {/* API Performance */}
          <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 p-4 rounded-lg border border-yellow-200">
            <h3 className="text-lg font-medium text-yellow-800 mb-2">API Performance</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Avg Response Time</span>
                <span className="font-medium">{metrics.avg_response_time || '0'} ms</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Requests/min</span>
                <span className="font-medium">{metrics.requests_per_minute || '0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Success Rate</span>
                <span className={`font-medium ${(metrics.api_success_rate || 0) < 95 ? 'text-red-600' : 'text-green-600'}`}>
                  {metrics.api_success_rate || '0'}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">5xx Errors</span>
                <span className={`font-medium ${(metrics.server_errors || 0) > 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {metrics.server_errors || '0'}
                </span>
              </div>
            </div>
          </div>
          
          {/* GPT Usage */}
          <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-lg border border-red-200">
            <h3 className="text-lg font-medium text-red-800 mb-2">GPT Usage</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Tokens</span>
                <span className="font-medium">{metrics.total_tokens || '0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Avg Tokens/Request</span>
                <span className="font-medium">{metrics.avg_tokens_per_request || '0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Completion Rate</span>
                <span className="font-medium">{metrics.completion_rate || '0'}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Latency</span>
                <span className="font-medium">{metrics.gpt_latency || '0'} ms</span>
              </div>
            </div>
          </div>
          
          {/* System Alerts */}
          <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-4 rounded-lg border border-gray-200">
            <h3 className="text-lg font-medium text-gray-800 mb-2">System Alerts</h3>
            {metrics.alerts && metrics.alerts.length > 0 ? (
              <ul className="space-y-2">
                {metrics.alerts.map((alert, index) => (
                  <li key={index} className={`text-sm p-2 rounded ${
                    alert.severity === 'high' ? 'bg-red-100 text-red-800' :
                    alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {alert.message}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-green-600 font-medium">No active alerts</p>
            )}
          </div>
        </div>
      ) : (
        <div className="text-center text-gray-500">No metrics data available</div>
      )}
    </div>
  );
};

export default DashboardView;
