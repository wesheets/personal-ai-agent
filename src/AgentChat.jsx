import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAgentDebug } from './useAgentDebug';
import TerminalDrawer from './TerminalDrawer';
import { logout } from './hooks/useAuth';

export default function AgentChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(true);
  const [loading, setLoading] = useState(false);
  const feedRef = useRef(null);
  const [debugOpen, setDebugOpen] = useState(false);
  const { payload, memory, logs, logPayload, logMemory, logThoughts } = useAgentDebug();
  const navigate = useNavigate();

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

    const res = await fetch('/api/agent/delegate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent_id: 'core-forge',
        prompt: input,
        history: updatedHistory
      })
    });

    if (!res.ok) {
      setMessages((prev) => [
        ...prev,
        { role: 'system', content: '⚠️ Failed to receive a response from Core.Forge' }
      ]);
      setLoading(false);
      return;
    }

    const data = await res.json();

    const assistantMessage = {
      role: 'assistant',
      content: data.message || '[No response]'
    };

    setMessages((prev) => [...prev, assistantMessage]);

    logMemory('Memory accessed: ' + input);
    logThoughts('Core.Forge processed input and returned dynamic response.');

    setMessages((prev) => [...prev, { role: 'system', content: '💾 Memory Logged' }]);
    setLoading(false);
  };

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="p-2 flex justify-end">
        <button
          onClick={handleLogout}
          className="text-sm px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Logout
        </button>
      </div>

      <div ref={feedRef} className="flex-1 overflow-y-auto p-4">
        {messages.map((msg, i) => (
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
        ))}
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
