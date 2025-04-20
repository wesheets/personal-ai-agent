import { useState } from 'react';
import LoopStatusPanel from './LoopStatusPanel';
import InputBar from './InputBar';
import ChatMessageFeed from './ChatMessageFeed';
import OverrideControls from './OverrideControls';
import SendToAgentsButton from './SendToAgentsButton';

function MainConsolePanel({ activeTab }) {
  const [messages, setMessages] = useState([]);
  const [orchestratorData, setOrchestratorData] = useState(null);
  const [isThinking, setIsThinking] = useState(false);
  const [pendingConfirmation, setPendingConfirmation] = useState(false);
  const [executionStarted, setExecutionStarted] = useState(false);
  
  // Handler for plan confirmation
  const handlePlanConfirm = (loopId) => {
    // Create a confirmation message from the orchestrator
    const confirmationMessage = {
      role: "orchestrator",
      agent: "orchestrator",
      message: "Plan confirmed. Executing loop with agents now...",
      timestamp: new Date().toISOString(),
      loop: loopId,
      execution_started: true
    };
    
    // Add the confirmation message to the chat
    setMessages(prev => [...prev, confirmationMessage]);
    
    // Update state to indicate execution has started
    setExecutionStarted(true);
    setPendingConfirmation(false);
    
    // In a real implementation, this would trigger the actual execution
    console.log('Execution started for loop:', loopId);
  };
  
  // Handler for new messages from InputBar
  const handleNewMessage = async (operatorMessage, orchestratorResponse, orchestratorConfirmationPrompt) => {
    // First add the operator message
    setMessages(prev => [...prev, operatorMessage]);
    
    // Show thinking state
    setIsThinking(true);
    
    // Simulate a delay for the orchestrator "thinking"
    setTimeout(() => {
      // Add the orchestrator response
      setMessages(prev => [...prev, orchestratorResponse]);
      
      // Update orchestrator data for the sandbox
      setOrchestratorData({
        loop: orchestratorResponse.loop_plan.loop_id,
        last_agent: "operator",
        next_agent: orchestratorResponse.loop_plan.agents[0],
        reason: orchestratorResponse.message,
        timestamp: orchestratorResponse.timestamp,
        loop_plan: orchestratorResponse.loop_plan
      });
      
      // End thinking state
      setIsThinking(false);
      
      // After a short delay, add the confirmation prompt
      setTimeout(() => {
        // Add the confirmation prompt
        setMessages(prev => [...prev, orchestratorConfirmationPrompt]);
        
        // Set pending confirmation state
        setPendingConfirmation(true);
        setExecutionStarted(false);
      }, 1000); // 1 second delay for visual effect
    }, 1500); // 1.5 second delay for visual effect
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
            <ChatMessageFeed 
              userMessages={messages} 
              isThinking={isThinking}
            />
          </div>
          
          {/* Send To Agents Button - only show when there's a pending confirmation and execution hasn't started */}
          {pendingConfirmation && !executionStarted && orchestratorData && (
            <div className="mt-4 mb-4 mx-auto max-w-md">
              <SendToAgentsButton 
                loopId={orchestratorData.loop}
                onConfirm={handlePlanConfirm}
                visible={true}
              />
            </div>
          )}
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
      {activeTab !== 'tools' && (
        <InputBar 
          onSubmit={handleNewMessage} 
        />
      )}
    </div>
  );
}

export default MainConsolePanel;
