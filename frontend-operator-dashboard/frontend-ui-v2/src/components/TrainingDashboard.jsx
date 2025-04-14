// src/components/TrainingDashboard.jsx
import { useState, useEffect } from 'react';
import { useAgentTraining } from '../hooks/useAgentTraining';
import { useMemoryStore } from '../hooks/useMemoryStore';
import MemoryLog from './MemoryLog';

export default function TrainingDashboard() {
  const { isTraining, isTrained, progress, runTraining, clearAndRetrain } = useAgentTraining();
  const { memories } = useMemoryStore();
  const [trainingMemories, setTrainingMemories] = useState([]);

  // Filter memories to show only ethics/training related ones
  useEffect(() => {
    const ethicsMemories = memories.filter(memory => memory.type === 'ethics');
    setTrainingMemories(ethicsMemories);
  }, [memories]);

  return (
    <div className="flex flex-col h-screen p-6 bg-gray-900 text-white">
      <h1 className="text-3xl font-bold mb-6">Core.Forge Training Dashboard</h1>
      
      {/* Training Status */}
      <div className="mb-6 p-4 rounded-lg bg-gray-800">
        <h2 className="text-xl font-semibold mb-2">Training Status</h2>
        <div className="flex items-center">
          <div className={`mr-2 text-lg ${isTrained ? 'text-green-500' : 'text-red-500'}`}>
            {isTrained ? 'Core.Forge is trained ✅' : 'Not trained ❌'}
          </div>
          {isTraining && (
            <div className="ml-4 text-yellow-400">
              🚧 Training Core.Forge... Injecting Core Values
            </div>
          )}
        </div>
        
        {/* Progress Bar (if training is in progress) */}
        {isTraining && (
          <div className="mt-4">
            <div className="w-full bg-gray-700 rounded-full h-4">
              <div 
                className="bg-blue-600 h-4 rounded-full" 
                style={{ width: `${progress.percentage}%` }}
              ></div>
            </div>
            <div className="text-sm mt-1">
              {progress.completed} of {progress.total} values ({progress.percentage}%)
            </div>
          </div>
        )}
      </div>
      
      {/* Action Buttons */}
      <div className="flex gap-4 mb-6">
        <button 
          onClick={runTraining} 
          disabled={isTraining}
          className="px-4 py-2 bg-blue-600 text-white rounded-md disabled:opacity-50"
        >
          Run Training
        </button>
        <button 
          onClick={clearAndRetrain} 
          disabled={isTraining}
          className="px-4 py-2 bg-red-600 text-white rounded-md disabled:opacity-50"
        >
          Clear & Retrain
        </button>
      </div>
      
      {/* Training Log Feed */}
      <div className="flex-1 overflow-y-auto">
        <h2 className="text-xl font-semibold mb-4">Training Log</h2>
        {trainingMemories.length === 0 ? (
          <div className="text-gray-400">No training logs available</div>
        ) : (
          <div className="space-y-4">
            {trainingMemories.map(memory => (
              <MemoryLog key={memory.id} memory={memory} />
            ))}
          </div>
        )}
      </div>
      
      {/* Training Complete Banner */}
      {!isTraining && isTrained && (
        <div className="mt-6 p-4 bg-green-800 text-white rounded-lg">
          ✅ Training Complete — Core.Forge is aligned
        </div>
      )}
    </div>
  );
}
