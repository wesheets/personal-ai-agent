import { useState, useEffect } from 'react';

function ModifyPlanModal({ isOpen, onClose, loopPlan, onSubmit }) {
  const [agents, setAgents] = useState('');
  const [goals, setGoals] = useState('');
  const [files, setFiles] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Initialize form values when modal opens or loopPlan changes
  useEffect(() => {
    if (loopPlan) {
      setAgents(loopPlan.agents.join(' → '));
      setGoals(loopPlan.goals.join(', '));
      setFiles(loopPlan.planned_files.join('\n'));
    }
  }, [loopPlan, isOpen]);
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    
    try {
      // Parse the input values
      const agentList = agents.split('→').map(agent => agent.trim());
      const goalList = goals.split(',').map(goal => goal.trim());
      const fileList = files.split('\n').filter(file => file.trim() !== '').map(file => file.trim());
      
      // Create the modified plan
      const modifiedPlan = {
        ...loopPlan,
        agents: agentList,
        goals: goalList,
        planned_files: fileList
      };
      
      // Log to memory
      const memoryUpdate = {
        prompt_confirmation: {
          status: "modified",
          timestamp: new Date().toISOString(),
          operator_action: "modified loop plan with updated agents, goals, or files"
        },
        loop_plan_override: modifiedPlan
      };
      
      console.log('Logging to PROJECT_MEMORY:', memoryUpdate);
      
      // Call the onSubmit callback with the modified plan
      if (onSubmit) {
        onSubmit(modifiedPlan);
      }
      
      // Close the modal
      onClose();
    } catch (error) {
      console.error('Error modifying plan:', error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // If modal is not open, don't render anything
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-lg shadow-xl border border-gray-700 w-full max-w-xl">
        {/* Modal header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700">
          <div className="flex items-center">
            <span className="text-yellow-400 mr-2">📝</span>
            <h2 className="text-lg font-medium text-white">Modify Loop Plan</h2>
          </div>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white"
            aria-label="Close"
          >
            ✕
          </button>
        </div>
        
        {/* Modal content */}
        <form onSubmit={handleSubmit}>
          <div className="p-4">
            {/* Agent sequence */}
            <div className="mb-4">
              <label htmlFor="agents" className="block text-sm font-medium text-gray-300 mb-2">
                Agent Sequence
              </label>
              <input
                id="agents"
                type="text"
                value={agents}
                onChange={(e) => setAgents(e.target.value)}
                className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-yellow-500"
                placeholder="HAL → NOVA → CRITIC"
              />
              <p className="mt-1 text-xs text-gray-500">Separate agents with → (arrow)</p>
            </div>
            
            {/* Goals */}
            <div className="mb-4">
              <label htmlFor="goals" className="block text-sm font-medium text-gray-300 mb-2">
                Loop Goals
              </label>
              <input
                id="goals"
                type="text"
                value={goals}
                onChange={(e) => setGoals(e.target.value)}
                className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-yellow-500"
                placeholder="scaffold UI, add logic, validate structure"
              />
              <p className="mt-1 text-xs text-gray-500">Separate goals with commas</p>
            </div>
            
            {/* Planned files */}
            <div className="mb-4">
              <label htmlFor="files" className="block text-sm font-medium text-gray-300 mb-2">
                Planned Files
              </label>
              <textarea
                id="files"
                value={files}
                onChange={(e) => setFiles(e.target.value)}
                className="w-full bg-gray-700 text-white rounded-lg px-3 py-2 min-h-[100px] focus:outline-none focus:ring-2 focus:ring-yellow-500"
                placeholder="src/components/Timeline.jsx
theme.json"
              />
              <p className="mt-1 text-xs text-gray-500">One file per line</p>
            </div>
          </div>
          
          {/* Modal footer */}
          <div className="px-4 py-3 border-t border-gray-700 flex justify-end">
            <button
              type="button"
              onClick={onClose}
              className="bg-gray-700 hover:bg-gray-600 text-white rounded-lg px-4 py-2 mr-2 focus:outline-none"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-yellow-700 hover:bg-yellow-600 text-white rounded-lg px-4 py-2 focus:outline-none flex items-center"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <span className="inline-flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Saving...
                </span>
              ) : (
                "Save Changes"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ModifyPlanModal;
