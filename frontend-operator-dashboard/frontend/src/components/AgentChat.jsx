import React, { useState, useEffect } from 'react';

export default function AgentChat({ agentId = 'core-forge' }) {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message to chat
    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch('/api/delegate-stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: agentId,
          prompt: input,
          history: messages
        })
      });

      if (!res.ok) {
        throw new Error(`Error: ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = { role: 'assistant', content: '' };

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        assistantMessage.content += chunk;

        // Update the message in real-time
        setMessages((prev) => [...prev.slice(0, -1), { ...assistantMessage }]);
      }

      // Log successful interaction to memory
      try {
        const memoryEntry = `LOG: User query: ${input}, Agent response: ${assistantMessage.content}`;
        fetch('/api/agent/delegate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            agent_id: 'memory',
            task: {
              input: memoryEntry
            }
          })
        });
        setMessages((prev) => [...prev, { role: 'system', content: '💾 Memory Logged' }]);
      } catch (memError) {
        console.error('Failed to log memory:', memError);
        setMessages((prev) => [...prev, { role: 'system', content: '⚠️ Failed to log memory' }]);
      }

      setIsLoading(false);
    } catch (error) {
      console.error('Error processing request:', error);

      // Enhanced error handling
      let errorMessage = "I'm sorry, I encountered an error processing your request.";

      if (error.response) {
        // Server responded with error
        errorMessage += ` Server error: ${error.response.status}`;
      } else if (error.request) {
        // Request made but no response
        errorMessage += ' No response from server. Please check your connection.';
      } else {
        // Other errors
        errorMessage += ` Error: ${error.message}`;
      }

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: errorMessage
        }
      ]);

      // Log memory of error
      try {
        const memoryEntry = `LOG: Error occurred: ${error.message}`;
        fetch('/api/agent/delegate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            agent_id: 'memory',
            task: {
              input: memoryEntry
            }
          })
        });
        setMessages((prev) => [...prev, { role: 'system', content: '⚠️ Error logged to memory' }]);
      } catch (memError) {
        console.error('Failed to log error to memory:', memError);
      }

      setIsLoading(false);
    }
  };

  return (
    <div className="agent-chat">
      <div className="chat-header">
        <h2>{agentId.charAt(0).toUpperCase() + agentId.slice(1).replace(/-/g, ' ')}</h2>
      </div>

      <div className="messages-container">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}
        {isLoading && <div className="loading">Agent is thinking...</div>}
      </div>

      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask something..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
