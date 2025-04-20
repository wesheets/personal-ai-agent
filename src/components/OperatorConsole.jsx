import { useState } from 'react';
import Sidebar from './Sidebar';
import MainConsolePanel from './MainConsolePanel';
import FileTreePanel from './FileTreePanel';
import SystemIntegrityPanel from './SystemIntegrityPanel';
import OrchestratorSandbox from './OrchestratorSandbox';

function OperatorConsole() {
  const [activeTab, setActiveTab] = useState('loops');

  // Function to handle tab changes from Sidebar
  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
  };

  // Determine which right panel to show based on active tab
  const renderRightPanel = () => {
    if (activeTab === 'health') {
      return <SystemIntegrityPanel />;
    } else {
      return <FileTreePanel />;
    }
  };

  return (
    <div className="flex h-screen w-full bg-gray-900 text-white">
      {/* Sidebar - 20% */}
      <div className="w-1/5 h-full">
        <Sidebar activeTab={activeTab} onTabChange={handleTabChange} />
      </div>
      
      {/* Main Console Panel - 60% */}
      <div className="w-3/5 h-full">
        <MainConsolePanel />
      </div>
      
      {/* Right Panel - 20% (FileTree or SystemIntegrity) */}
      <div className="w-1/5 h-full flex flex-col">
        <div className="flex-grow">
          {renderRightPanel()}
        </div>
        
        {/* Orchestrator Sandbox - pinned to bottom right */}
        <div className="mb-4 mx-4">
          <OrchestratorSandbox />
        </div>
      </div>
    </div>
  );
}

export default OperatorConsole;
