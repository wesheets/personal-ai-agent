import React, { useState } from 'react';
import AgentSidebar from './components/AgentSidebar';
import AgentInputBar from './components/AgentInputBar';
import AgentLogThread from './components/AgentLogThread';
import RightPanel from './components/RightPanel';
import ThemeToggle from './components/ThemeToggle';
import { callOrchestrator } from './api/callOrchestrator';

export default function ControlRoom() {
  const [messages, setMessages] = useState([]);
  const [thinking, setThinking] = useState(false);
  const [replyTo, setReplyTo] = useState(null);

  const handleSend = async (message) => {
    const userMessage = {
      id: Date.now(),
      sender: 'operator',
      text: message,
      replyTo: replyTo, // link to parent if replying
    };

    setMessages((prev) => [...prev, userMessage]);
    setThinking(true);
    setReplyTo(null); // reset reply after send

    // Simulated agent response (ORCHESTRATOR call is pre-wired but inactive)
    setTimeout(() => {
      const agentReply = {
        id: Date.now() + 1,
        sender: 'orchestrator',
        text: `🔁 Received: "${message}" — response coming soon...`,
        replyTo: userMessage.id, // reply to user's message
      };

      setMessages((prev) => [...prev, agentReply]);
      setThinking(false);
    }, 1500);

    // Uncomment this block to activate real backend
    /*
    try {
      const agentResponse = await callOrchestrator(message);
      const agentReply = {
        id: Date.now() + 1,
        sender: 'orchestrator',
        text: agentResponse,
        replyTo: userMessage.id,
      };
      setMessages((prev) => [...prev, agentReply]);
    } catch (err) {
      setMessages((prev) => [...prev, {
        id: Date.now() + 1,
        sender: 'system',
        text: '[Error: Unable to reach ORCHESTRATOR]',
        replyTo: userMessage.id,
      }]);
    } finally {
      setThinking(false);
    }
    */
  };

  return (
    <div className="flex h-screen bg-black text-white overflow-hidden">
      <AgentSidebar />

      <main className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 flex flex-col p-6 space-y-6 overflow-y-auto">
          <header className="text-center">
            <h1 className="text-3xl font-bold tracking-wide mb-2">🧠 Promethios Control Room</h1>
            <p className="text-sm text-gray-400">
              Operator interface connected. Awaiting input.
            </p>
          </header>

          <div className="flex-1 bg-gray-900 rounded-xl p-4 overflow-y-auto space-y-2">
            <AgentLogThread messages={messages} onReply={setReplyTo} />
            {thinking && (
              <div className="text-left animate-pulse text-gray-500 italic mt-2">
                [ orchestrator is thinking... ]
              </div>
            )}
          </div>
        </div>

        <AgentInputBar onSend={handleSend} replyTo={replyTo} clearReply={() => setReplyTo(null)} />
      </main>

      <RightPanel visible={thinking} />
      <ThemeToggle />
    </div>
  );
}
