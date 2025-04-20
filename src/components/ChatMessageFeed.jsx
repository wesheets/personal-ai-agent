import { useState, useRef, useEffect } from 'react';
import NestedReply from './NestedReply';
import ThreadSummaryTooltip from './ThreadSummaryTooltip';

function ChatMessageFeed({ userMessages, isThinking }) {
  const [filter, setFilter] = useState('all');
  const [isUserScrolling, setIsUserScrolling] = useState(false);
  const [expandedThreads, setExpandedThreads] = useState({});
  const scrollContainerRef = useRef(null);
  const messagesEndRef = useRef(null);
  
  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current && !isUserScrolling) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [userMessages, isUserScrolling]);
  
  // Handle scroll events to detect user scrolling
  const handleScroll = () => {
    if (scrollContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
      
      setIsUserScrolling(!isAtBottom);
    }
  };
  
  // Toggle thread expansion
  const toggleThreadExpansion = (threadId) => {
    setExpandedThreads(prev => ({
      ...prev,
      [threadId]: !prev[threadId]
    }));
  };
  
  // Filter messages based on selected filter
  const filteredMessages = userMessages.filter(msg => {
    if (filter === "all") return true;
    if (filter === "orchestrator") return msg.role === "orchestrator";
    if (filter === "operator") return msg.role === "operator";
    if (filter === "agents") return msg.role === "agent";
    return true;
  });
  
  // Agent color mapping - updated for Promethios minimal UI
  const agentColors = {
    hal: "bg-gray-900 border-blue-800 text-blue-50",
    nova: "bg-gray-900 border-purple-800 text-purple-50",
    critic: "bg-gray-900 border-amber-800 text-amber-50",
    ash: "bg-gray-900 border-teal-800 text-teal-50",
    orchestrator: "bg-gray-900 border-gray-700 text-gray-100",
    operator: "bg-gray-900 border-cyan-800 text-cyan-50",
    cto: "bg-gray-900 border-red-800 text-red-50"
  };
  
  // Thread status badge mapping - updated for Promethios minimal UI
  const statusBadges = {
    open: "bg-gray-800 text-green-400 border border-green-700",
    closed: "bg-gray-800 text-blue-400 border border-blue-700",
    integrated: "bg-gray-800 text-cyan-400 border border-cyan-700",
    discarded: "bg-gray-800 text-gray-400 border border-gray-600"
  };
  
  // Format timestamp for display
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  // Check if message has replies
  const hasReplies = (msg) => {
    return msg.thread_id && userMessages.some(reply => 
      reply.parent_id === msg.message_id || 
      (reply.thread_id === msg.thread_id && reply.parent_id)
    );
  };
  
  // Get replies for a message
  const getReplies = (msg) => {
    if (!msg.thread_id) return [];
    
    // Get direct replies to this message
    const directReplies = userMessages.filter(reply => 
      reply.parent_id === msg.message_id
    );
    
    // Get all replies in the thread
    const allThreadReplies = userMessages.filter(reply => 
      reply.thread_id === msg.thread_id && reply.message_id !== msg.message_id
    );
    
    // If this is the root message of the thread, return all thread replies
    if (!msg.parent_id) {
      return allThreadReplies;
    }
    
    // Otherwise, return only direct replies
    return directReplies;
  };
  
  // Get thread status
  const getThreadStatus = (msg) => {
    if (!msg.thread_id) return null;
    
    // Find root message of thread
    const rootMessage = userMessages.find(m => 
      m.thread_id === msg.thread_id && !m.parent_id
    );
    
    return rootMessage?.status || "open";
  };
  
  // Get thread summary
  const getThreadSummary = (msg) => {
    if (!msg.thread_id) return null;
    
    // Find root message of thread
    const rootMessage = userMessages.find(m => 
      m.thread_id === msg.thread_id && !m.parent_id
    );
    
    return rootMessage?.summary;
  };
  
  // Render a message bubble based on role
  const renderMessage = (msg, index, prevMsg) => {
    // Check if this is the start of a new loop
    const isNewLoop = index === 0 || msg.loop !== prevMsg?.loop;
    
    // Determine alignment based on role
    const alignment = msg.role === "operator" 
      ? "justify-end" 
      : msg.role === "orchestrator" 
        ? "justify-center" 
        : "justify-start";
    
    // Determine bubble style based on agent
    const bubbleStyle = agentColors[msg.agent?.toLowerCase()] || "bg-gray-900 border-gray-700 text-gray-100";
    
    // Special styling for CTO
    const isCTO = msg.agent?.toLowerCase() === "cto";
    
    // Special styling for orchestrator planning messages
    const isOrchestratorPlanning = msg.role === "orchestrator" && msg.loop_plan;
    
    // Check if message has replies
    const messageHasReplies = hasReplies(msg);
    
    // Get replies for this message
    const replies = messageHasReplies ? getReplies(msg) : [];
    
    // Get thread status if this is a root message
    const threadStatus = !msg.parent_id && msg.thread_id ? msg.status || "open" : null;
    
    // Check if thread is expanded
    const isThreadExpanded = expandedThreads[msg.thread_id];
    
    return (
      <div key={index}>
        {/* Loop divider if needed */}
        {isNewLoop && (
          <div className="flex items-center my-4">
            <div className="flex-grow border-t border-gray-800"></div>
            <div className="mx-4 text-xs text-gray-500">Loop {msg.loop}</div>
            <div className="flex-grow border-t border-gray-800"></div>
          </div>
        )}
        
        {/* Message container with alignment */}
        <div className={`flex ${alignment} mb-3 group`}>
          <div className={`relative max-w-[80%] px-3 py-2 rounded-md border ${bubbleStyle} shadow-sm ${
            isOrchestratorPlanning ? 'border-cyan-800 shadow-[0_0_4px_rgba(6,182,212,0.15)]' : ''
          }`}>
            {/* Agent/role badge */}
            <div className="flex items-center mb-1.5">
              <span className={`text-xs font-medium ${
                msg.agent?.toLowerCase() === 'hal' ? 'text-blue-400' :
                msg.agent?.toLowerCase() === 'nova' ? 'text-purple-400' :
                msg.agent?.toLowerCase() === 'critic' ? 'text-amber-400' :
                msg.agent?.toLowerCase() === 'ash' ? 'text-teal-400' :
                msg.agent?.toLowerCase() === 'cto' ? 'text-red-400' :
                msg.agent?.toLowerCase() === 'operator' ? 'text-cyan-400' :
                'text-gray-300'
              }`}>
                {msg.agent}
              </span>
              
              {/* CTO badge if applicable */}
              {isCTO && (
                <span className="ml-2 px-1.5 py-0.5 text-xs bg-gray-800 text-red-400 border border-red-800 rounded-sm">
                  CTO
                </span>
              )}
              
              {/* Planning badge if applicable */}
              {isOrchestratorPlanning && (
                <span className="ml-2 px-1.5 py-0.5 text-xs bg-gray-800 text-cyan-400 border border-cyan-800 rounded-sm flex items-center">
                  <span className="mr-1">⚙️</span> planning
                </span>
              )}
              
              {/* Thread status badge if applicable */}
              {threadStatus && (
                <span className={`ml-2 px-1.5 py-0.5 text-xs ${statusBadges[threadStatus]} rounded-sm flex items-center`}>
                  <span className="mr-1">
                    {threadStatus === 'open' ? '○' : 
                     threadStatus === 'closed' ? '●' : 
                     threadStatus === 'integrated' ? '✓' : '×'}
                  </span>
                  {threadStatus}
                </span>
              )}
            </div>
            
            {/* Message content */}
            <div className={`${msg.role === "orchestrator" ? "font-mono text-sm" : ""} leading-relaxed`}>
              {msg.message}
            </div>
            
            {/* Thread summary if available */}
            {msg.summary && !msg.parent_id && (
              <div className="mt-2 pt-2 border-t border-gray-800 text-xs text-gray-300">
                <div className="flex items-center mb-1">
                  <span className="text-cyan-400 mr-1">📝</span>
                  <span className="font-medium">Summary:</span>
                </div>
                <div className="pl-2 border-l-2 border-gray-800 leading-relaxed">
                  {msg.summary}
                </div>
              </div>
            )}
            
            {/* Loop plan if available */}
            {msg.loop_plan && (
              <div className="mt-2 pt-2 border-t border-gray-800 font-mono text-xs">
                <div className="mb-1">
                  <span className="text-gray-400">Agents: </span>
                  {msg.loop_plan.agents.map((agent, i) => (
                    <span key={i} className={`${
                      agent.toLowerCase() === 'hal' ? 'text-blue-400' :
                      agent.toLowerCase() === 'nova' ? 'text-purple-400' :
                      agent.toLowerCase() === 'critic' ? 'text-amber-400' :
                      agent.toLowerCase() === 'ash' ? 'text-teal-400' :
                      'text-gray-300'
                    } ${i < msg.loop_plan.agents.length - 1 ? 'mr-1' : ''}`}>
                      {agent}{i < msg.loop_plan.agents.length - 1 ? ' → ' : ''}
                    </span>
                  ))}
                </div>
                <div className="mb-1">
                  <span className="text-gray-400">Goals: </span>
                  {msg.loop_plan.goals.map((goal, i) => (
                    <span key={i} className="text-gray-300">
                      {goal}{i < msg.loop_plan.goals.length - 1 ? ', ' : ''}
                    </span>
                  ))}
                </div>
                <div>
                  <span className="text-gray-400">Files: </span>
                  {msg.loop_plan.planned_files.map((file, i) => (
                    <span key={i} className="text-cyan-300">
                      {file}{i < msg.loop_plan.planned_files.length - 1 ? ', ' : ''}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {/* File attachment if any */}
            {msg.file && (
              <div className="mt-2 px-2 py-1 bg-gray-800 rounded-sm inline-flex items-center">
                <span className="text-cyan-400 mr-1">📎</span>
                <span className="text-xs text-gray-300">{msg.file}</span>
              </div>
            )}
            
            {/* Thread replies badge if applicable */}
            {messageHasReplies && !msg.parent_id && (
              <div 
                className="mt-2 px-2 py-1 bg-gray-800 rounded-sm inline-flex items-center cursor-pointer hover:bg-gray-700 focus:outline-none focus:ring-1 focus:ring-cyan-700 transition-colors"
                onClick={() => toggleThreadExpansion(msg.thread_id)}
                tabIndex={0}
                role="button"
                aria-expanded={isThreadExpanded}
                aria-label={`${isThreadExpanded ? 'Hide' : 'Show'} ${replies.length} ${replies.length === 1 ? 'reply' : 'replies'}`}
              >
                <span className="text-cyan-400 mr-1">
                  {isThreadExpanded ? '▾' : '▸'}
                </span>
                <span className="text-xs text-gray-300">
                  {isThreadExpanded ? 'Hide' : 'Show'} {replies.length} {replies.length === 1 ? 'reply' : 'replies'}
                </span>
              </div>
            )}
            
            {/* Timestamp on hover */}
            <div className="absolute bottom-0 right-0 transform translate-y-full opacity-0 group-hover:opacity-100 transition-opacity text-xs text-gray-500 mt-1 px-1">
              Loop {msg.loop} • {formatTime(msg.timestamp)}
            </div>
            
            {/* Thread summary tooltip */}
            {msg.thread_id && getThreadSummary(msg) && (
              <ThreadSummaryTooltip 
                summary={getThreadSummary(msg)} 
                status={getThreadStatus(msg)}
              />
            )}
          </div>
        </div>
        
        {/* Nested replies if thread is expanded */}
        {messageHasReplies && isThreadExpanded && !msg.parent_id && (
          <div className="ml-8 mb-3">
            {replies.map((reply, replyIndex) => (
              <NestedReply
                key={replyIndex}
                reply={reply}
                agentColors={agentColors}
                formatTime={formatTime}
                parentMessage={msg}
                allMessages={userMessages}
                expandedThreads={expandedThreads}
                toggleThreadExpansion={toggleThreadExpansion}
              />
            ))}
          </div>
        )}
      </div>
    );
  };
  
  return (
    <div className="w-full flex flex-col">
      {/* Filter controls */}
      <div className="flex justify-between items-center mb-3 pb-2 border-b border-gray-800">
        <div className="relative">
          <select 
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-gray-900 text-gray-300 text-sm rounded-sm px-3 py-1.5 appearance-none cursor-pointer pr-8 border border-gray-800 focus:outline-none focus:ring-1 focus:ring-cyan-700 focus:border-cyan-700 transition-colors"
            aria-label="Filter messages"
          >
            <option value="all">All Messages</option>
            <option value="orchestrator">Orchestrator Only</option>
            <option value="operator">Operator Only</option>
            <option value="agents">Agents Only</option>
          </select>
          <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
            <span className="text-gray-500">▼</span>
          </div>
        </div>
      </div>
      
      {/* Messages container with scroll */}
      <div 
        ref={scrollContainerRef}
        className="flex-grow overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-gray-900" 
        onScroll={handleScroll}
        style={{ maxHeight: 'calc(100vh - 300px)' }}
      >
        {filteredMessages.filter(msg => !msg.parent_id).map((msg, index) => 
          renderMessage(msg, index, index > 0 ? filteredMessages.filter(m => !m.parent_id)[index - 1] : null)
        )}
        
        {/* Thinking indicator */}
        {isThinking && (
          <div className="flex justify-center mb-3">
            <div className="px-4 py-2 bg-gray-900 border border-gray-800 rounded-md shadow-sm">
              <div className="flex items-center">
                <div className="mr-2 text-gray-400">
                  <span className="inline-block w-1.5 h-1.5 bg-cyan-500 rounded-full animate-pulse mr-1"></span>
                  <span className="inline-block w-1.5 h-1.5 bg-cyan-500 rounded-full animate-pulse delay-150 mr-1"></span>
                  <span className="inline-block w-1.5 h-1.5 bg-cyan-500 rounded-full animate-pulse delay-300"></span>
                </div>
                <span className="text-sm text-gray-300 font-mono">Orchestrator thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

export default ChatMessageFeed;
