import React, { useState } from 'react';
import AgentSidebar from './components/AgentSidebar';
import AgentInputBar from './components/AgentInputBar';
import ThemeToggle from './components/ThemeToggle';

export default function ControlRoom() {
  const [messages, setMessages] = useState([]);

  const handleSend = (message) => {
    // For now, append message locally; ORCHESTRATOR integration coming next
    const newMessage = {
      id: Date.now(),
      sender: 'operator',
      text: message,
    };
    setMessages((prev) => [...prev, newMessage]);
  };

  return (
    <div className="flex h-screen bg-black text-white overflow-hidden">
      {/* Sidebar */}
      <AgentSidebar />

      {/* Main Panel */}
      <main className="flex-1 flex flex-col overflow-y-auto">
        <div className="flex-1 flex flex-col p-6 space-y-6 overflow-y-auto">
          <header className="text-center">
            <h1 className="text-3xl font-bold tracking-wide mb-2">🧠 Promethios Control Room</h1>
            <p className="text-sm text-gray-400">
              Operator interface connected. Awaiting input.
            </p>
          </header>

          {/* Message Feed (placeholder for now) */}
          <div className="flex-1 bg-gray-900 rounded-xl p-4 overflow-y-auto">
            {messages.map((msg) => (
              <div key={msg.id} className={`text-sm mb-3 ${msg.sender === 'operator' ? 'text-right' : 'text-left'}`}>
                <span className="font-mono text-gray-300">{msg.text}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Input */}
        <AgentInputBar onSend={handleSend} />
      </main>

      {/* Theme Button */}
      <ThemeToggle />
    </div>
  );
}
