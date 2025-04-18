import { useState, useEffect } from 'react';
import './SystemPanels.css';

export default function AgentOutputPanel({ projectId }) {
  const [output, setOutput] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOutput = async () => {
      try {
        setLoading(true);
        const res = await fetch(`/api/project/output?project_id=${projectId}`);
        if (!res.ok) {
          throw new Error(`Failed to fetch output: ${res.status}`);
        }
        const data = await res.json();
        setOutput(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching agent output:', err);
        setError('Failed to load agent output');
      } finally {
        setLoading(false);
      }
    };

    fetchOutput();
    
    // Set up polling interval
    const intervalId = setInterval(fetchOutput, 10000); // Poll every 10 seconds
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, [projectId]);

  if (loading && !output) {
    return (
      <div className="system-panel">
        <div className="system-panel-header">
          <span className="icon">📁</span>
          <h3>Agent Output</h3>
        </div>
        <div className="animate-pulse system-panel-content">Loading agent output...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="system-panel">
        <div className="system-panel-header">
          <span className="icon">📁</span>
          <h3>Agent Output</h3>
        </div>
        <div className="system-panel-content status-error">{error}</div>
      </div>
    );
  }

  return (
    <div className="system-panel">
      <div className="system-panel-header">
        <span className="icon">📁</span>
        <h3>Agent Output</h3>
      </div>
      
      {output ? (
        <div className="system-panel-content">
          <div className="system-panel-row">
            <div className="system-panel-label">Status:</div>
            <div className="system-panel-value">
              {output.status === 'success' && (
                <span className="status-completed">✅ Success</span>
              )}
              {output.status === 'in_progress' && (
                <span className="status-in-progress">⚙️ In Progress</span>
              )}
              {output.status === 'error' && (
                <span className="status-error">❌ Error</span>
              )}
              {!['success', 'in_progress', 'error'].includes(output.status) && (
                <span>{output.status}</span>
              )}
            </div>
          </div>
          
          <div className="system-panel-row">
            <div className="system-panel-label">Last Agent:</div>
            <div className="system-panel-value">
              {output.last_agent || 'None'}
            </div>
          </div>
          
          <div className="system-panel-row">
            <div className="system-panel-label">Task:</div>
            <div className="system-panel-value">
              {output.task || 'No task information'}
            </div>
          </div>
          
          {output.summary && (
            <div className="system-panel-row">
              <div className="system-panel-label">Summary:</div>
              <div className="system-panel-value">{output.summary}</div>
            </div>
          )}
          
          {output.files_created && output.files_created.length > 0 && (
            <div className="system-panel-row">
              <div className="system-panel-label">Files Created:</div>
              <div className="system-panel-value">
                <ul className="files-list">
                  {output.files_created.map((file, index) => (
                    <li key={index} className="file-item">
                      {file}
                      {/* Optional file preview button */}
                      <button 
                        className="file-preview-button"
                        onClick={() => alert(`Preview functionality for ${file} would open here`)}
                      >
                        👁️
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
          
          <div className="system-panel-footer">
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      ) : (
        <div className="system-panel-content">No agent output information available</div>
      )}
    </div>
  );
}
