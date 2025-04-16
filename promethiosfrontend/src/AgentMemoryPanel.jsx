export default function AgentMemoryPanel({ memories = [] }) {
  const grouped = memories.reduce((acc, mem) => {
    if (!acc[mem.agent]) acc[mem.agent] = [];
    acc[mem.agent].push(mem);
    return acc;
  }, {});

  return (
    <div className="w-80 h-full bg-gray-950 border-l border-gray-800 p-4 overflow-y-auto space-y-6">
      <h2 className="text-lg font-bold text-white">🧠 Agent Memory</h2>

      {Object.keys(grouped).map((agent) => (
        <div key={agent} className="space-y-2">
          <h3 className="text-teal-400 font-semibold border-b border-gray-800 pb-1">
            {agent.toUpperCase()}
          </h3>
          {grouped[agent].map((mem, idx) => (
            <div
              key={idx}
              className="bg-gray-800 p-2 rounded text-sm text-gray-200 whitespace-pre-wrap"
            >
              {mem.content}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
