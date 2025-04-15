import { useState } from "react";
import { BrainCog, Terminal, ScrollText, LayoutDashboard, Wand2 } from "lucide-react";

const tools = [
  { name: "Memory", icon: BrainCog },
  { name: "Sandbox", icon: Terminal },
  { name: "CRITIC", icon: ScrollText },
  { name: "UI", icon: LayoutDashboard },
  { name: "Debug", icon: Wand2 },
];

export default function AgentSidebar({ onSelectTool }) {
  const [active, setActive] = useState("Memory");

  return (
    <div className="h-full w-20 bg-gray-950 border-r border-gray-800 flex flex-col items-center py-4 space-y-6">
      {tools.map(({ name, icon: Icon }) => (
        <button
          key={name}
          onClick={() => {
            setActive(name);
            onSelectTool?.(name);
          }}
          className={`p-2 rounded-lg hover:bg-gray-800 ${
            active === name ? "bg-gray-800 text-teal-400" : "text-gray-400"
          }`}
        >
          <Icon size={22} />
        </button>
      ))}
    </div>
  );
}
