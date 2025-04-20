import { useState } from 'react';
import LoopStatusPanel from './LoopStatusPanel';
import InputBar from './InputBar';

function MainConsolePanel() {
  const [messages, setMessages] = useState([]);

  // Handler for new messages from InputBar
  const handleNewMessage = (message, file) => {
    const newMessage = {
      type: "operator_input",
      message,
      file: file ? file.name : null,
      timestamp: new Date().toISOString(),
    };
    
    // Add message to the list
    setMessages(prev => [...prev, newMessage]);
    
    // Log to console as required in the specs
    console.log(newMessage);
  };

  return (
    <div className="h-full bg-gray-900 border-r border-gray-800 w-full p-4 flex flex-col">
      <div className="border-b border-gray-800 pb-4 mb-4">
        <h2 className="text-lg font-semibold">Console</h2>
      </div>
      
      {/* Scrollable content area */}
      <div className="flex-grow overflow-y-auto mb-4">
        {/* Loop Status Panel */}
        <LoopStatusPanel />
        
        {/* Welcome message */}
        <div className="bg-gray-800 rounded-lg p-4 mb-4">
          <p className="text-gray-400">Welcome to Promethios Console</p>
          <p className="text-gray-400 mt-2">This is the main console panel where conversation threads will appear.</p>
        </div>
        
        {/* Message history */}
        {messages.map((msg, index) => (
          <div key={index} className="bg-gray-800/70 rounded-lg p-3 mb-3">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>Operator</span>
              <span>{new Date(msg.timestamp).toLocaleTimeString()}</span>
            </div>
            {msg.file && (
              <div className="mb-2 px-2 py-1 bg-gray-700 rounded inline-flex items-center">
                <span className="text-cyan-400 mr-1">📎</span>
                <span className="text-xs text-gray-300">{msg.file}</span>
              </div>
            )}
            <p className="text-white whitespace-pre-wrap">{msg.message}</p>
          </div>
        ))}
      </div>
      
      {/* Input bar fixed at bottom */}
      <InputBar onSubmit={handleNewMessage} />
    </div>
  );
}

export default MainConsolePanel;
