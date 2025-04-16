import { useState } from 'react';
import { Terminal } from 'lucide-react';

export default function TerminalDrawer() {
  const [open, setOpen] = useState(false);

  return (
    <div className="fixed bottom-4 right-4 z-40">
      <button
        onClick={() => setOpen(!open)}
        className="bg-black text-white border border-gray-600 px-4 py-2 rounded-lg shadow hover:bg-gray-800 transition"
      >
        <Terminal size={16} className="inline-block mr-2" />
        {open ? 'Close Sandbox' : 'Open Sandbox'}
      </button>

      {open && (
        <div className="fixed bottom-16 right-4 w-[480px] h-[300px] bg-gray-900 border border-gray-700 rounded-lg shadow-lg p-4 overflow-y-auto">
          <p className="text-sm text-gray-400 mb-2">🧪 Agent Sandbox Terminal</p>
          <pre className="text-xs text-gray-300 whitespace-pre-wrap">
            {`• HAL requested /plan/scope
• ASH generated /docs/onboarding
• CRITIC scored last output 8/10
• Waiting for operator input...`}
          </pre>
        </div>
      )}
    </div>
  );
}
