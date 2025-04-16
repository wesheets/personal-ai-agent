const loop = ["HAL", "ASH", "NOVA"];

export default function AgentLoopVisualizer({ activeAgent = "HAL" }) {
  return (
    <div className="flex items-center justify-center gap-6 py-4">
      {loop.map((agent) => {
        const isActive = agent === activeAgent;
        return (
          <div key={agent} className="flex flex-col items-center">
            <div
              className={`w-4 h-4 rounded-full mb-1 ${
                isActive ? "bg-teal-400 animate-pulse" : "bg-gray-700"
              }`}
            ></div>
            <span
              className={`text-xs tracking-wide ${
                isActive ? "text-teal-400 font-bold" : "text-gray-400"
              }`}
            >
              {agent}
            </span>
          </div>
        );
      })}
    </div>
  );
}
