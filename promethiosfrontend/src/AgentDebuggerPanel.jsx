import { useAgent } from './AgentContext';

export default function AgentDebuggerPanel() {
  const { agentLogs } = useAgent();

  if (!agentLogs || agentLogs.length === 0) return null;

  return (
    <div className="fixed bottom-4 left-4 w-[360px] max-h-[300px] overflow-y-auto bg-gray-950 border border-gray-800 rounded-xl shadow-xl p-4 z-50">
      <h3 className="text-sm font-semibold text-teal-400 mb-2">🧠 Agent Debugger</h3>
      <ul className="space-y-2 text-xs text-gray-300">
        {agentLogs
          .slice(-6)
          .reverse()
          .map((log, idx) => (
            <li key={idx} className="border-b border-gray-800 pb-2">
              <div>
                <strong>{log.agent}</strong> → {log.action}
              </div>
              {log.step && <div className="text-gray-400">step: {log.step}</div>}
              {log.score && <div className="text-yellow-400">score: {log.score}/10</div>}
              <div className="text-gray-500 text-[10px]">{log.timestamp}</div>
            </li>
          ))}
      </ul>
    </div>
  );
}
