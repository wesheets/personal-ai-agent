import React from 'react';

export default function AgentLogThread({ messages, onReply }) {
  if (!messages.length) {
    return (
      <div className="text-center text-gray-500 italic py-12">
        [ Awaiting your first command... ]
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {messages.map((msg) => {
        const isReply = !!msg.replyTo;
        const parent = messages.find((m) => m.id === msg.replyTo);

        return (
          <div
            key={msg.id}
            className={`w-full ${msg.sender === 'operator' ? 'text-right' : 'text-left'} ${
              isReply ? 'ml-5 border-l-2 border-gray-700 pl-4' : ''
            }`}
          >
            {isReply && parent && (
              <div className="text-xs text-gray-500 italic mb-1">
                ↪ replying to: “{parent.text.slice(0, 40)}...”
              </div>
            )}
            <div
              className={`inline-block px-4 py-2 rounded-xl ${
                msg.sender === 'operator'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-800 text-gray-200'
              }`}
            >
              {msg.text}
            </div>
            <div className="text-xs text-gray-500 mt-1 cursor-pointer hover:underline" onClick={() => onReply(msg.id)}>
              Reply
            </div>
          </div>
        );
      })}
    </div>
  );
}
