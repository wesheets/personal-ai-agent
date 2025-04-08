// src/components/MemoryFeed.jsx
import MemoryLog from './MemoryLog'

export default function MemoryFeed({ memories }) {
  return (
    <div className="p-4 space-y-3">
      <h2 className="text-xl text-white mb-4">Memory Feed</h2>
      {memories.map(memory => (
        <MemoryLog key={memory.id} memory={memory} />
      ))}
    </div>
  );
}
