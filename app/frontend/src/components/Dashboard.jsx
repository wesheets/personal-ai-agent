import React, { useState } from 'react';

// Import components (to be created)
import GoalLoopVisualization from './GoalLoopVisualization.jsx';
import MemoryViewer from './MemoryViewer.jsx';
import InterruptControl from './InterruptControl.jsx';
import StatusFeedback from './StatusFeedback.jsx';

const Dashboard = () => {
  return (
    <div className="container">
      <header className="header">
        <h1>Personal AI Agent System</h1>
      </header>
      
      <div className="grid">
        <div className="card">
          <h2>Goal Loop Visualization</h2>
          <GoalLoopVisualization />
        </div>
        
        <div className="card">
          <h2>Memory Viewer</h2>
          <MemoryViewer />
        </div>
      </div>
      
      <div className="grid">
        <div className="card">
          <h2>Interrupt Control</h2>
          <InterruptControl />
        </div>
        
        <div className="card">
          <h2>Status Feedback</h2>
          <StatusFeedback />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
