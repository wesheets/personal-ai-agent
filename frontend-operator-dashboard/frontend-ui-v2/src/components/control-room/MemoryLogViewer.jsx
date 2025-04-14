import React, { useState } from 'react';
import axios from 'axios';

const MemoryLogViewer = () => {
  const [agent_id, setAgentId] = useState('');
  const [type, setType] = useState('');
  const [tag, setTag] = useState('');
  const [limit, setLimit] = useState(10);
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchMemories = async (e) => {
    e.preventDefault();
    if (!agent_id) {
      setError('Agent ID is required');
      return;
    }

    try {
      setLoading(true);
      let url = `/api/modules/memory/read?agent_id=${agent_id}`;
      
      if (type) url += `&type=${type}`;
      if (tag) url += `&tag=${tag}`;
      if (limit) url += `&limit=${limit}`;
      
      const response = await axios.get(url);
      
      if (response.data && response.data.status === 'ok') {
        setMemories(response.data.memories);
        setError(null);
      }
    } catch (err) {
      console.error('Error fetching memories:', err);
      setError('Failed to load memories. Please try again later.');
      setMemories([]);
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold mb-4">Memory Log Viewer</h2>
      
      <form onSubmit={fetchMemories} className="bg-white shadow rounded-xl p-4 mb-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label htmlFor="agent_id" className="block text-sm font-medium text-gray-700 mb-1">
              Agent ID *
            </label>
            <input
              type="text"
              id="agent_id"
              value={agent_id}
              onChange={(e) => setAgentId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., hal"
              required
            />
          </div>
          
          <div>
            <label htmlFor="type" className="block text-sm font-medium text-gray-700 mb-1">
              Memory Type
            </label>
            <input
              type="text"
              id="type"
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., reflection"
            />
          </div>
          
          <div>
            <label htmlFor="tag" className="block text-sm font-medium text-gray-700 mb-1">
              Tag
            </label>
            <input
              type="text"
              id="tag"
              value={tag}
              onChange={(e) => setTag(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., error"
            />
          </div>
          
          <div>
            <label htmlFor="limit" className="block text-sm font-medium text-gray-700 mb-1">
              Limit
            </label>
            <input
              type="number"
              id="limit"
              value={limit}
              onChange={(e) => setLimit(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              min="1"
              max="100"
            />
          </div>
        </div>
        
        <div className="flex justify-end">
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Search Memories'}
          </button>
        </div>
      </form>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <span className="block sm:inline">{error}</span>
        </div>
      )}
      
      <div className="bg-white shadow rounded-xl p-4 max-h-96 overflow-y-auto">
        <h3 className="text-lg font-semibold mb-2">Results ({memories.length})</h3>
        
        {memories.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No memories found. Try adjusting your search criteria.</p>
        ) : (
          <div className="space-y-3">
            {memories.map((memory) => (
              <div key={memory.memory_id} className="bg-gray-50 p-4 rounded-lg mb-3 border border-gray-200">
                <div className="flex justify-between items-start mb-2">
                  <div className="font-semibold text-blue-600">{memory.agent_id}</div>
                  <div className="text-xs text-gray-500">{formatTimestamp(memory.timestamp)}</div>
                </div>
                <div className="mb-2">
                  <span className="inline-block bg-gray-200 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 mr-2">
                    {memory.type}
                  </span>
                  {memory.tags && memory.tags.map((tag) => (
                    <span key={tag} className="inline-block bg-blue-100 rounded-full px-3 py-1 text-sm font-semibold text-blue-700 mr-2">
                      {tag}
                    </span>
                  ))}
                </div>
                <p className="text-gray-700 whitespace-pre-wrap">{memory.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MemoryLogViewer;
