import React, { useState, useEffect } from 'react';

/**
 * AgentManifestViewer component
 *
 * Displays agent manifest data from the system for live verification of available agent IDs
 */
const AgentManifestViewer = () => {
  const [manifest, setManifest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch agent manifest data
  useEffect(() => {
    const fetchManifest = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch('/api/system/agents/manifest');

        if (!response.ok) {
          throw new Error(`Failed to fetch agent manifest: ${response.status}`);
        }

        const data = await response.json();
        setManifest(data);
      } catch (error) {
        console.error('Error fetching agent manifest:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchManifest();
  }, []);

  // Render loading state
  if (loading) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-md">
        <div className="flex flex-col items-center justify-center h-48">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-600">Loading agent manifest...</p>
        </div>
      </div>
    );
  }

  // Render error state
  if (error) {
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
              fetch('/api/system/agents/manifest')
                .then((res) => res.json())
                .then((data) => {
                  setManifest(data);
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

  // Extract agents from manifest
  const agents = manifest?.agents || [];

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Agent Manifest</h2>

      {agents.length === 0 ? (
        <div className="text-center text-gray-500 py-8">No agents found in manifest</div>
      ) : (
        <>
          <p className="text-sm text-gray-600 mb-4">
            Found {agents.length} agents in the system manifest. Use these IDs for agent
            verification and routing.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agents.map((agent, index) => (
              <div key={agent.id || index} className="border rounded-lg p-4 bg-gray-50">
                <div className="flex items-center mb-2">
                  <div
                    className={`w-3 h-3 rounded-full ${agent.active ? 'bg-green-500' : 'bg-gray-400'} mr-2`}
                  ></div>
                  <h3 className="font-medium">{agent.name || 'Unnamed Agent'}</h3>
                </div>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">ID:</span>
                    <code className="bg-gray-200 px-2 py-0.5 rounded">{agent.id}</code>
                  </div>
                  {agent.type && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Type:</span>
                      <span>{agent.type}</span>
                    </div>
                  )}
                  {agent.version && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Version:</span>
                      <span>{agent.version}</span>
                    </div>
                  )}
                  {agent.aliases && agent.aliases.length > 0 && (
                    <div className="mt-2">
                      <span className="text-gray-600">Aliases:</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {agent.aliases.map((alias, i) => (
                          <span
                            key={i}
                            className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded"
                          >
                            {alias}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default AgentManifestViewer;
