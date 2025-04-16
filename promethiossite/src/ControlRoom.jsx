import React, { useState } from 'react';
import AgentSidebar from './components/AgentSidebar';
import AgentInputBar from './components/AgentInputBar';
import AgentLogThread from './components/AgentLogThread';
import ThemeToggle from './components/ThemeToggle';

export default function ControlRoom() {
  const [messages, setMessages] = useState([]);
  const [thinking, setThinking] = useState(false);

  const handleSend = async (message) => {
    const userMessage = {
      id: Date.now(),
      sender: 'operator',
      text: message,
    };

    setMessages((prev) => [...prev, userMessage]);
    setThinking(true);

    // Simulate agent delay
    setTimeout(() => {
      const agentReply = {
        id: Date.now() + 1,
        sender: 'orchestrator',
        text: `🔁 Received: "${message}" — response coming soon...`,
      };

      setMessages((prev) => [...prev, agentReply]);
      setThinking(false);
    }, 1500);
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

          {/* Agent Log Thread */}
          <div className="flex-1 bg-gray-900 rounded-xl p-4 overflow-y-auto space-y-2">
            <AgentLogThread messages={messages} />
            {thinking && (
              <div className="text-left animate-pulse text-gray-500 italic mt-2">
                [ orchestrator is thinking... ]
              </div>
            )}
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
