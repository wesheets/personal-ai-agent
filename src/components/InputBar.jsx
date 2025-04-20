import { useState, useRef, useEffect } from 'react';

function InputBar({ onSubmit }) {
  const [message, setMessage] = useState('');
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);
  const containerRef = useRef(null);

  // Auto-resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(200, Math.max(40, textareaRef.current.scrollHeight))}px`;
    }
  }, [message]);

  // Handle text input changes
  const handleMessageChange = (e) => {
    setMessage(e.target.value);
  };

  // Handle file selection
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  // Handle file drop
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  // Handle drag enter
  const handleDragEnter = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  // Handle drag leave
  const handleDragLeave = (e) => {
    e.preventDefault();
    // Only set isDragging to false if we're leaving the container
    if (containerRef.current && !containerRef.current.contains(e.relatedTarget)) {
      setIsDragging(false);
    }
  };

  // Prevent default behavior for drag events
  const handleDragOver = (e) => {
    e.preventDefault();
  };

  // Handle file button click
  const handleFileButtonClick = () => {
    fileInputRef.current.click();
  };

  // Handle form submission
  const handleSubmit = () => {
    if (message.trim() || file) {
      // Call the onSubmit prop with message and file
      if (onSubmit) {
        onSubmit(message, file);
      }

      // Clear the form
      setMessage('');
      setFile(null);
      
      // Focus back on textarea
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
    }
  };

  // Handle key press (Enter to submit)
  const handleKeyPress = (e) => {
    // Submit on Enter without Shift key
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div 
      ref={containerRef}
      className={`mt-auto bg-gray-800 rounded-lg p-3 shadow-md border ${isDragging ? 'border-cyan-500 border-dashed' : 'border-gray-700'} transition-colors`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
    >
      {/* File preview */}
      {file && (
        <div className="mb-2 px-3 py-1 bg-gray-700 rounded flex items-center justify-between">
          <div className="flex items-center truncate">
            <span className="text-cyan-400 mr-2 flex-shrink-0">📎</span>
            <span className="text-sm text-gray-300 truncate">{file.name}</span>
          </div>
          <button 
            onClick={() => setFile(null)}
            className="text-gray-400 hover:text-white ml-2 flex-shrink-0"
            aria-label="Remove file"
          >
            ✕
          </button>
        </div>
      )}

      {/* Input area */}
      <div className="flex flex-col sm:flex-row sm:items-end">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={handleMessageChange}
          onKeyDown={handleKeyPress}
          placeholder="Type your instructions here..."
          className="w-full sm:flex-grow bg-gray-700 text-white rounded-lg px-3 py-2 min-h-[40px] resize-none focus:outline-none focus:ring-1 focus:ring-cyan-500"
          style={{ overflow: 'auto' }}
        />
        
        <div className="flex mt-2 sm:mt-0 sm:ml-2">
          {/* File upload button */}
          <button
            onClick={handleFileButtonClick}
            className="bg-gray-700 hover:bg-gray-600 text-cyan-400 rounded-lg p-2 mr-2 focus:outline-none"
            title="Upload file"
            aria-label="Upload file"
          >
            📎
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              className="hidden"
              aria-hidden="true"
            />
          </button>
          
          {/* Send button */}
          <button
            onClick={handleSubmit}
            className="bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg px-4 py-2 focus:outline-none flex-grow sm:flex-grow-0"
            aria-label="Send message"
          >
            Send
          </button>
        </div>
      </div>
      
      <div className="mt-1 text-xs text-gray-500">
        Press Enter to send, Shift+Enter for new line
      </div>
    </div>
  );
}

export default InputBar;
