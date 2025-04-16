import { useEffect, useState } from "react";
import AgentSidebar from "./AgentSidebar";
import AgentOutputCard from "./AgentOutputCard";
import CriticOutputCard from "./CriticOutputCard";
import AgentChatPanel from "./AgentChatPanel";
import TerminalDrawer from "./TerminalDrawer";
import ThemeToggle from "./ThemeToggle";

export default function ControlRoom() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Mocked data (swap with fetch later)
    setTimeout(() => {
      setData({
        project_id: "founder-stack",
        chain_id: "latest",
        outputs: {
          hal: "Scoped MVP: login, dashboard, Stripe billing integration.",
          ash: "Created onboarding documentation and product summary.",
          nova: "Suggested layout: left sidebar, top nav, card dashboard.",
          critic: {
            score: 8,
            feedback: "Solid execution. Could use real-time error boundaries and loading states."
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
            Project:
