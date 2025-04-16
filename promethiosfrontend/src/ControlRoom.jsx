import { useEffect, useState } from "react";
import AgentOutputCard from "./AgentOutputCard";
import CriticOutputCard from "./CriticOutputCard";

export default function ControlRoom() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/orchestrator/status?project_id=founder-stack&chain_id=latest")
      .then((res) => res.json())
      .then((result) => {
        setData(result);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8 text-gray-500">Loading agent thread...</div>;

  return (
    <div className="max-w-4xl mx-auto p-6 text-white">
      <h1 className="text-3xl font-bold mb-6 text-center tracking-wide">🧠 Promethios Control Room</h1>
      <p className="text-sm text-gray-400 mb-4 text-center">
        Project: <strong>{data.project_id}</strong> / Chain: <strong>{data.chain_id}</strong>
      </p>

      <AgentOutputCard title="HAL – Product Scope" content={data.outputs?.hal} />
      <AgentOutputCard title="ASH – Docs & Onboarding" content={data.outputs?.ash} />
      <AgentOutputCard title="NOVA – UI Layouts" content={data.outputs?.nova} />
      <CriticOutputCard score={data.outputs?.critic?.score} feedback={data.outputs?.critic?.feedback} />
    </div>
  );
}
