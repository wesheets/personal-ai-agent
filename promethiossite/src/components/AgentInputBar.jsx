import { useState } from 'react';
import { FiUpload } from 'react-icons/fi';

export default function AgentInputBar({ onSend }) {
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
    <form onSubmit={handleSubmit} className="w-full flex items-end space-x-2 px-4 py-3 border-t border-gray-800 bg-black sticky bottom-0 z-10">
      <div className="flex-1">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your command..."
          rows={1}
          className="w-full bg-gray-900 text-white p-3 rounded-md resize-none border border-gray-700"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) handleSubmit(e);
          }}
        />
        {file && (
          <div className="text-sm text-gray-400 mt-1">
            Attached: {file.name}
          </div>
        )}
      </div>

      <label className="cursor-pointer">
        <input
          type="file"
          className="hidden"
          onChange={handleFileChange}
        />
        <div className="p-2 bg-gray-800 rounded-md hover:bg-gray-700">
          <FiUpload />
        </div>
      </label>
    </form>
  );
}
