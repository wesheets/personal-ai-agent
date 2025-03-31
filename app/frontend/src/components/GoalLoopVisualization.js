import React, { useState, useEffect } from 'react';
import { goalsService } from '../services/api';

// Component for visualizing the goal loop with subtasks and agent assignments
const GoalLoopVisualization = () => {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Function to fetch goals data from the API
    const fetchGoals = async () => {
      try {
        setLoading(true);
        const data = await goalsService.getGoals();
        setGoals(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch goals data');
        setLoading(false);
        console.error('Error fetching goals:', err);
      }
    };

    // Initial fetch
    fetchGoals();

    // Set up polling for real-time updates (every 5 seconds)
    const intervalId = setInterval(fetchGoals, 5000);

    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  // Function to determine status color
  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'status-completed';
      case 'in_progress':
        return 'status-active';
      case 'failed':
        return 'status-error';
      case 'pending':
        return 'status-paused';
      default:
        return '';
    }
  };

  if (loading) {
    return <div className="loading">Loading goal data...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (goals.length === 0) {
    return <div className="empty-state">No active goals found</div>;
  }

  return (
    <div className="goal-visualization">
      {goals.map((goal) => (
        <div key={goal.goal_id} className="goal-container">
          <div className="goal-header">
            <h3>
              <span className={`status-indicator ${getStatusColor(goal.status)}`}></span>
              {goal.title}
            </h3>
            <div className="goal-meta">
              <span>Created: {new Date(goal.created_at).toLocaleString()}</span>
              <span>Status: {goal.status}</span>
            </div>
          </div>
          
          <div className="goal-description">{goal.description}</div>
          
          {/* Subtasks visualization */}
          <div className="subtasks">
            <h4>Subtasks</h4>
            {goal.tasks && goal.tasks.length > 0 ? (
              <div className="subtask-tree">
                {goal.tasks.map((task) => (
                  <div key={task.task_id} className="subtask-item">
                    <div className="subtask-header">
                      <span className={`status-indicator ${getStatusColor(task.status)}`}></span>
                      <span className="subtask-title">{task.title}</span>
                      <span className="subtask-agent">Agent: {task.assigned_agent || 'Unassigned'}</span>
                    </div>
                    <div className="subtask-details">
                      <div className="subtask-description">{task.description}</div>
                      <div className="subtask-meta">
                        <span>Status: {task.status}</span>
                        {task.started_at && <span>Started: {new Date(task.started_at).toLocaleString()}</span>}
                        {task.completed_at && <span>Completed: {new Date(task.completed_at).toLocaleString()}</span>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">No subtasks found</div>
            )}
          </div>
          
          {/* Timeline visualization */}
          <div className="timeline">
            <h4>Timeline</h4>
            <div className="timeline-container">
              {goal.tasks && goal.tasks
                .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
                .map((task, index) => (
                  <div key={`timeline-${task.task_id}`} className="timeline-item">
                    <div className={`timeline-marker ${getStatusColor(task.status)}`}></div>
                    <div className="timeline-content">
                      <h5>{task.title}</h5>
                      <div className="timeline-meta">
                        <span>{task.status}</span>
                        <span>{new Date(task.created_at).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default GoalLoopVisualization;
