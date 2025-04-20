import { useState, useEffect } from 'react';

// Mock file data
const mockFiles = [
  {
    path: "src/components/InputBar.jsx",
    created_by: "hal",
    loop_created: 22,
    status: "complete",
    last_modified: "2025-04-21T13:22:00Z",
    type: "jsx"
  },
  {
    path: "src/components/ChatMessageFeed.jsx",
    created_by: "nova",
    loop_created: 23,
    status: "complete",
    last_modified: "2025-04-21T14:15:30Z",
    type: "jsx"
  },
  {
    path: "src/components/LoopStatusPanel.jsx",
    created_by: "hal",
    loop_created: 22,
    status: "complete",
    last_modified: "2025-04-21T12:45:10Z",
    type: "jsx"
  },
  {
    path: "src/utils/formatters.js",
    created_by: "ash",
    loop_created: 23,
    status: "in_progress",
    last_modified: "2025-04-21T15:10:20Z",
    type: "js"
  },
  {
    path: "src/styles/theme.css",
    created_by: "hal",
    loop_created: 22,
    status: "complete",
    last_modified: "2025-04-21T11:30:45Z",
    type: "css"
  },
  {
    path: "README.md",
    created_by: "critic",
    loop_created: 24,
    status: "complete",
    last_modified: "2025-04-21T16:05:15Z",
    type: "md"
  },
  {
    path: "package.json",
    created_by: "hal",
    loop_created: 22,
    status: "complete",
    last_modified: "2025-04-21T11:15:30Z",
    type: "json"
  }
];

// Mock planned files (not yet created)
const mockPlannedFiles = [
  {
    path: "src/components/SystemIntegrityPanel.jsx",
    planned_by: "orchestrator",
    loop_planned: 25,
    status: "planned",
    type: "jsx"
  },
  {
    path: "src/utils/agentHelpers.js",
    planned_by: "nova",
    loop_planned: 25,
    status: "planned",
    type: "js"
  },
  {
    path: "src/hooks/useFileSystem.js",
    planned_by: "hal",
    loop_planned: 25,
    status: "planned",
    type: "js"
  },
  {
    path: "tests/components/InputBar.test.jsx",
    planned_by: "critic",
    loop_planned: 25,
    status: "planned",
    type: "jsx"
  }
];

