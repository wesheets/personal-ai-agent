import { useEffect, useState } from 'react';

import AgentSidebar from './AgentSidebar';
import AgentOutputCard from './AgentOutputCard';
import CriticOutputCard from './CriticOutputCard';
import AgentChatPanel from './AgentChatPanel';
import AgentInputBar from './AgentInputBar';
import TerminalDrawer from './TerminalDrawer';
import ThemeToggle from './ThemeToggle';
import SystemStatusPanel from './SystemStatusPanel';
import SystemSummaryPanel from './SystemSummaryPanel';

export default function ControlRoom() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const projectId = 'founder-stack'; // Default project ID

  useEffect(() => {
    // Simulate agent output for now
    setTimeout(() => {
      setData({
        project_id: projectId,
        chain_id: 'latest',
        outputs: {
          hal: 'Scoped MVP: login, dashboard, Stripe billing integration.',
          ash: 'Created onboarding documentation and product summary.',
          nova: 'Suggested layout: left sidebar, top nav, card dashboard.',
          critic: {
            score: 8,
            feedback: 'Solid execution. Could use real-time error boundaries and loading states.'
          }
        }
      });
      setLoading(false);
    }, 1000);
  }, []);

  if (loading) return <div className="p-8 text-gray-400">Loading agent thread...</div>;

  return (
    <div className="flex h-screen bg-black text-white overflow-hidden">
      <AgentSidebar />

      <main className="flex-1 flex flex-col overflow-y-auto p-6 space-y-6">
        <header className="text-center">
          <h1 className="text-3xl font-bold tracking-wide mb-2">🧠 Promethios Control Room</h1>
          <p className="text-sm text-gray-400">
            Project: <strong>{data.project_id}</strong> / Chain: <strong>{data.chain_id}</strong>
          </p>
        </header>

        {/* Ground Control Integration - System Status and Summary Panels */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <SystemStatusPanel projectId={data.project_id} />
          <SystemSummaryPanel projectId={data.project_id} />
        </div>

        <section className="space-y-4">
          <AgentOutputCard title="HAL – Product Scope" content={data.outputs.hal} />
          <AgentOutputCard title="ASH – Docs & Onboarding" content={data.outputs.ash} />
          <AgentOutputCard title="NOVA – UI Layouts" content={data.outputs.nova} />
          <CriticOutputCard
            score={data.outputs.critic.score}
            feedback={data.outputs.critic.feedback}
          />
        </section>

        <section className="flex-1 min-h-[200px] mt-6">
          <AgentChatPanel />
          <div className="mt-4">
            <AgentInputBar />
          </div>
        </section>
      </main>

      <ThemeToggle />
      <TerminalDrawer />
    </div>
  );
}
