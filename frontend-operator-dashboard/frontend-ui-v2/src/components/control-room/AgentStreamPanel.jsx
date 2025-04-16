import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AgentStreamPanel = () => {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMemories = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/modules/stream?limit=10');
      if (response.data && response.data.status === 'ok') {
        setMemories(response.data.stream);
      }
      setError(null);
    } catch (err) {
      console.error('Error fetching memory stream:', err);
      setError('Failed to load memory stream. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchMemories();

    // Set up polling every 5 seconds
    const intervalId = setInterval(fetchMemories, 5000);

    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Agent Activity Stream</h2>
        <div className="flex items-center">
          <span
            className={`h-3 w-3 rounded-full mr-2 ${loading ? 'bg-yellow-500' : 'bg-green-500'}`}
          ></span>
          <span className="text-sm text-gray-500">{loading ? 'Updating...' : 'Live'}</span>
        </div>
      </div>

      {error && (
        <div
          className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative"
          role="alert"
        >
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      <div className="space-y-3">
        {memories.length === 0 && !loading ? (
          <div className="bg-white shadow p-4 rounded-xl text-center text-gray-500">
            No recent agent activity found.
          </div>
        ) : (
          memories.map((memory) => (
            <div key={memory.memory_id} className="bg-white shadow p-4 rounded-xl mb-3">
              <div className="flex justify-between items-start mb-2">
                <div className="font-semibold text-blue-600">{memory.agent_id}</div>
                <div className="text-xs text-gray-500">{formatTimestamp(memory.timestamp)}</div>
              </div>
              <div className="mb-2">
                <span className="inline-block bg-gray-200 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 mr-2">
                  {memory.type}
                </span>
                {memory.tags &&
                  memory.tags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-block bg-blue-100 rounded-full px-3 py-1 text-sm font-semibold text-blue-700 mr-2"
                    >
                      {tag}
                    </span>
                  ))}
              </div>
              <p className="text-gray-700 whitespace-pre-wrap">{memory.content}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AgentStreamPanel;
