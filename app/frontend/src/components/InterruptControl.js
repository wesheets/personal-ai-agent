import React, { useState, useEffect } from 'react';
import isEqual from 'lodash.isequal';
import { controlService, goalsService } from '../services/api';

// Component for controlling agent execution with interrupt capabilities
const InterruptControl = () => {
  const [systemState, setSystemState] = useState({
    executionMode: 'auto', // 'auto', 'manual', 'paused'
    activeAgents: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [taskPrompt, setTaskPrompt] = useState('');
  const [activeTasks, setActiveTasks] = useState([]);

  useEffect(() => {
    // Function to fetch system state and active tasks
    const fetchSystemState = async () => {
      try {
        setLoading(true);
        
        // Fetch system control mode
        const controlModeData = await controlService.getControlMode();
        
        // Fetch active tasks
        const tasksData = await goalsService.getTaskState();
        
        setSystemState({
          executionMode: controlModeData.mode,
          activeAgents: controlModeData.active_agents || []
        });
        
        setActiveTasks(tasksData.tasks || []);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch system state');
        setLoading(false);
        console.error('Error fetching system state:', err);
      }
    };

    // Initial fetch
    fetchSystemState();
    
    // Set up polling for real-time updates (every 3 seconds)
    const intervalId = setInterval(fetchSystemState, 3000);
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  // Handle system execution mode change
  const handleModeChange = async (mode) => {
    try {
      await controlService.setControlMode(mode);
      setSystemState(prev => ({
        ...prev,
        executionMode: mode
      }));
    } catch (err) {
      setError(`Failed to change execution mode to ${mode}`);
      console.error('Error changing execution mode:', err);
    }
  };

  // Handle task kill/restart
  const handleTaskAction = async (taskId, action) => {
    try {
      if (action === 'kill') {
        await goalsService.killTask(taskId);
      } else if (action === 'restart') {
        await goalsService.restartTask(taskId);
      }
      // State will be updated on next polling cycle
    } catch (err) {
      setError(`Failed to ${action} task ${taskId}`);
      console.error(`Error ${action} task:`, err);
    }
  };

  // Handle task redirection to another agent
  const handleTaskRedirect = async (taskId, targetAgent) => {
    try {
      await controlService.delegateTask(taskId, targetAgent);
      // State will be updated on next polling cycle
    } catch (err) {
      setError(`Failed to redirect task ${taskId} to ${targetAgent}`);
      console.error('Error redirecting task:', err);
    }
  };

  // Handle task prompt editing (Manual Mode only)
  const handlePromptEdit = async () => {
    if (!selectedTask) return;
    
    try {
      await controlService.editTaskPrompt(selectedTask.task_id, taskPrompt);
      
      // Reset form
      setSelectedTask(null);
      setTaskPrompt('');
    } catch (err) {
      setError(`Failed to edit prompt for task ${selectedTask.task_id}`);
      console.error('Error editing task prompt:', err);
    }
  };

  // Open task prompt editor
  const openPromptEditor = (task) => {
    setSelectedTask(task);
    setTaskPrompt(task.prompt || '');
  };

  if (loading) {
    return <div className="loading">Loading control panel...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="interrupt-control">
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
    </div>
  );
};

export default InterruptControl;
