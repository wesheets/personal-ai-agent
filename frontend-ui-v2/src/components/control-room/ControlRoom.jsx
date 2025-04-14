// ControlRoom.jsx
import React, { useState, useEffect } from 'react';
import AgentStreamPanel from './AgentStreamPanel';
import MemoryLogViewer from './MemoryLogViewer';
import AgentCommandPanel from './AgentCommandPanel';
import AgentCreationPanel from './AgentCreationPanel';
import TrainingDashboardPanel from './TrainingDashboardPanel';
import SystemStatusBar from './SystemStatusBar';

const ControlRoom = () => {
  const [activePanel, setActivePanel] = useState('stream');

  const renderPanel = () => {
    switch (activePanel) {
      case 'stream':
        return <AgentStreamPanel />;
      case 'log':
        return <MemoryLogViewer />;
      case 'command':
        return <AgentCommandPanel />;
      case 'create':
        return <AgentCreationPanel />;
      case 'train-log':
        return <TrainingDashboardPanel />;
      default:
        return <AgentStreamPanel />;
    }
  };

  return (
    <div className="flex h-screen">
      <aside className="w-64 bg-gray-900 text-white p-4 space-y-4">
        <h1 className="text-xl font-bold">🧠 Control Room</h1>
        <nav className="flex flex-col space-y-2">
          <button onClick={() => setActivePanel('stream')} className="text-left hover:text-blue-400">Live Stream</button>
          <button onClick={() => setActivePanel('log')} className="text-left hover:text-blue-400">Memory Logs</button>
          <button onClick={() => setActivePanel('command')} className="text-left hover:text-blue-400">Command Console</button>
          <button onClick={() => setActivePanel('create')} className="text-left hover:text-blue-400">Create Agent</button>
          <button onClick={() => setActivePanel('train-log')} className="text-left hover:text-blue-400">Training Logs</button>
        </nav>
      </aside>
      <main className="flex-1 bg-gray-100 p-6 overflow-auto">
        {renderPanel()}
      </main>
      <SystemStatusBar />
    </div>
  );
};

export default ControlRoom;
