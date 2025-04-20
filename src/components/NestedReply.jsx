import { useState } from 'react';
import ThreadSummaryTooltip from './ThreadSummaryTooltip';

function NestedReply({ 
  reply, 
  agentColors, 
  formatTime, 
  parentMessage, 
  allMessages, 
  expandedThreads, 
  toggleThreadExpansion 
}) {
  // Determine if this reply has nested replies
  const hasNestedReplies = allMessages.some(msg => msg.parent_id === reply.message_id);
  
  // Get nested replies for this reply
  const nestedReplies = allMessages.filter(msg => msg.parent_id === reply.message_id);
  
  // Check if nested replies are expanded
  const areNestedRepliesExpanded = expandedThreads[reply.message_id];
  
  // Determine if this reply should be collapsed based on depth
  const shouldCollapseByDefault = reply.depth > 3;
  
  // State for collapsed status (initially collapsed if depth > 3)
  const [isCollapsed, setIsCollapsed] = useState(shouldCollapseByDefault);
  
  // Toggle collapsed state
  const toggleCollapsed = (e) => {
    e.stopPropagation();
    setIsCollapsed(!isCollapsed);
  };
  
  // Determine bubble style based on agent
  const bubbleStyle = agentColors[reply.agent?.toLowerCase()] || "bg-gray-900 border-gray-700 text-gray-100";
  
  // Calculate left margin based on depth
  const depthMargin = `${Math.min(reply.depth * 16, 64)}px`;
  
  // Special styling for CTO
  const isCTO = reply.agent?.toLowerCase() === "cto";
  
  // Get thread summary if available
  const getThreadSummary = () => {
    if (!reply.thread_id) return null;
    
    // Find root message of thread
    const rootMessage = allMessages.find(m => 
      m.thread_id === reply.thread_id && !m.parent_id
    );
    
    return rootMessage?.summary;
  };
  
  // Get thread status
  const getThreadStatus = () => {
    if (!reply.thread_id) return null;
    
    // Find root message of thread
    const rootMessage = allMessages.find(m => 
      m.thread_id === reply.thread_id && !m.parent_id
    );
    
    return rootMessage?.status || "open";
  };
  
  // If collapsed, show only a preview
  if (isCollapsed) {
    return (
      <div 
        className="flex mb-2 cursor-pointer hover:opacity-90 focus:outline-none focus:ring-1 focus:ring-cyan-700"
        onClick={toggleCollapsed}
        style={{ marginLeft: depthMargin }}
        tabIndex={0}
        role="button"
        aria-expanded="false"
        aria-label="Expand nested reply"
      >
        <div className={`px-3 py-1 rounded-md border ${bubbleStyle} shadow-sm opacity-80 flex items-center transition-opacity`}>
          <span className="text-xs mr-2">↳</span>
          <span className={`text-xs font-medium mr-1 ${
            reply.agent?.toLowerCase() === 'hal' ? 'text-blue-400' :
            reply.agent?.toLowerCase() === 'nova' ? 'text-purple-400' :
            reply.agent?.toLowerCase() === 'critic' ? 'text-amber-400' :
            reply.agent?.toLowerCase() === 'ash' ? 'text-teal-400' :
            reply.agent?.toLowerCase() === 'cto' ? 'text-red-400' :
            reply.agent?.toLowerCase() === 'operator' ? 'text-cyan-400' :
            'text-gray-300'
          }`}>
            {reply.agent}:
          </span>
          <span className="text-xs truncate" style={{ maxWidth: '200px' }}>
            {reply.message.substring(0, 50)}{reply.message.length > 50 ? '...' : ''}
          </span>
          <span className="text-xs ml-2 text-gray-500">[Click to expand]</span>
        </div>
      </div>
    );
  }
  
  return (
    <div className="mb-2" style={{ marginLeft: depthMargin }}>
      <div className="flex group">
        <div className={`relative max-w-[90%] px-3 py-2 rounded-md border ${bubbleStyle} shadow-sm`}>
          {/* Collapse button for deep replies */}
          {reply.depth > 3 && (
            <button 
              className="absolute -left-6 top-2 text-gray-500 hover:text-gray-300 text-xs focus:outline-none focus:text-cyan-400"
              onClick={toggleCollapsed}
              aria-label="Collapse reply"
            >
              ◀
            </button>
          )}
          
          {/* Reply indicator */}
          <div className="absolute -left-4 top-1/2 transform -translate-y-1/2 text-gray-600">
            ↳
          </div>
          
          {/* Agent/role badge */}
          <div className="flex items-center mb-1.5">
            <span className={`text-xs font-medium ${
              reply.agent?.toLowerCase() === 'hal' ? 'text-blue-400' :
              reply.agent?.toLowerCase() === 'nova' ? 'text-purple-400' :
              reply.agent?.toLowerCase() === 'critic' ? 'text-amber-400' :
              reply.agent?.toLowerCase() === 'ash' ? 'text-teal-400' :
              reply.agent?.toLowerCase() === 'cto' ? 'text-red-400' :
              reply.agent?.toLowerCase() === 'operator' ? 'text-cyan-400' :
              'text-gray-300'
            }`}>
              {reply.agent}
            </span>
            
            {/* CTO badge if applicable */}
            {isCTO && (
              <span className="ml-2 px-1.5 py-0.5 text-xs bg-gray-800 text-red-400 border border-red-800 rounded-sm">
                CTO
              </span>
            )}
            
            {/* Depth indicator */}
            <span className="ml-2 text-xs text-gray-500">
              depth: {reply.depth}
            </span>
          </div>
          
          {/* Message content */}
          <div className={`${reply.role === "orchestrator" ? "font-mono text-sm" : ""} leading-relaxed`}>
            {reply.message}
          </div>
          
          {/* File attachment if any */}
          {reply.file && (
            <div className="mt-2 px-2 py-1 bg-gray-800 rounded-sm inline-flex items-center">
              <span className="text-cyan-400 mr-1">📎</span>
              <span className="text-xs text-gray-300">{reply.file}</span>
            </div>
          )}
          
          {/* Nested replies badge if applicable */}
          {hasNestedReplies && (
            <div 
              className="mt-2 px-2 py-1 bg-gray-800 rounded-sm inline-flex items-center cursor-pointer hover:bg-gray-700 focus:outline-none focus:ring-1 focus:ring-cyan-700 transition-colors"
              onClick={() => toggleThreadExpansion(reply.message_id)}
              tabIndex={0}
              role="button"
              aria-expanded={areNestedRepliesExpanded}
              aria-label={`${areNestedRepliesExpanded ? 'Hide' : 'Show'} ${nestedReplies.length} ${nestedReplies.length === 1 ? 'reply' : 'replies'}`}
            >
              <span className="text-cyan-400 mr-1">
                {areNestedRepliesExpanded ? '▾' : '▸'}
              </span>
              <span className="text-xs text-gray-300">
                {areNestedRepliesExpanded ? 'Hide' : 'Show'} {nestedReplies.length} {nestedReplies.length === 1 ? 'reply' : 'replies'}
              </span>
            </div>
          )}
          
          {/* Timestamp on hover */}
          <div className="absolute bottom-0 right-0 transform translate-y-full opacity-0 group-hover:opacity-100 transition-opacity text-xs text-gray-500 mt-1 px-1">
            Loop {reply.loop} • {formatTime(reply.timestamp)}
          </div>
          
          {/* Thread summary tooltip if available */}
          {reply.thread_id && getThreadSummary() && (
            <ThreadSummaryTooltip 
              summary={getThreadSummary()} 
              status={getThreadStatus()}
            />
          )}
        </div>
      </div>
      
      {/* Nested replies if expanded */}
      {hasNestedReplies && areNestedRepliesExpanded && (
        <div className="mt-1">
          {nestedReplies.map((nestedReply, index) => (
            <NestedReply
              key={index}
              reply={nestedReply}
              agentColors={agentColors}
              formatTime={formatTime}
              parentMessage={reply}
              allMessages={allMessages}
              expandedThreads={expandedThreads}
              toggleThreadExpansion={toggleThreadExpansion}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default NestedReply;
