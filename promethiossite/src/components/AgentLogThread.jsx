import React from 'react';

export default function AgentLogThread({ messages }) {
  if (!messages.length) {
    return (
      <div className="text-center text-gray-500 italic py-12">
        [ Awaiting your first command... ]
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {messages.map((msg) => (
        <div key={msg.id} className={`w-full ${msg.sender === 'operator' ? 'text-right' : 'text-left'}`}>
          <div
            className={`inline-block px-4 py-2 rounded-xl ${
              msg.sender === 'operator'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-800 text-gray-200'
            }`}
          >
            {msg.text}
          </div>
        </div>
      ))}
    </div>
  );
}
