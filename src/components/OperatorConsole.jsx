import Sidebar from './Sidebar';
import MainConsolePanel from './MainConsolePanel';
import FileTreePanel from './FileTreePanel';

function OperatorConsole() {
  return (
    <div className="flex h-screen w-full bg-gray-900 text-white">
      {/* Sidebar - 20% */}
      <div className="w-1/5 h-full">
        <Sidebar />
      </div>
      
      {/* Main Console Panel - 60% */}
      <div className="w-3/5 h-full">
        <MainConsolePanel />
      </div>
      
      {/* File Tree Panel - 20% */}
      <div className="w-1/5 h-full">
        <FileTreePanel />
      </div>
    </div>
  );
}

export default OperatorConsole;
