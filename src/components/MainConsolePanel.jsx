import { useState } from 'react';
import LoopStatusPanel from './LoopStatusPanel';
import InputBar from './InputBar';
import ChatMessageFeed from './ChatMessageFeed';
import OverrideControls from './OverrideControls';

function MainConsolePanel({ activeTab }) {
  const [messages, setMessages] = useState([]);
  
  // Handler for new messages from InputBar
  const handleNewMessage = (message, file) => {
    const newMessage = {
      role: "operator",
      agent: "operator",
      message,
      file: file ? file.name : null,
      timestamp: new Date().toISOString(),
      loop: 23, // This would be dynamic in a real implementation
    };
    
    // Add message to the list
    setMessages(prev => [...prev, newMessage]);
    
    // Log to console as required in the specs
    console.log(newMessage);
  };

  // Determine what to render based on active tab
  const renderContent = () => {
    if (activeTab === 'tools') {
      return <OverrideControls />;
    } else {
      return (
        <>
          {/* Loop Status Panel */}
          <LoopStatusPanel />
          
          {/* Welcome message - only show if no messages */}
          {messages.length === 0 && (
            <div className="bg-gray-800 rounded-lg p-4 mb-4">
              <p className="text-gray-400">Welcome to Promethios Console</p>
              <p className="text-gray-400 mt-2">This is the main console panel where conversation threads will appear.</p>
            </div>
          )}
          
          {/* Chat Message Feed */}
          <div className="flex-grow">
            <ChatMessageFeed userMessages={messages} />
          </div>
        </>
      );
    }
  };

  return (
    <div className="h-full bg-gray-900 border-r border-gray-800 w-full p-4 flex flex-col">
      <div className="border-b border-gray-800 pb-4 mb-4">
        <h2 className="text-lg font-semibold">Console</h2>
      </div>
      
      {/* Scrollable content area */}
      <div className="flex-grow overflow-y-auto mb-4 flex flex-col">
        {renderContent()}
      </div>
      
      {/* Input bar fixed at bottom - only show when not in tools tab */}
      {activeTab !== 'tools' && <InputBar onSubmit={handleNewMessage} />}
    </div>
  );
}

export default MainConsolePanel;
