import React, { useState } from 'react';
import { FiCopy, FiCheckCircle } from 'react-icons/fi';

export default function AgentLogThread({ messages, onReply }) {
  const [resolvedMessages, setResolvedMessages] = useState([]);
  const [copiedId, setCopiedId] = useState(null);

  const handleCopy = async (text, id) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 1500);
    } catch (err) {
      console.error('Copy failed', err);
    }
  };

  const toggleResolved = (id) => {
    setResolvedMessages((prev) =>
      prev.includes(id) ? prev.filter((m) => m !== id) : [...prev, id]
    );
  };

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
        const isResolved = resolvedMessages.includes(msg.id);

        return (
          <div
            key={msg.id}
            className={`w-full relative group ${
              msg.sender === 'operator' ? 'text-right' : 'text-left'
            } ${isReply ? 'ml-5 border-l-2 border-gray-700 pl-4' : ''}`}
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
              } ${isResolved ? 'opacity-50 line-through' : ''}`}
            >
              {msg.text}
            </div>

            <div className="text-xs text-gray-500 mt-1 flex gap-3 items-center opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <span className="cursor-pointer hover:text-indigo-400" onClick={() => onReply(msg.id)}>
                Reply
              </span>
              <span className="cursor-pointer hover:text-green-400" onClick={() => toggleResolved(msg.id)}>
                <FiCheckCircle className="inline mr-1" />
                {isResolved ? 'Unresolve' : 'Mark Resolved'}
              </span>
              <span className="cursor-pointer hover:text-blue-400" onClick={() => handleCopy(msg.text, msg.id)}>
                <FiCopy className="inline mr-1" />
                {copiedId === msg.id ? 'Copied!' : 'Copy'}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