function FileTreePanel() {
  const [mode, setMode] = useState('build'); // 'build' or 'plan'
  const [expandedFolders, setExpandedFolders] = useState({
    'src': true,
    'src/components': true
  });
  const [hoveredFile, setHoveredFile] = useState(null);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  // Handle window resize for responsive design
  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Toggle between build and plan mode
  const toggleMode = () => {
    setMode(mode === 'build' ? 'plan' : 'build');
  };

  // Toggle folder expansion
  const toggleFolder = (folderPath) => {
    setExpandedFolders(prev => ({
      ...prev,
      [folderPath]: !prev[folderPath]
    }));
  };

  // Get all files based on current mode
  const getAllFiles = () => {
    if (mode === 'build') {
      return mockFiles;
    } else {
      // In plan mode, show both built and planned files
      return [...mockFiles, ...mockPlannedFiles];
    }
  };

  // Organize files into a folder structure
  const organizeFileTree = () => {
    const files = getAllFiles();
    const fileTree = {};

    files.forEach(file => {
      const pathParts = file.path.split('/');
      let currentLevel = fileTree;

      // Create folder structure
      for (let i = 0; i < pathParts.length - 1; i++) {
        const part = pathParts[i];
        if (!currentLevel[part]) {
          currentLevel[part] = { __isFolder: true, __children: {} };
        }
        currentLevel = currentLevel[part].__children;
      }

      // Add file to the deepest level
      const fileName = pathParts[pathParts.length - 1];
      currentLevel[fileName] = { ...file, __isFile: true };
    });

    return fileTree;
  };

  // Get file icon based on file type
  const getFileIcon = (fileType) => {
    switch (fileType) {
      case 'jsx':
        return '⚛️';
      case 'js':
        return '📜';
      case 'css':
        return '🎨';
      case 'md':
        return '📝';
      case 'json':
        return '🔧';
      default:
        return '📄';
    }
  };

  // Get status icon based on file status
  const getStatusIcon = (status) => {
    switch (status) {
      case 'complete':
        return <span className="text-green-500 ml-2">✅</span>;
      case 'in_progress':
        return <span className="text-yellow-500 ml-2">🕒</span>;
      case 'planned':
        return <span className="text-gray-500 ml-2">💡</span>;
      case 'flagged':
        return <span className="text-red-500 ml-2">❌</span>;
      default:
        return null;
    }
  };

  // Format timestamp for display
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Agent color mapping
  const agentColors = {
    hal: "text-blue-400",
    nova: "text-purple-400",
    critic: "text-yellow-400",
    ash: "text-teal-400",
    orchestrator: "text-gray-400"
  };

  // Handle mouse enter for file hover
  const handleMouseEnter = (e, item) => {
    setHoveredFile(item);
    
    // Calculate tooltip position based on available space
    const rect = e.currentTarget.getBoundingClientRect();
    const tooltipWidth = 200; // Approximate width of tooltip
    
    // Check if there's enough space to the right
    const spaceToRight = window.innerWidth - rect.right;
    const tooltipLeft = spaceToRight > tooltipWidth ? rect.right + 8 : rect.left - tooltipWidth - 8;
    
    setTooltipPosition({
      top: rect.top,
      left: tooltipLeft
    });
  };

  // Render a file or folder in the tree
  const renderTreeItem = (name, item, path = '', level = 0) => {
    const fullPath = path ? `${path}/${name}` : name;
    
    // If it's a folder
    if (item.__isFolder) {
      const isExpanded = expandedFolders[fullPath];
      
      return (
        <div key={fullPath} className="mb-1">
          <div 
            className="flex items-center text-gray-300 hover:text-white cursor-pointer"
            onClick={() => toggleFolder(fullPath)}
          >
            <span className="mr-1">{isExpanded ? '📂' : '📁'}</span>
            <span className="truncate">{name}</span>
            <span className="ml-1 text-xs text-gray-500">{isExpanded ? '▼' : '▶'}</span>
          </div>
          
          {isExpanded && (
            <div className="pl-4 mt-1">
              {Object.entries(item.__children).map(([childName, childItem]) => 
                renderTreeItem(childName, childItem, fullPath, level + 1)
              )}
            </div>
          )}
        </div>
      );
    }
    
    // If it's a file
    const isPlanned = item.status === 'planned';
    const fileClasses = isPlanned && mode === 'plan' 
      ? "flex items-center text-gray-500 hover:text-gray-300 cursor-pointer" 
      : "flex items-center text-gray-300 hover:text-white cursor-pointer";
    
    return (
      <div 
        key={fullPath}
        className="mb-1 relative group"
        onMouseEnter={(e) => handleMouseEnter(e, item)}
        onMouseLeave={() => setHoveredFile(null)}
      >
        <div className={fileClasses}>
          <span className="mr-1">{getFileIcon(item.type)}</span>
          <span className="truncate">{name}</span>
          {getStatusIcon(item.status)}
        </div>
      </div>
    );
  };

  const fileTree = organizeFileTree();

  // Determine if we should use compact mode for small screens
  const isCompactMode = windowWidth < 768;

  return (
    <div className="h-full bg-gray-900 w-full p-4 flex flex-col">
      <div className="border-b border-gray-800 pb-4 mb-4">
        <div className={`flex ${isCompactMode ? 'flex-col space-y-2' : 'justify-between items-center'}`}>
          <h2 className="text-lg font-semibold">Files</h2>
          
          {/* Mode toggle */}
          <div className="flex bg-gray-800 rounded-lg p-0.5">
            <button
              className={`px-3 py-1 text-xs rounded-md transition-colors ${
                mode === 'build' 
                  ? 'bg-gray-700 text-cyan-400' 
                  : 'text-gray-400 hover:text-gray-200'
              }`}
              onClick={() => setMode('build')}
            >
              🔨 Build
            </button>
            <button
              className={`px-3 py-1 text-xs rounded-md transition-colors ${
                mode === 'plan' 
                  ? 'bg-gray-700 text-cyan-400' 
                  : 'text-gray-400 hover:text-gray-200'
              }`}
              onClick={() => setMode('plan')}
            >
              💡 Plan
            </button>
          </div>
        </div>
      </div>
      
      {/* File tree */}
      <div className="flex-grow overflow-y-auto">
        <div className="text-sm">
          {Object.entries(fileTree).map(([name, item]) => 
            renderTreeItem(name, item)
          )}
        </div>
      </div>
      
      {/* Legend */}
      <div className="mt-4 pt-2 border-t border-gray-800 text-xs text-gray-500">
        <div className={`flex ${isCompactMode ? 'flex-col space-y-1' : 'items-center justify-between mb-1'}`}>
          <span className="flex items-center">
            <span className="text-green-500 mr-1">✅</span> Complete
          </span>
          <span className="flex items-center">
            <span className="text-yellow-500 mr-1">🕒</span> In Progress
          </span>
        </div>
        <div className="flex items-center">
          <span className="flex items-center">
            <span className="text-gray-500 mr-1">💡</span> Planned
          </span>
          {mode === 'plan' && !isCompactMode && (
            <span className="ml-4 text-gray-400">
              Showing {mockPlannedFiles.length} planned files
            </span>
          )}
        </div>
      </div>
      
      {/* Tooltip - positioned fixed to avoid container boundaries */}
      {hoveredFile && (
        <div 
          className="fixed bg-gray-800 border border-gray-700 rounded p-2 shadow-lg z-10 w-48"
          style={{ 
            top: `${tooltipPosition.top}px`, 
            left: `${tooltipPosition.left}px`,
            maxWidth: '90vw'
          }}
        >
          <div className="text-xs mb-1">
            <span className="text-gray-400">Path: </span>
            <span className="text-gray-300 break-words">{hoveredFile.path}</span>
          </div>
          <div className="text-xs mb-1">
            <span className="text-gray-400">
              {hoveredFile.status === 'planned' ? 'Planned by: ' : 'Created by: '}
            </span>
            <span className={agentColors[hoveredFile.status === 'planned' ? hoveredFile.planned_by : hoveredFile.created_by]}>
              {hoveredFile.status === 'planned' ? hoveredFile.planned_by : hoveredFile.created_by}
            </span>
          </div>
          <div className="text-xs mb-1">
            <span className="text-gray-400">
              {hoveredFile.status === 'planned' ? 'Loop planned: ' : 'Loop created: '}
            </span>
            <span className="text-cyan-400">
              {hoveredFile.status === 'planned' ? hoveredFile.loop_planned : hoveredFile.loop_created}
            </span>
          </div>
          {hoveredFile.status !== 'planned' && (
            <div className="text-xs">
              <span className="text-gray-400">Last modified: </span>
              <span className="text-gray-300">{formatTime(hoveredFile.last_modified)}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default FileTreePanel;
