import { useState } from 'react';

function Sidebar({ activeTab, onTabChange }) {
  const tabs = [
    { id: 'loops', label: 'Loops', icon: '🔄' },
    { id: 'files', label: 'Files', icon: '📁' },
    { id: 'health', label: 'System Health', icon: '❤️' },
    { id: 'tools', label: 'Tools', icon: '🔧' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
    { id: 'projects', label: 'Projects', icon: '📊' },
  ];
  
  return (
    <div className="h-full bg-gray-900 border-r border-gray-800 w-full">
      <div className="p-4 border-b border-gray-800">
        <h1 className="text-xl font-bold text-accent">Promethios</h1>
      </div>
      <nav className="p-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`w-full text-left mb-1 p-2 rounded flex items-center ${
              activeTab === tab.id 
                ? 'bg-gray-800 text-cyan-400' 
                : 'text-gray-400 hover:text-gray-200'
            }`}
            onClick={() => onTabChange(tab.id)}
          >
            <span className="text-lg mr-2">{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}

export default Sidebar;
