import React, { useState, useEffect } from 'react';
import { controlService } from '../services/api';

// Component for displaying live status feedback for active agents
const StatusFeedback = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Function to fetch agent status data
    const fetchAgentStatus = async () => {
      try {
        setLoading(true);
        
        // Fetch active agents and their status
        const response = await controlService.getAgentStatus();
        setAgents(response.agents || []);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch agent status data');
        setLoading(false);
        console.error('Error fetching agent status:', err);
      }
    };

    // Initial fetch
    fetchAgentStatus();
    
    // Set up polling for real-time updates (every 2 seconds)
    const intervalId = setInterval(fetchAgentStatus, 2000);
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  // Function to determine status color
  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'active':
      case 'running':
      case 'in_progress':
        return 'status-active';
      case 'idle':
      case 'waiting':
      case 'pending':
        return 'status-paused';
      case 'error':
      case 'failed':
        return 'status-error';
      case 'completed':
      case 'success':
        return 'status-completed';
      default:
        return '';
    }
  };

  if (loading) {
    return <div className="loading">Loading agent status...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="status-feedback">
      {agents.length > 0 ? (
        <div className="agent-status-list">
          {agents.map((agent) => (
            <div key={agent.id} className="agent-status-item">
              <div className="agent-header">
                <h4>
                  <span className={`status-indicator ${getStatusColor(agent.status)}`}></span>
                  {agent.name}
                </h4>
                <span className="agent-type">{agent.type}</span>
              </div>
              
              <div className="agent-details">
                <div className="status-row">
                  <span className="status-label">Status:</span>
                  <span className={`status-value ${getStatusColor(agent.status)}`}>{agent.status}</span>
                </div>
                
                {agent.current_task && (
                  <div className="status-row">
                    <span className="status-label">Current Task:</span>
                    <span className="status-value">{agent.current_task.title}</span>
                  </div>
                )}
                
                {agent.completion_state && (
                  <div className="status-row">
                    <span className="status-label">Completion:</span>
                    <span className="status-value">{agent.completion_state}</span>
                  </div>
                )}
                
                {agent.errors && agent.errors.length > 0 && (
                  <div className="status-row">
                    <span className="status-label">Errors:</span>
                    <span className="status-value error-count">{agent.errors.length}</span>
                  </div>
                )}
                
                {agent.retry_count > 0 && (
                  <div className="status-row">
                    <span className="status-label">Retries:</span>
                    <span className="status-value">{agent.retry_count}</span>
                  </div>
                )}
              </div>
              
              {/* Error details (expandable) */}
              {agent.errors && agent.errors.length > 0 && (
                <div className="error-details">
                  <details>
                    <summary>Error Details</summary>
                    <ul className="error-list">
                      {agent.errors.map((error, index) => (
                        <li key={index} className="error-item">
                          <span className="error-time">{new Date(error.timestamp).toLocaleString()}</span>
                          <span className="error-message">{error.message}</span>
                        </li>
                      ))}
                    </ul>
                  </details>
                </div>
              )}
              
              {/* Performance metrics */}
              {agent.metrics && (
                <div className="agent-metrics">
                  <details>
                    <summary>Performance Metrics</summary>
                    <div className="metrics-grid">
                      <div className="metric-item">
                        <span className="metric-label">Tasks Completed:</span>
                        <span className="metric-value">{agent.metrics.tasks_completed || 0}</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Avg. Response Time:</span>
                        <span className="metric-value">{agent.metrics.avg_response_time || 'N/A'}</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Success Rate:</span>
                        <span className="metric-value">{agent.metrics.success_rate || 'N/A'}</span>
                      </div>
                    </div>
                  </details>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">No active agents found</div>
      )}
    </div>
  );
};

export default StatusFeedback;
