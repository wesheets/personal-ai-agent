import React, { useState, useEffect } from 'react';
import { memoryService } from '../services/api';

// Component for viewing memory entries with filtering capabilities
const MemoryViewer = () => {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    goalId: '',
    agentType: '',
    startTimestamp: '',
    endTimestamp: ''
  });

  useEffect(() => {
    // Function to fetch memory data from the API
    const fetchMemories = async () => {
      try {
        setLoading(true);
        
        // Build query parameters based on filters
        const params = {};
        if (filters.goalId) params.goal_id = filters.goalId;
        if (filters.agentType) params.agent_type = filters.agentType;
        if (filters.startTimestamp) params.start_timestamp = filters.startTimestamp;
        if (filters.endTimestamp) params.end_timestamp = filters.endTimestamp;
        
        const data = await memoryService.getMemoryEntries(params);
        setMemories(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch memory data');
        setLoading(false);
        console.error('Error fetching memories:', err);
      }
    };

    // Initial fetch
    fetchMemories();
  }, [filters]);

  // Handle filter changes
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Reset all filters
  const resetFilters = () => {
    setFilters({
      goalId: '',
      agentType: '',
      startTimestamp: '',
      endTimestamp: ''
    });
  };

  if (loading) {
    return <div className="loading">Loading memory data...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="memory-viewer">
      {/* Filter controls */}
      <div className="memory-filters">
        <div className="filter-group">
          <label htmlFor="goalId">Goal ID:</label>
          <input
            type="text"
            id="goalId"
            name="goalId"
            value={filters.goalId}
            onChange={handleFilterChange}
            placeholder="Filter by Goal ID"
          />
        </div>
        
        <div className="filter-group">
          <label htmlFor="agentType">Agent Type:</label>
          <select
            id="agentType"
            name="agentType"
            value={filters.agentType}
            onChange={handleFilterChange}
          >
            <option value="">All Agents</option>
            <option value="builder">Builder</option>
            <option value="ops">Ops</option>
            <option value="research">Research</option>
            <option value="memory">Memory</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label htmlFor="startTimestamp">From:</label>
          <input
            type="datetime-local"
            id="startTimestamp"
            name="startTimestamp"
            value={filters.startTimestamp}
            onChange={handleFilterChange}
          />
        </div>
        
        <div className="filter-group">
          <label htmlFor="endTimestamp">To:</label>
          <input
            type="datetime-local"
            id="endTimestamp"
            name="endTimestamp"
            value={filters.endTimestamp}
            onChange={handleFilterChange}
          />
        </div>
        
        <button className="btn btn-secondary" onClick={resetFilters}>
          Reset Filters
        </button>
      </div>
      
      {/* Memory entries display */}
      <div className="memory-entries">
        {memories.length > 0 ? (
          <div className="memory-list">
            {memories.map((memory) => (
              <div key={memory.id} className="memory-item">
                <div className="memory-header">
                  <h4>{memory.title || 'Memory Entry'}</h4>
                  <span className="memory-timestamp">
                    {new Date(memory.timestamp).toLocaleString()}
                  </span>
                </div>
                
                <div className="memory-content">
                  <p>{memory.content}</p>
                </div>
                
                <div className="memory-metadata">
                  <span className="memory-agent">Agent: {memory.agent_type || 'Unknown'}</span>
                  {memory.goal_id && <span className="memory-goal">Goal: {memory.goal_id}</span>}
                  {memory.tags && memory.tags.length > 0 && (
                    <div className="memory-tags">
                      Tags: {memory.tags.join(', ')}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">No memory entries found</div>
        )}
      </div>
    </div>
  );
};

export default MemoryViewer;
