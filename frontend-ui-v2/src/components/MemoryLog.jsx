// src/components/MemoryLog.jsx
export default function MemoryLog({ memory }) {
  return (
    <div className="p-4 mb-2 border border-gray-700 rounded text-white bg-gray-800">
      <div className="text-sm text-gray-400">{memory.timestamp} • {memory.type.toUpperCase()}</div>
      <div className="text-base mt-1">{memory.content}</div>
      <div className="text-xs mt-2 text-gray-500">Tags: {memory.tags.join(', ')}</div>
    </div>
  );
}
