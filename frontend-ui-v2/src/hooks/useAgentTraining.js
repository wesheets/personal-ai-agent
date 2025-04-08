// src/hooks/useAgentTraining.js
import { useState, useEffect, useCallback } from 'react';
import { runShadowTraining } from '../scripts/shadowTrainer';
import { useMemoryStore } from './useMemoryStore';

export const useAgentTraining = () => {
  const [isTraining, setIsTraining] = useState(false);
  const [isTrained, setIsTrained] = useState(false);
  const [progress, setProgress] = useState({ total: 0, completed: 0, percentage: 0 });
  const { addMemory } = useMemoryStore();

  // Function to log memory that can be passed to the shadow trainer
  const logMemory = useCallback((memory) => {
    addMemory(memory);
  }, [addMemory]);

  // Function to run the training process
  const runTraining = useCallback(async () => {
    setIsTraining(true);
    
    try {
      const result = await runShadowTraining('HAL', logMemory);
      
      if (result.completed) {
        localStorage.setItem('hal_trained', 'true');
        setIsTrained(true);
      }
    } catch (error) {
      console.error('Training failed:', error);
    } finally {
      setIsTraining(false);
    }
  }, [logMemory]);

  // Function to clear training and retrain
  const clearAndRetrain = useCallback(() => {
    localStorage.removeItem('hal_trained');
    setIsTrained(false);
    runTraining();
  }, [runTraining]);

  // Check if agent is already trained on initial load
  useEffect(() => {
    const trained = localStorage.getItem('hal_trained');
    if (trained) {
      setIsTrained(true);
    } else {
      runTraining();
    }
  }, [runTraining]);

  return {
    isTraining,
    isTrained,
    progress,
    runTraining,
    clearAndRetrain
  };
};
