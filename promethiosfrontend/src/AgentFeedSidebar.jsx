import { useAgent } from "./AgentContext";

const views = ["Chat", "Memory", "Actions", "Debug"];

export default function AgentFeedSidebar() {
  const { selectedTool, setSelectedTool } = useAgent();

  return (
    <div className="w-40 h-full bg-gray-950 border-l border-gray-800 flex flex-col p-4 space-y-4">
      <h2 className="text-sm text-gray-400 font-semibold uppercase tracking-wide">
        Modules
      </h2>

      {views.map((view) => (
        <button
          key={view}
          onClick={() => setSelectedTool(view)}
          className={`text-sm text-left px-2 py-1 rounded ${
            selectedTool === view
              ? "bg-gray-800 text-teal-400 font-semibold"
              : "text-gray-300 hover:bg-gray-800"
          }`}
        >
          {view}
        </button>
      ))}
    </div>
  );
}
