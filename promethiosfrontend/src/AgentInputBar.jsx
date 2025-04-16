import { useState } from 'react';

export default function AgentInputBar({ onSend }) {
  const [value, setValue] = useState('');

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend(value);
      setValue('');
    }
  }

  return (
    <div className="border-t border-gray-700 p-4 bg-black sticky bottom-0 z-10">
      <textarea
        rows={2}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type a command or ask an agent..."
        className="w-full bg-gray-800 text-white rounded-lg p-3 text-sm resize-none outline-none focus:ring-2 focus:ring-teal-500"
      />
    </div>
  );
}
