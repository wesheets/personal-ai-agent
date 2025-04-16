import React from 'react';
import AgentSidebar from './components/AgentSidebar';
import ThemeToggle from './components/ThemeToggle';

export default function ControlRoom() {
  return (
    <div className="flex h-screen bg-black text-white overflow-hidden">
      {/* Left Sidebar */}
      <AgentSidebar />

      {/* Main Area (Chat + Logs) */}
      <main className="flex-1 flex flex-col overflow-y-auto p-6 space-y-6">
        <header className="text-center">
          <h1 className="text-3xl font-bold tracking-wide mb-2">🧠 Promethios Control Room</h1>
          <p className="text-sm text-gray-400">
            Operator interface connected. Awaiting input.
          </p>
        </header>

        {/* TODO: Chat feed goes here */}
        <section className="flex-1 bg-gray-900 rounded-xl p-4">
          <div className="text-gray-500 text-center">
            [ Chat stream will appear here... ]
          </div>
        </section>

        {/* TODO: Input bar will go here */}
      </main>

      {/* Theme toggle (floating) */}
      <ThemeToggle />
    </div>
  );
}
