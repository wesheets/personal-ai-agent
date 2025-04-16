import React from 'react';
import { FiGrid, FiUser, FiTool, FiTarget, FiClock, FiArchive, FiSettings, FiHelpCircle } from 'react-icons/fi';

const SidebarItem = ({ icon: Icon, label }) => (
  <div className="flex items-center space-x-3 px-4 py-2 rounded-md hover:bg-gray-800 cursor-pointer">
    <Icon className="text-lg" />
    <span className="text-sm">{label}</span>
  </div>
);

export default function AgentSidebar() {
  return (
    <aside className="w-[260px] bg-gray-950 border-r border-gray-800 flex flex-col py-6 space-y-8 text-white">
      {/* SYSTEM */}
      <div>
        <h2 className="text-xs text-gray-500 px-4 mb-2 uppercase">System</h2>
        <SidebarItem icon={FiGrid} label="Orchestrator" />
      </div>

      {/* AGENTS */}
      <div>
        <h2 className="text-xs text-gray-500 px-4 mb-2 uppercase">Agents</h2>
        <SidebarItem icon={FiUser} label="HAL" />
        <SidebarItem icon={FiUser} label="ASH" />
        <SidebarItem icon={FiUser} label="NOVA" />
      </div>

      {/* MODULES */}
      <div className="flex-1">
        <h2 className="text-xs text-gray-500 px-4 mb-2 uppercase">Modules</h2>
        <SidebarItem icon={FiTarget} label="Goals / Threads" />
        <SidebarItem icon={FiTool} label="Tools" />
        <SidebarItem icon={FiClock} label="Checkpoints" />
        <SidebarItem icon={FiArchive} label="Archives" />
        <SidebarItem icon={FiSettings} label="Settings" />
        <SidebarItem icon={FiHelpCircle} label="Help" />
      </div>
    </aside>
  );
}
