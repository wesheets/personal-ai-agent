import { useState, useEffect } from 'react';
import './SystemPanels.css';

export default function SystemStatusPanel({ projectId }) {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setLoading(true);
        const res = await fetch(`/api/system/status?project_id=${projectId}`);
        if (!res.ok) {
          throw new Error(`Failed to fetch status: ${res.status}`);
        }
        const data = await res.json();
        setStatus(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching system status:', err);
        setError('Failed to load system status');
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
    
    // Set up polling interval
    const intervalId = setInterval(fetchStatus, 10000); // Poll every 10 seconds
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, [projectId]);

  if (loading && !status) {
    return (
      <div className="system-panel">
        <div className="system-panel-header">
          <span className="icon">⚙️</span>
          <h3>System Status</h3>
        </div>
        <div className="animate-pulse system-panel-content">Loading status...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="system-panel">
        <div className="system-panel-header">
          <span className="icon">⚙️</span>
          <h3>System Status</h3>
        </div>
        <div className="system-panel-content status-error">{error}</div>
      </div>
    );
  }

  return (
    <div className="system-panel">
      <div className="system-panel-header">
        <span className="icon">⚙️</span>
        <h3>System Status</h3>
      </div>
      
      {status ? (
        <div className="system-panel-content">
          <div className="system-panel-row">
            <div className="system-panel-label">Status:</div>
            <div className="system-panel-value">
              {status.status === 'in_progress' && (
                <span className="status-in-progress">⚙️ In Progress</span>
              )}
              {status.status === 'completed' && (
                <span className="status-completed">✅ Completed</span>
              )}
              {status.status === 'error' && (
                <span className="status-error">❌ Error</span>
              )}
              {status.status === 'blocked' && (
                <span className="status-blocked">🔒 Blocked</span>
              )}
              {!['in_progress', 'completed', 'error', 'blocked'].includes(status.status) && (
                <span>{status.status}</span>
              )}
            </div>
          </div>
          
          <div className="system-panel-row">
            <div className="system-panel-label">Agents:</div>
            <div className="system-panel-value">
              {status.agents_involved?.join(', ') || 'None'}
            </div>
          </div>
          
          <div className="system-panel-row">
            <div className="system-panel-label">Latest Action:</div>
            <div className="system-panel-value">
              {status.latest_agent_action?.action || 'No recent actions'}
            </div>
          </div>
          
          {status.next_step && (
            <div className="system-panel-row">
              <div className="system-panel-label">Next Step:</div>
              <div className="system-panel-value">{status.next_step}</div>
            </div>
          )}
          
          {status.files_created && status.files_created.length > 0 && (
            <div className="system-panel-row">
              <div className="system-panel-label">Files Created:</div>
              <div className="system-panel-value">{status.files_created.length} files</div>
            </div>
          )}
          
          {status.blocked_due_to && (
            <div className="system-panel-row">
              <div className="system-panel-label">Blocked By:</div>
              <div className="system-panel-value status-blocked">{status.blocked_due_to}</div>
            </div>
          )}
          
          <div className="system-panel-footer">
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      ) : (
        <div className="system-panel-content">No status information available</div>
      )}
    </div>
  );
}
