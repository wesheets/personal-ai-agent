import React, { useState, useEffect } from 'react';

/**
 * MemoryBrowser component
 *
 * Displays and paginates through agent memory entries
 */
const MemoryBrowser = () => {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // Fetch memories with pagination
  useEffect(() => {
    const fetchMemories = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(`/api/memory?page=${page}&limit=${pageSize}`);

        if (!response.ok) {
          throw new Error(`Failed to fetch memories: ${response.status}`);
        }

        const data = await response.json();

        // Check if data has the expected structure
        if (Array.isArray(data.memories)) {
          setMemories(data.memories);
          setTotalPages(data.totalPages || Math.ceil(data.total / pageSize) || 1);
        } else if (Array.isArray(data)) {
          // Handle case where API returns array directly
          setMemories(data);
          setTotalPages(Math.ceil(data.length / pageSize) || 1);
        } else {
          throw new Error('Invalid memory data format');
        }
      } catch (error) {
        console.error('Error fetching memories:', error);
        setError(error.message);
        setMemories([]);
      } finally {
        setLoading(false);
      }
    };

    fetchMemories();
  }, [page, pageSize]);

  const handlePrevPage = () => {
    setPage((prev) => Math.max(prev - 1, 1));
  };

  const handleNextPage = () => {
    setPage((prev) => Math.min(prev + 1, totalPages));
  };

  const handlePageSizeChange = (e) => {
    setPageSize(Number(e.target.value));
    setPage(1); // Reset to first page when changing page size
  };

  // Render loading state
  if (loading && memories.length === 0) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-md">
        <div className="flex flex-col items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-600">Loading system memories...</p>
        </div>
      </div>
    );
  }

  // Render error state
  if (error && !loading && memories.length === 0) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-md">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> {error}</span>
        </div>
        <div className="flex justify-center">
          <button
            onClick={() => setPage(1)}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Render empty state
  if (!loading && memories.length === 0) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-md">
        <div className="flex flex-col items-center justify-center h-64">
          <svg
            className="w-16 h-16 text-gray-400 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            ></path>
          </svg>
          <p className="text-gray-600 text-lg font-medium">No memories found</p>
          <p className="text-gray-500 text-sm mt-1">
            Try interacting with agents to generate memory entries
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Memory Browser</h2>
        <div className="flex items-center space-x-2">
          <label htmlFor="pageSize" className="text-sm text-gray-600">
            Items per page:
          </label>
          <select
            id="pageSize"
            value={pageSize}
            onChange={handlePageSizeChange}
            className="border rounded px-2 py-1 text-sm"
          >
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
          </select>
        </div>
      </div>

      {loading && (
        <div className="flex justify-center my-4">
          <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="min-w-full bg-white">
          <thead className="bg-gray-100">
            <tr>
              <th className="py-2 px-4 text-left">Agent</th>
              <th className="py-2 px-4 text-left">Type</th>
              <th className="py-2 px-4 text-left">Content</th>
              <th className="py-2 px-4 text-left">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {memories.map((memory, index) => (
              <tr key={memory.id || index} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                <td className="py-2 px-4 font-medium">
                  {memory.agent_id || memory.agentId || 'Unknown'}
                </td>
                <td className="py-2 px-4">
                  <span
                    className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                      memory.type === 'task'
                        ? 'bg-blue-100 text-blue-800'
                        : memory.type === 'delegation'
                          ? 'bg-purple-100 text-purple-800'
                          : memory.type === 'reflection'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {memory.type || 'memory'}
                  </span>
                </td>
                <td className="py-2 px-4">
                  <div className="max-h-20 overflow-y-auto">
                    <p className="text-sm">{memory.content || memory.text || 'No content'}</p>
                  </div>
                </td>
                <td className="py-2 px-4 text-sm text-gray-600">
                  {memory.timestamp ? new Date(memory.timestamp).toLocaleString() : 'Unknown'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex justify-between items-center mt-4">
        <div className="text-sm text-gray-600">
          Page {page} of {totalPages}
        </div>
        <div className="flex space-x-2">
          <button
            onClick={handlePrevPage}
            disabled={page <= 1}
            className={`px-3 py-1 rounded ${page <= 1 ? 'bg-gray-200 text-gray-500' : 'bg-blue-600 text-white hover:bg-blue-700'}`}
          >
            Previous
          </button>
          <button
            onClick={handleNextPage}
            disabled={page >= totalPages}
            className={`px-3 py-1 rounded ${page >= totalPages ? 'bg-gray-200 text-gray-500' : 'bg-blue-600 text-white hover:bg-blue-700'}`}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
};

export default MemoryBrowser;
