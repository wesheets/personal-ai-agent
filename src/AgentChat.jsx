import { useState, useRef, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAgentDebug } from './useAgentDebug';
import TerminalDrawer from './TerminalDrawer';
import { logout } from './hooks/useAuth';

// Agent name to backend ID mapping
const agentNameMap = {
  "ReflectionAgent": "LifeTree",
  "CADBuilderAgent": "SiteGen",
  "DreamAgent": "NEUREAL"
};

export default function AgentChat() {
  // Get agentId from URL params
  const { agentId } = useParams();
  const resolvedAgentId = agentNameMap[agentId] || agentId || 'core-forge';
  
  // State for agent data
  const [agent, setAgent] = useState(null);
  const [agentLoading, setAgentLoading] = useState(true);
  const [agentError, setAgentError] = useState(null);
  
  // Persist conversationHistory as an array of user and assistant messages
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(true);
  const [loading, setLoading] = useState(false);
  const feedRef = useRef(null);
  const [debugOpen, setDebugOpen] = useState(false);
  const { payload, memory, logs, logPayload, logMemory, logThoughts } = useAgentDebug();
  const navigate = useNavigate();
  
  // AbortController for fetch requests
  const abortControllerRef = useRef(null);
  
  // Retry counter for API calls
  const [retryCount, setRetryCount] = useState(0);
  const maxRetries = 1; // Maximum number of retries

  // Fetch agent data
  useEffect(() => {
    const fetchAgentData = async () => {
      setAgentLoading(true);
      setAgentError(null);
      
      try {
        const response = await fetch(`/api/agent/${resolvedAgentId}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch agent data: ${response.status}`);
        }
        
        const data = await response.json();
        setAgent(data);
      } catch (error) {
        console.error('Error fetching agent data:', error);
        setAgentError(error.message);
        // Fallback agent data
        setAgent({
          id: resolvedAgentId,
          name: resolvedAgentId
        });
      } finally {
        setAgentLoading(false);
      }
    };
    
    if (resolvedAgentId) {
      fetchAgentData();
    }
  }, [resolvedAgentId]);

  // Load conversation history from localStorage on component mount
  useEffect(() => {
    // Scope conversation history to specific agent
    const historyKey = `chat_history_${resolvedAgentId}`;
    const savedHistory = localStorage.getItem(historyKey);
    if (savedHistory) {
      try {
        setMessages(JSON.parse(savedHistory));
      } catch (e) {
        console.error(`Failed to parse saved conversation history for ${resolvedAgentId}:`, e);
      }
    } else {
      // Clear messages if no history exists for this agent
      setMessages([]);
    }
  }, [resolvedAgentId]);

  // Save conversation history to localStorage whenever it changes
  useEffect(() => {
    if (messages.length > 0 && resolvedAgentId) {
      const historyKey = `chat_history_${resolvedAgentId}`;
      localStorage.setItem(historyKey, JSON.stringify(messages));
    }
  }, [messages, resolvedAgentId]);

  useEffect(() => {
    feedRef.current?.scrollTo(0, feedRef.current.scrollHeight);
  }, [messages]);

  const makeApiRequest = async (endpoint, body, signal) => {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal
    });
    
    // Handle API failures (502, 504, etc.)
    if (response.status === 502 || response.status === 504) {
      throw new Error('UNAVAILABLE');
    }

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }
    
    return response;
  };

  const handleSubmit = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setRetryCount(0); // Reset retry counter on new submission

    // Cancel any ongoing requests
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    // Create new AbortController for this request
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    const userMessage = { role: 'user', content: input };
    const updatedHistory = [...messages, userMessage];
    setMessages(updatedHistory);
    setInput('');

    logPayload({ task_name: 'user', task_goal: input, streaming, agent_id: resolvedAgentId });

    const makeRequest = async (isRetry = false) => {
      try {
        // Use delegate-stream endpoint for streaming responses
        const endpoint = streaming ? '/api/agent/delegate-stream' : '/api/agent/delegate';
        const requestBody = {
          agent_id: resolvedAgentId,
          prompt: input,
          history: updatedHistory // Pass full conversation history with every prompt
        };
        
        if (streaming) {
          // Handle streaming response
          const response = await makeApiRequest(endpoint, requestBody, signal);
          
          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let responseText = '';
          
          // Create a placeholder for the streaming response
          const assistantMessageId = Date.now();
          setMessages(prev => [...prev, { 
            id: assistantMessageId,
            role: 'assistant', 
            content: '' 
          }]);

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            responseText += chunk;
            
            // Update the message with the accumulated text
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessageId 
                ? { ...msg, content: responseText } 
                : msg
            ));
          }

          // Finalize the message without the temporary ID
          setMessages(prev => prev.map(msg => 
            msg.id === assistantMessageId 
              ? { role: 'assistant', content: responseText } 
              : msg
          ));
        } else {
          // Handle non-streaming response
          const res = await makeApiRequest(endpoint, requestBody, signal);
          const data = await res.json();

          const assistantMessage = {
            role: 'assistant',
            content: data.message || '[No response]'
          };

          // Append GPT response to history array before next message
          setMessages(prev => [...prev, assistantMessage]);
        }

        logMemory('Memory accessed: ' + input);
        logThoughts(`${resolvedAgentId} processed input and returned dynamic response.`);

        setMessages(prev => [...prev, { role: 'system', content: '💾 Memory Logged' }]);
        
        // Reset retry counter on success
        setRetryCount(0);
      } catch (error) {
        console.error('Error during chat:', error);
        
        // Handle retry logic for unavailable agent
        if (error.message === 'UNAVAILABLE' && retryCount < maxRetries && !isRetry) {
          console.log(`Retrying request (${retryCount + 1}/${maxRetries})...`);
          setRetryCount(prev => prev + 1);
          
          // Add a retry message
          setMessages(prev => [
            ...prev,
            { role: 'system', content: `⚠️ Connection issue. Retrying...` }
          ]);
          
          // Wait a moment before retrying
          setTimeout(() => makeRequest(true), 1500);
          return;
        }
        
        // Special handling for unavailable agent
        if (error.message === 'UNAVAILABLE' || error.name === 'AbortError') {
          setMessages(prev => [
            ...prev,
            { role: 'system', content: `⚠️ This agent is temporarily unavailable. Please try again or switch agents.` }
          ]);
        } else {
          setMessages(prev => [
            ...prev,
            { role: 'system', content: `⚠️ Agent response failed. Try again or switch agents.` }
          ]);
        }
        
        // Reset retry counter on final failure
        setRetryCount(0);
      } finally {
        if (isRetry || retryCount >= maxRetries) {
          setLoading(false);
          abortControllerRef.current = null;
        }
      }
    };
    
    // Start the request process
    await makeRequest();
  };

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };

  const clearHistory = () => {
    setMessages([]);
    if (resolvedAgentId) {
      const historyKey = `chat_history_${resolvedAgentId}`;
      localStorage.removeItem(historyKey);
    }
  };

  // Show loading spinner while agent is being fetched
  if (agentLoading) {
    return (
      <div className="flex flex-col h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
        <p className="text-gray-600">Loading agent...</p>
      </div>
    );
  }

  // Show error state if agent fetch failed
  if (agentError && !agent) {
    return (
      <div className="flex flex-col h-screen items-center justify-center">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative max-w-md">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> Failed to load agent. Please try again later.</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen">
      <div className="p-2 flex justify-between items-center">
        <div className="flex items-center">
          <span className="font-bold mr-2">
            {agent?.name || resolvedAgentId}
          </span>
          <span className="text-xs bg-gray-200 px-2 py-1 rounded">
            {resolvedAgentId}
          </span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={clearHistory}
            className="text-sm px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            Clear History
          </button>
          <button
            onClick={handleLogout}
            className="text-sm px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Logout
          </button>
        </div>
      </div>

      <div ref={feedRef} className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-10">
            <p>Start a new conversation with {agent?.name || resolvedAgentId}</p>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div key={i} className={`my-2 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
              <div
                className={`inline-block px-4 py-2 rounded-xl ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : msg.role === 'system'
                      ? 'bg-gray-500 text-white'
                      : 'bg-gray-200 text-black'
                }`}
              >
                <strong>{msg.role === 'user' ? 'You' : msg.role === 'assistant' ? (agent?.name || 'ASSISTANT') : msg.role.toUpperCase()}:</strong> {msg.content}
              </div>
            </div>
          ))
        )}
      </div>

      <div className="p-4 border-t flex items-center gap-2">
        <button
          onClick={() => setDebugOpen(!debugOpen)}
          className="text-sm px-2 py-1 border rounded"
        >
          &lt;/&gt;
        </button>
        <button
          onClick={() => setStreaming(!streaming)}
          className="text-sm px-2 py-1 border rounded"
        >
          {streaming ? 'Streaming ON' : 'Streaming OFF'}
        </button>
        <textarea
          className="flex-1 border rounded p-2"
          rows={2}
          placeholder="Enter your task..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) =>
            e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSubmit())
          }
        />
        <button
          onClick={handleSubmit}
          disabled={loading}
          className={`px-4 py-2 rounded ${loading ? 'bg-gray-400' : 'bg-white text-black'}`}
        >
          {loading ? (
            <span className="flex items-center">
              <span className="animate-spin h-4 w-4 mr-2 border-t-2 border-b-2 border-gray-900 rounded-full"></span>
              Thinking...
            </span>
          ) : (
            'Send'
          )}
        </button>
      </div>

      <TerminalDrawer
        open={debugOpen}
        onClose={() => setDebugOpen(false)}
        payload={payload}
        memory={memory}
        logs={logs}
      />
    </div>
  );
}
