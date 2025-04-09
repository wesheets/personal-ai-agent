import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAgentDebug } from './useAgentDebug';
import TerminalDrawer from './TerminalDrawer';
import { logout } from './hooks/useAuth';

export default function AgentChat() {
  // Persist conversationHistory as an array of user and assistant messages
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(true);
  const [loading, setLoading] = useState(false);
  const feedRef = useRef(null);
  const [debugOpen, setDebugOpen] = useState(false);
  const { payload, memory, logs, logPayload, logMemory, logThoughts } = useAgentDebug();
  const navigate = useNavigate();

  // Load conversation history from localStorage on component mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('conversationHistory');
    if (savedHistory) {
      try {
        setMessages(JSON.parse(savedHistory));
      } catch (e) {
        console.error('Failed to parse saved conversation history:', e);
      }
    }
  }, []);

  // Save conversation history to localStorage whenever it changes
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('conversationHistory', JSON.stringify(messages));
    }
  }, [messages]);

  useEffect(() => {
    feedRef.current?.scrollTo(0, feedRef.current.scrollHeight);
  }, [messages]);

  const handleSubmit = async () => {
    if (!input.trim()) return;
    setLoading(true);

    const userMessage = { role: 'user', content: input };
    const updatedHistory = [...messages, userMessage];
    setMessages(updatedHistory);
    setInput('');

    logPayload({ task_name: 'user', task_goal: input, streaming });

    try {
      // Use delegate-stream endpoint for streaming responses
      const endpoint = streaming ? '/api/agent/delegate-stream' : '/api/agent/delegate';
      
      if (streaming) {
        // Handle streaming response
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            agent_id: 'core-forge',
            prompt: input,
            history: updatedHistory // Pass full conversation history with every prompt
          })
        });

        if (!response.ok) {
          throw new Error(`Server responded with ${response.status}`);
        }

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
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            agent_id: 'core-forge',
            prompt: input,
            history: updatedHistory // Pass full conversation history with every prompt
          })
        });

        if (!res.ok) {
          throw new Error(`Server responded with ${res.status}`);
        }

        const data = await res.json();

        const assistantMessage = {
          role: 'assistant',
          content: data.message || '[No response]'
        };

        // Append GPT response to history array before next message
        setMessages(prev => [...prev, assistantMessage]);
      }

      logMemory('Memory accessed: ' + input);
      logThoughts('Core.Forge processed input and returned dynamic response.');

      setMessages(prev => [...prev, { role: 'system', content: '💾 Memory Logged' }]);
    } catch (error) {
      console.error('Error during chat:', error);
      setMessages(prev => [
        ...prev,
        { role: 'system', content: `⚠️ Error: ${error.message}` }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };

  const clearHistory = () => {
    setMessages([]);
    localStorage.removeItem('conversationHistory');
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="p-2 flex justify-between">
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

      <div ref={feedRef} className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-10">
            <p>Start a new conversation</p>
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
                <strong>{msg.role === 'user' ? 'You' : msg.role.toUpperCase()}:</strong> {msg.content}
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
          className="bg-white text-black px-4 py-2 rounded"
        >
          {loading ? 'Thinking...' : 'Send'}
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
