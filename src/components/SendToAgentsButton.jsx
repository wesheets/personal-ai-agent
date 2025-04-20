import { useState } from 'react';
import ModifyPlanModal from './ModifyPlanModal';

function SendToAgentsButton({ loopId, loopPlan, onConfirm, onModify, onReject, visible = true }) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isModifyModalOpen, setIsModifyModalOpen] = useState(false);
  const [activeButton, setActiveButton] = useState(null);
  
  // Handle confirmation click (Approve)
  const handleConfirm = async () => {
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    setActiveButton('approve');
    
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
      setActiveButton(null);
    }
  };
  
  // Handle modify click
  const handleModifyClick = () => {
    setIsModifyModalOpen(true);
  };
  
  // Handle plan modification submission
  const handleModifySubmit = (modifiedPlan) => {
    setIsSubmitting(true);
    setActiveButton('modify');
    
    try {
      // Call the onModify callback with the modified plan
      if (onModify) {
        onModify(modifiedPlan);
      }
    } catch (error) {
      console.error('Error submitting modified plan:', error);
    } finally {
      setIsSubmitting(false);
      setActiveButton(null);
    }
  };
  
  // Handle rejection click
  const handleReject = async () => {
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    setActiveButton('reject');
    
    try {
      // Log to memory
      const memoryUpdate = {
        prompt_confirmation: {
          status: "rejected",
          timestamp: new Date().toISOString(),
          operator_action: "rejected loop plan due to misalignment with intent"
        }
      };
      
      console.log('Logging to PROJECT_MEMORY.prompt_confirmation:', memoryUpdate);
      
      // Call the onReject callback
      if (onReject) {
        onReject(loopId);
      }
    } catch (error) {
      console.error('Error rejecting plan:', error);
    } finally {
      setIsSubmitting(false);
      setActiveButton(null);
    }
  };
  
  if (!visible) return null;
  
  return (
    <div className="mt-2">
      <div className="flex space-x-2">
        {/* Approve Button */}
        <button
          onClick={handleConfirm}
          className="flex-1 bg-gray-800 hover:bg-gray-700 text-cyan-400 hover:text-cyan-300 border border-gray-700 hover:border-cyan-800 rounded-lg py-2 px-2 transition-colors shadow-md hover:shadow-[0_0_10px_rgba(6,182,212,0.2)] focus:outline-none focus:ring-2 focus:ring-cyan-600 focus:ring-opacity-50 font-medium flex items-center justify-center"
          disabled={isSubmitting}
        >
          {isSubmitting && activeButton === 'approve' ? (
            <span className="inline-flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-cyan-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </span>
          ) : (
            <>
              <span className="mr-1">✅</span>
              Approve
            </>
          )}
        </button>
        
        {/* Modify Button */}
        <button
          onClick={handleModifyClick}
          className="flex-1 bg-gray-800 hover:bg-gray-700 text-yellow-400 hover:text-yellow-300 border border-gray-700 hover:border-yellow-800 rounded-lg py-2 px-2 transition-colors shadow-md hover:shadow-[0_0_10px_rgba(234,179,8,0.2)] focus:outline-none focus:ring-2 focus:ring-yellow-600 focus:ring-opacity-50 font-medium flex items-center justify-center"
          disabled={isSubmitting}
        >
          {isSubmitting && activeButton === 'modify' ? (
            <span className="inline-flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-yellow-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </span>
          ) : (
            <>
              <span className="mr-1">📝</span>
              Modify
            </>
          )}
        </button>
        
        {/* Reject Button */}
        <button
          onClick={handleReject}
          className="flex-1 bg-gray-800 hover:bg-gray-700 text-red-400 hover:text-red-300 border border-gray-700 hover:border-red-800 rounded-lg py-2 px-2 transition-colors shadow-md hover:shadow-[0_0_10px_rgba(239,68,68,0.2)] focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-opacity-50 font-medium flex items-center justify-center"
          disabled={isSubmitting}
        >
          {isSubmitting && activeButton === 'reject' ? (
            <span className="inline-flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-red-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </span>
          ) : (
            <>
              <span className="mr-1">❌</span>
              Reject
            </>
          )}
        </button>
      </div>
      
      {/* Modify Plan Modal */}
      <ModifyPlanModal
        isOpen={isModifyModalOpen}
        onClose={() => setIsModifyModalOpen(false)}
        loopPlan={loopPlan}
        onSubmit={handleModifySubmit}
      />
    </div>
  );
}

export default SendToAgentsButton;
