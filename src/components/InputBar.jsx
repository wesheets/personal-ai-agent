import { useState, useRef, useEffect } from 'react';

function InputBar({ onSubmit }) {
  const [message, setMessage] = useState('');
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
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

  // POST to API and handle orchestrator reflection
  const postToOrchestrator = async (messageText, fileObj) => {
    setIsSubmitting(true);
    
    try {
      // Create payload according to requirements
      const payload = {
        project_id: "lifetree_001", // This would be dynamic in a real implementation
        message: messageText,
        file: fileObj ? fileObj.name : null
      };
      
      console.log('POST /api/operator/prompt', payload);
      
      // In a real implementation, this would be an actual API call:
      // const response = await fetch('/api/operator/prompt', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(payload)
      // });
      // const data = await response.json();
      
      // Generate a new loop ID (25 for this phase)
      const loopId = 25;
      
      // Mock orchestrator reflection response as specified in requirements
      const orchestratorResponse = {
        role: "orchestrator",
        agent: "orchestrator",
        message: "Understood. I will run Loop 25 with HAL → NOVA → CRITIC to build the base layout.",
        loop_plan: {
          loop_id: loopId,
          agents: ["hal", "nova", "critic"],
          goals: ["scaffold UI", "add logic", "validate structure"],
          planned_files: ["src/components/Timeline.jsx", "theme.json"]
        },
        timestamp: new Date().toISOString(),
        loop: loopId
      };
      
      // Mock orchestrator confirmation prompt as specified in requirements
      const orchestratorConfirmationPrompt = {
        role: "orchestrator",
        agent: "orchestrator",
        message: `Loop plan ready: ${orchestratorResponse.loop_plan.agents.join(' → ')}. Shall I proceed?`,
        loop_plan: orchestratorResponse.loop_plan,
        requires_confirmation: true,
        timestamp: new Date().toISOString(),
        loop: loopId
      };
      
      // Log the operator prompt to memory
      const operatorPrompt = {
        message: messageText,
        timestamp: new Date().toISOString(),
        used_in_loop: orchestratorResponse.loop_plan.loop_id
      };
      
      console.log('Logging to PROJECT_MEMORY.operator_prompts:', operatorPrompt);
      
      // Log the prompt confirmation to memory
      const promptConfirmation = {
        prompt_confirmation: {
          plan_id: `loop_${loopId}`,
          status: "awaiting_operator",
          timestamp: new Date().toISOString()
        }
      };
      
      console.log('Logging to PROJECT_MEMORY.prompt_confirmation:', promptConfirmation);
      
      // Return the operator message, orchestrator response, and confirmation prompt
      return {
        operatorMessage: {
          role: "operator",
          agent: "operator",
          message: messageText,
          file: fileObj ? fileObj.name : null,
          timestamp: new Date().toISOString(),
          loop: loopId
        },
        orchestratorResponse,
        orchestratorConfirmationPrompt
      };
    } catch (error) {
      console.error('Error posting to orchestrator:', error);
      return null;
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle form submission
  const handleSubmit = async () => {
    if (message.trim() || file) {
      // Post to orchestrator and get response
      const result = await postToOrchestrator(message, file);
      
      if (result && onSubmit) {
        // Call the onSubmit prop with all messages
        onSubmit(
          result.operatorMessage, 
          result.orchestratorResponse, 
          result.orchestratorConfirmationPrompt
        );
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
          disabled={isSubmitting}
        />
        
        <div className="flex mt-2 sm:mt-0 sm:ml-2">
          {/* File upload button */}
          <button
            onClick={handleFileButtonClick}
            className="bg-gray-700 hover:bg-gray-600 text-cyan-400 rounded-lg p-2 mr-2 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
            title="Upload file"
            aria-label="Upload file"
            disabled={isSubmitting}
          >
            📎
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              className="hidden"
              aria-hidden="true"
              disabled={isSubmitting}
            />
          </button>
          
          {/* Send button */}
          <button
            onClick={handleSubmit}
            className="bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg px-4 py-2 focus:outline-none flex-grow sm:flex-grow-0 disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Send message"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <span className="inline-flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Sending
              </span>
            ) : "Send"}
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
