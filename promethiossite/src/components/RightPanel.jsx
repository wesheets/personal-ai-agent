import React from 'react';

export default function RightPanel({ visible }) {
  if (!visible) return null;

  return (
    <aside className="w-[280px] bg-gray-950 border-l border-gray-800 p-4 flex flex-col space-y-4">
      <div className="text-xs text-gray-400 uppercase">Status</div>
      <div className="text-sm bg-gray-800 p-2 rounded text-green-400 font-mono">Executing...</div>

      <div className="text-xs text-gray-400 uppercase">Last Memory</div>
      <div className="text-sm bg-gray-800 p-2 rounded text-gray-300">
        “HAL initialized vertical scaffolding for SaaS deployment.”
      </div>

      <div className="text-xs text-gray-400 uppercase">Active Tool</div>
      <div className="text-sm bg-gray-800 p-2 rounded text-indigo-400 font-mono">file_writer.py</div>

      <div className="text-xs text-gray-400 uppercase">Toolkit</div>
      <ul className="text-sm text-gray-300 list-disc ml-5 space-y-1">
        <li>file_writer.py</li>
        <li>vercel_deploy.py</li>
        <li>snapshot.py</li>
      </ul>

      <div className="text-xs text-gray-400 uppercase">Reflection</div>
      <div className="text-sm bg-gray-800 p-2 rounded italic text-gray-400">
        “System confidence in output: moderate. Loop completion likely.”
      </div>
    </aside>
  );
}
