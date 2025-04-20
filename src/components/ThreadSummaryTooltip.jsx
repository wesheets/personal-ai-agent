import { useState, useRef, useEffect } from 'react';

function ThreadSummaryTooltip({ summary, status }) {
  const [isTooltipVisible, setIsTooltipVisible] = useState(false);
  const [isPinned, setIsPinned] = useState(false);
  const tooltipRef = useRef(null);
  
  // Status color mapping - updated for Promethios minimal UI
  const statusColors = {
    open: "border-green-700",
    closed: "border-blue-700",
    integrated: "border-cyan-700",
    discarded: "border-gray-600"
  };
  
  // Status icon mapping - updated for minimal UI
  const statusIcons = {
    open: "○",
    closed: "●",
    integrated: "✓",
    discarded: "×"
  };
  
  // Handle click outside to close tooltip if not pinned
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (tooltipRef.current && !tooltipRef.current.contains(event.target) && !isPinned) {
        setIsTooltipVisible(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isPinned]);
  
  // Toggle tooltip visibility
  const toggleTooltip = (e) => {
    e.stopPropagation();
    setIsTooltipVisible(!isTooltipVisible);
  };
  
  // Toggle pin status
  const togglePin = (e) => {
    e.stopPropagation();
    setIsPinned(!isPinned);
  };
  
  return (
    <div className="relative">
      {/* Summary indicator button */}
      <button
        className="absolute top-0 right-0 transform -translate-y-1/2 translate-x-1/2 w-5 h-5 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center text-xs text-cyan-400 hover:bg-gray-700 focus:outline-none focus:ring-1 focus:ring-cyan-700 transition-colors"
        onClick={toggleTooltip}
        title="Thread summary"
        aria-label="Show thread summary"
        aria-expanded={isTooltipVisible}
      >
        ℹ️
      </button>
      
      {/* Tooltip content */}
      {isTooltipVisible && (
        <div 
          ref={tooltipRef}
          className={`absolute top-0 right-0 transform translate-x-full mt-4 z-10 w-64 p-3 rounded-md bg-gray-900 border ${statusColors[status] || 'border-gray-700'} shadow-md`}
          role="tooltip"
        >
          {/* Tooltip header */}
          <div className="flex justify-between items-center mb-2 pb-1 border-b border-gray-800">
            <div className="flex items-center">
              <span className={`mr-1 ${
                status === 'open' ? 'text-green-400' :
                status === 'closed' ? 'text-blue-400' :
                status === 'integrated' ? 'text-cyan-400' :
                'text-gray-400'
              }`}>
                {statusIcons[status] || '○'}
              </span>
              <span className="text-xs font-medium text-gray-300">Thread Summary</span>
            </div>
            <button
              className={`w-5 h-5 rounded-full ${isPinned ? 'bg-gray-800 text-cyan-400 border border-cyan-700' : 'bg-gray-800 text-gray-500 border border-gray-700'} flex items-center justify-center text-xs hover:bg-gray-700 focus:outline-none focus:ring-1 focus:ring-cyan-700 transition-colors`}
              onClick={togglePin}
              title={isPinned ? "Unpin summary" : "Pin summary"}
              aria-label={isPinned ? "Unpin summary" : "Pin summary"}
              aria-pressed={isPinned}
            >
              📌
            </button>
          </div>
          
          {/* Summary content */}
          <div className="text-xs text-gray-300 whitespace-pre-line leading-relaxed">
            {summary}
          </div>
          
          {/* Status indicator */}
          <div className="mt-2 pt-1 border-t border-gray-800 flex items-center justify-between">
            <span className="text-xs text-gray-500">Status: </span>
            <span className={`text-xs font-medium flex items-center ${
              status === 'open' ? 'text-green-400' :
              status === 'closed' ? 'text-blue-400' :
              status === 'integrated' ? 'text-cyan-400' :
              'text-gray-400'
            }`}>
              <span className="mr-1">{statusIcons[status] || '○'}</span>
              {status || 'unknown'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default ThreadSummaryTooltip;
