import { useState, useRef, useEffect } from 'react';

// Mock chat message data
const mockChatMessages = [
  {
    role: "orchestrator",
    agent: "orchestrator",
    message: "Loop 22 initiated. HAL will scaffold the structure.",
    timestamp: "2025-04-20T12:10:01Z",
    loop: 22
  },
  {
    role: "agent",
    agent: "hal",
    message: "I'll create the basic file structure for the project. Starting with index.html, app.js, and styles.css.",
    timestamp: "2025-04-20T12:10:30Z",
    loop: 22
  },
  {
    role: "agent",
    agent: "nova",
    message: "Once HAL completes the structure, I'll implement the core logic for user authentication and data processing.",
    timestamp: "2025-04-20T12:11:15Z",
    loop: 22
  },
  {
    role: "operator",
    agent: "operator",
    message: "Please make sure to include responsive design principles in the CSS implementation.",
    timestamp: "2025-04-20T12:12:05Z",
    loop: 22
  },
  {
    role: "agent",
    agent: "hal",
    message: "I've added responsive meta tags and created a mobile-first CSS structure with media queries.",
    timestamp: "2025-04-20T12:13:20Z",
    loop: 22
  },
  {
    role: "agent",
    agent: "critic",
    message: "The current structure lacks proper error handling. We should implement try-catch blocks and user-friendly error messages.",
    timestamp: "2025-04-20T12:14:45Z",
    loop: 22
  },
  {
    role: "orchestrator",
    agent: "orchestrator",
    message: "Loop 23 initiated. NOVA will implement authentication logic.",
    timestamp: "2025-04-20T12:20:01Z",
    loop: 23
  },
  {
    role: "agent",
    agent: "nova",
    message: "I'm implementing JWT-based authentication with secure password hashing and token refresh mechanisms.",
    timestamp: "2025-04-20T12:21:30Z",
    loop: 23
  },
  {
    role: "agent",
    agent: "ash",
    message: "We should consider adding rate limiting to prevent brute force attacks on the authentication endpoints.",
    timestamp: "2025-04-20T12:22:45Z",
    loop: 23
  },
  {
    role: "cto",
    agent: "cto",
    message: "Please ensure all authentication follows OWASP security best practices and implement proper CSRF protection.",
    timestamp: "2025-04-20T12:23:15Z",
    loop: 23
  },
  {
    role: "operator",
    agent: "operator",
    message: "Can we also add support for OAuth providers like Google and GitHub?",
    timestamp: "2025-04-20T12:24:05Z",
    loop: 23
  }
];

function ChatMessageFeed({ userMessages = [] }) {
  // Combine mock messages with user messages
  const [messages, setMessages] = useState([...mockChatMessages]);
  const [filter, setFilter] = useState("all");
  const messagesEndRef = useRef(null);
  const scrollContainerRef = useRef(null);
  const [isUserScrolling, setIsUserScrolling] = useState(false);

  // Update messages when userMessages changes
  useEffect(() => {
    if (userMessages.length > 0) {
      setMessages([...mockChatMessages, ...userMessages]);
    }
  }, [userMessages]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current && !isUserScrolling) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isUserScrolling]);

  // Handle scroll events to detect if user is manually scrolling
  const handleScroll = () => {
    if (scrollContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
      setIsUserScrolling(!isAtBottom);
    }
  };

  // Filter messages based on selected filter
  const filteredMessages = messages.filter(msg => {
    if (filter === "all") return true;
    if (filter === "orchestrator") return msg.role === "orchestrator";
    if (filter === "operator") return msg.role === "operator";
    if (filter === "agents") return msg.role === "agent";
    return true;
  });

  // Agent color mapping
  const agentColors = {
    hal: "bg-blue-900 border-blue-700 text-blue-100",
    nova: "bg-purple-900 border-purple-700 text-purple-100",
    critic: "bg-yellow-900 border-yellow-700 text-yellow-100",
    ash: "bg-teal-900 border-teal-700 text-teal-100",
    orchestrator: "bg-gray-800 border-gray-700 text-gray-100",
    operator: "bg-cyan-900 border-cyan-700 text-cyan-50",
    cto: "bg-red-900 border-red-700 text-red-100"
  };

  // Format timestamp for display
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
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
    const bubbleStyle = agentColors[msg.agent?.toLowerCase()] || "bg-gray-800 border-gray-700 text-gray-100";
    
    // Special styling for CTO
    const isCTO = msg.agent?.toLowerCase() === "cto";
    
    return (
      <div key={index}>
        {/* Loop divider if needed */}
        {isNewLoop && (
          <div className="flex items-center my-4">
            <div className="flex-grow border-t border-gray-700"></div>
            <div className="mx-4 text-xs text-gray-500">Loop {msg.loop}</div>
            <div className="flex-grow border-t border-gray-700"></div>
          </div>
        )}
        
        {/* Message container with alignment */}
        <div className={`flex ${alignment} mb-3 group`}>
          <div className={`relative max-w-[80%] px-3 py-2 rounded-lg border ${bubbleStyle} shadow-sm`}>
            {/* Agent/role badge */}
            <div className="flex items-center mb-1">
              <span className="text-xs font-medium opacity-80">
                {msg.agent}
              </span>
              
              {/* CTO badge if applicable */}
              {isCTO && (
                <span className="ml-2 px-1.5 py-0.5 text-xs bg-red-800 text-white rounded">
                  CTO
                </span>
              )}
            </div>
            
            {/* Message content */}
            <div className={`${msg.role === "orchestrator" ? "font-mono text-sm" : ""}`}>
              {msg.message}
            </div>
            
            {/* File attachment if any */}
            {msg.file && (
              <div className="mt-2 px-2 py-1 bg-gray-700 bg-opacity-50 rounded inline-flex items-center">
                <span className="text-cyan-400 mr-1">📎</span>
                <span className="text-xs text-gray-300">{msg.file}</span>
              </div>
            )}
            
            {/* Timestamp on hover */}
            <div className="absolute bottom-0 right-0 transform translate-y-full opacity-0 group-hover:opacity-100 transition-opacity text-xs text-gray-500 mt-1 px-1">
              Loop {msg.loop} • {formatTime(msg.timestamp)}
            </div>
          </div>
        </div>
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
            className="bg-gray-800 text-gray-300 text-sm rounded-lg px-3 py-1.5 appearance-none cursor-pointer pr-8 focus:outline-none focus:ring-1 focus:ring-cyan-500"
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
        className="flex-grow overflow-y-auto pr-1" 
        onScroll={handleScroll}
        style={{ maxHeight: 'calc(100vh - 300px)' }}
      >
        {filteredMessages.map((msg, index) => 
          renderMessage(msg, index, index > 0 ? filteredMessages[index - 1] : null)
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

export default ChatMessageFeed;
