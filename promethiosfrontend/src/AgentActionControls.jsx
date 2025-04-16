export default function AgentActionControls({ onRetry, onRewrite, onRespond }) {
  return (
    <div className="flex space-x-3 mt-3">
      <button
        onClick={onRetry}
        className="text-xs bg-gray-800 hover:bg-gray-700 text-white px-3 py-1 rounded"
      >
        🔁 Retry
      </button>
      <button
        onClick={onRewrite}
        className="text-xs bg-teal-600 hover:bg-teal-500 text-white px-3 py-1 rounded"
      >
        ✏️ Rewrite
      </button>
      <button
        onClick={onRespond}
        className="text-xs bg-blue-600 hover:bg-blue-500 text-white px-3 py-1 rounded"
      >
        💬 Respond
      </button>
    </div>
  );
}
