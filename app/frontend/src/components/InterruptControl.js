import React, { useState, useEffect, useRef } from 'react';
import { controlService, goalsService } from '../services/api';

// Component for controlling agent execution with interrupt capabilities
const InterruptControl = () => {
  const [systemState, setSystemState] = useState({
    executionMode: 'auto', // 'auto', 'manual', 'paused'
    activeAgents: []
  });
  const [loading, setLoading] = useState(false); // Changed to false to avoid initial loading state
  const [error, setError] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [taskPrompt, setTaskPrompt] = useState('');
  const [activeTasks, setActiveTasks] = useState([]);
  const [debugVisible, setDebugVisible] = useState(true);
  const mountedRef = useRef(true);

  useEffect(() => {
    // Set up mounted ref for cleanup
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    // TEMPORARILY DISABLED: Function to fetch system state and active tasks
    const fetchSystemState = async () => {
      console.log("🔥 fetchSystemState is temporarily disabled to prevent spinner freeze");
      
      // Use mock data instead of real API calls
      try {
        // Set mock data for control mode
        const mockControlData = { 
          mode: 'auto', 
          active_agents: ['builder', 'research', 'ops'] 
        };
        
        // Set mock data for tasks
        const mockTasksData = { 
          tasks: [
            {
              task_id: 'mock-task-1',
              title: 'Mock Task 1',
              status: 'in_progress',
              assigned_agent: 'builder'
            }
          ] 
        };
        
        // Update state with mock data
        if (mountedRef.current) {
          setSystemState({
            executionMode: mockControlData.mode,
            activeAgents: mockControlData.active_agents || []
          });
          
          setActiveTasks(mockTasksData.tasks || []);
          setLoading(false);
        }
      } catch (err) {
        console.error('Error in mock data setup:', err);
        if (mountedRef.current) {
          setError('System control temporarily offline');
          setLoading(false);
        }
      }
    };

    // Initial fetch
    fetchSystemState();
    
    // Disable polling to prevent repeated errors
    // const intervalId = setInterval(fetchSystemState, 3000);
    // return () => clearInterval(intervalId);
  }, []);

  // Handle system execution mode change
  const handleModeChange = async (mode) => {
    try {
      // TEMPORARILY DISABLED: await controlService.setControlMode(mode);
      console.log("🔥 setControlMode is temporarily disabled");
      
      if (mountedRef.current) {
        setSystemState(prev => ({
          ...prev,
          executionMode: mode
        }));
      }
    } catch (err) {
      console.error('Error changing execution mode:', err);
      if (mountedRef.current) {
        setError(`Failed to change execution mode to ${mode}`);
      }
    }
  };

  // Handle task kill/restart
  const handleTaskAction = async (taskId, action) => {
    try {
      // TEMPORARILY DISABLED: Real API calls
      console.log(`🔥 ${action} task is temporarily disabled`);
      /*
      if (action === 'kill') {
        await goalsService.killTask(taskId);
      } else if (action === 'restart') {
        await goalsService.restartTask(taskId);
      }
      */
      // State will be updated on next polling cycle
    } catch (err) {
      console.error(`Error ${action} task:`, err);
      if (mountedRef.current) {
        setError(`Failed to ${action} task ${taskId}`);
      }
    }
  };

  // Handle task redirection to another agent
  const handleTaskRedirect = async (taskId, targetAgent) => {
    try {
      // TEMPORARILY DISABLED: await controlService.delegateTask(taskId, targetAgent);
      console.log("🔥 delegateTask is temporarily disabled");
      // State will be updated on next polling cycle
    } catch (err) {
      console.error('Error redirecting task:', err);
      if (mountedRef.current) {
        setError(`Failed to redirect task ${taskId} to ${targetAgent}`);
      }
    }
  };

  // Handle task prompt editing (Manual Mode only)
  const handlePromptEdit = async () => {
    if (!selectedTask) return;
    
    try {
      // TEMPORARILY DISABLED: await controlService.editTaskPrompt(selectedTask.task_id, taskPrompt);
      console.log("🔥 editTaskPrompt is temporarily disabled");
      
      // Reset form
      if (mountedRef.current) {
        setSelectedTask(null);
        setTaskPrompt('');
      }
    } catch (err) {
      console.error('Error editing task prompt:', err);
      if (mountedRef.current) {
        setError(`Failed to edit prompt for task ${selectedTask.task_id}`);
      }
    }
  };

  // Open task prompt editor
  const openPromptEditor = (task) => {
    if (mountedRef.current) {
      setSelectedTask(task);
      setTaskPrompt(task.prompt || '');
    }
  };

  // Render error fallback if component fails
  if (error) {
    return (
      <div className="error-fallback">
        <h3>⚠️ System control temporarily offline</h3>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  // Conditionally render based on loading state
  return (
    <div className="interrupt-control">
      {loading ? (
        <div className="loading">Loading control panel...</div>
      ) : (
        <>
          {/* System execution mode controls */}
          <div className="control-panel">
            <h3>Execution Control</h3>
            <div className="control-buttons">
              <button 
                className={`btn ${systemState.executionMode === 'auto' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => handleModeChange('auto')}
              >
                <i className="fas fa-play"></i> Auto Mode
              </button>
              
              <button 
                className={`btn ${systemState.executionMode === 'manual' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => handleModeChange('manual')}
              >
                <i className="fas fa-user"></i> Manual Mode
              </button>
              
              <button 
                className={`btn ${systemState.executionMode === 'paused' ? 'btn-warning' : 'btn-secondary'}`}
                onClick={() => handleModeChange('paused')}
              >
                <i className="fas fa-pause"></i> Pause All
              </button>
            </div>
          </div>
          
          {/* Active tasks control */}
          <div className="tasks-control">
            <h3>Active Tasks</h3>
            {activeTasks.length > 0 ? (
              <div className="task-list">
                {activeTasks.map((task) => (
                  <div key={task.task_id} className="task-control-item">
                    <div className="task-info">
                      <h4>{task.title}</h4>
                      <div className="task-meta">
                        <span>Status: {task.status}</span>
                        <span>Agent: {task.assigned_agent || 'Unassigned'}</span>
                      </div>
                    </div>
                    
                    <div className="task-actions">
                      {/* Kill/restart task */}
                      <button 
                        className="btn btn-warning"
                        onClick={() => handleTaskAction(task.task_id, task.status === 'in_progress' ? 'kill' : 'restart')}
                        disabled={task.status === 'completed'}
                      >
                        <i className={`fas ${task.status === 'in_progress' ? 'fa-stop' : 'fa-redo'}`}></i>
                        {task.status === 'in_progress' ? ' Kill' : ' Restart'}
                      </button>
                      
                      {/* Redirect task */}
                      <div className="redirect-control">
                        <select 
                          onChange={(e) => handleTaskRedirect(task.task_id, e.target.value)}
                          disabled={task.status === 'completed'}
                        >
                          <option value="">Redirect to...</option>
                          {systemState.activeAgents.map((agent) => (
                            <option key={agent} value={agent}>{agent}</option>
                          ))}
                        </select>
                      </div>
                      
                      {/* Edit prompt (Manual Mode only) */}
                      {systemState.executionMode === 'manual' && (
                        <button 
                          className="btn btn-secondary"
                          onClick={() => openPromptEditor(task)}
                          disabled={task.status === 'completed'}
                        >
                          <i className="fas fa-edit"></i> Edit Prompt
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">No active tasks found</div>
            )}
          </div>
          
          {/* Prompt editor modal (Manual Mode only) */}
          {selectedTask && (
            <div className="prompt-editor-modal">
              <div className="modal-content">
                <div className="modal-header">
                  <h3>Edit Task Prompt</h3>
                  <button className="close-btn" onClick={() => setSelectedTask(null)}>×</button>
                </div>
                
                <div className="modal-body">
                  <div className="task-info">
                    <p><strong>Task:</strong> {selectedTask.title}</p>
                    <p><strong>ID:</strong> {selectedTask.task_id}</p>
                  </div>
                  
                  <div className="prompt-form">
                    <label htmlFor="taskPrompt">Task Prompt:</label>
                    <textarea
                      id="taskPrompt"
                      value={taskPrompt}
                      onChange={(e) => setTaskPrompt(e.target.value)}
                      rows={10}
                    />
                  </div>
                </div>
                
                <div className="modal-footer">
                  <button className="btn btn-secondary" onClick={() => setSelectedTask(null)}>Cancel</button>
                  <button className="btn btn-primary" onClick={handlePromptEdit}>Save Changes</button>
                </div>
              </div>
            </div>
          )}
          
          {/* Debug info */}
          {debugVisible && (
            <div className="debug-info" style={{marginTop: '20px', padding: '10px', border: '1px solid #ccc', borderRadius: '4px'}}>
              <h4>Debug Info</h4>
              <p>InterruptControl.js - fetchSystemState disabled</p>
              <p>Using mock data for system state and tasks</p>
              <p>Last updated: {new Date().toLocaleTimeString()}</p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default InterruptControl;
