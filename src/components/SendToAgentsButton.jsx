import { useState } from 'react';

function SendToAgentsButton({ loopId, onConfirm, visible = true }) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Handle confirmation click
  const handleConfirm = async () => {
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    
    try {
      // Create payload according to requirements
      const payload = {
        project_id: "lifetree_001", // This would be dynamic in a real implementation
        confirmed_loop: loopId
      };
      
      console.log('POST /api/orchestrator/confirm-plan', payload);
      
      // In a real implementation, this would be an actual API call:
      // const response = await fetch('/api/orchestrator/confirm-plan', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(payload)
      // });
      // const data = await response.json();
      
      // Log to memory
      const memoryUpdate = {
        loop_plan: {
          confirmed: true,
          confirmed_by: "operator",
          confirmed_at: new Date().toISOString()
        }
      };
      
      console.log('Logging to PROJECT_MEMORY.loop_plan:', memoryUpdate);
      
      // Call the onConfirm callback
      if (onConfirm) {
        onConfirm(loopId);
      }
    } catch (error) {
      console.error('Error confirming plan:', error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  if (!visible) return null;
  
  return (
    <div className="mt-2">
      <button
        onClick={handleConfirm}
        className="w-full bg-gray-800 hover:bg-gray-700 text-cyan-400 hover:text-cyan-300 border border-gray-700 hover:border-cyan-800 rounded-lg py-2 px-4 transition-colors shadow-md hover:shadow-[0_0_10px_rgba(6,182,212,0.2)] focus:outline-none focus:ring-2 focus:ring-cyan-600 focus:ring-opacity-50 font-medium flex items-center justify-center"
        disabled={isSubmitting}
      >
        {isSubmitting ? (
          <span className="inline-flex items-center">
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-cyan-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Processing...
          </span>
        ) : (
          <>
            <span className="mr-2">🚀</span>
            Send to Agents
          </>
        )}
      </button>
    </div>
  );
}

export default SendToAgentsButton;
