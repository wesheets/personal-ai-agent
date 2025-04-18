import { useState } from 'react';
import { FiUpload, FiSend, FiX } from 'react-icons/fi';

export default function AgentInputBar({ onSend, replyTo, clearReply }) {
  const [input, setInput] = useState('');
  const [file, setFile] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSend(input);
    setInput('');
    setFile(null);
  };

  const handleFileChange = (e) => {
    const uploaded = e.target.files[0];
    if (uploaded) setFile(uploaded);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="w-full flex flex-col border-t border-gray-800 bg-black sticky bottom-0 z-10 px-4 py-3 space-y-2"
    >
      {/* Reply context */}
      {replyTo && (
        <div className="flex items-center justify-between text-xs text-gray-400 bg-gray-800 px-3 py-2 rounded">
          <span>↪ Replying to: <span className="italic text-gray-300">{replyTo.text?.slice(0, 60)}...</span></span>
          <button onClick={clearReply} title="Cancel reply" type="button">
            <FiX />
          </button>
        </div>
      )}

      {/* Input Row */}
      <div className="flex items-end space-x-2">
        <div className="flex-1">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your command..."
            rows={1}
            className="w-full bg-gray-900 text-white p-3 rounded-md resize-none border border-gray-700 pr-10"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          {file && (
            <div className="text-sm text-gray-400 mt-1">
              Attached: {file.name}
            </div>
          )}
        </div>

        {/* File Upload */}
        <label className="cursor-pointer">
          <input type="file" className="hidden" onChange={handleFileChange} />
          <div className="p-2 bg-gray-800 rounded-md hover:bg-gray-700">
            <FiUpload />
          </div>
        </label>

        {/* Send Button */}
        <button
          type="submit"
          className="p-2 bg-indigo-600 hover:bg-indigo-500 rounded-md text-white"
          title="Send"
        >
          <FiSend />
        </button>
      </div>
    </form>
  );
}
