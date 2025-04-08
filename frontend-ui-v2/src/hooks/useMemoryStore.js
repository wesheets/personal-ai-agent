// src/hooks/useMemoryStore.js
import { useState } from 'react';

export function useMemoryStore() {
  const [memories, setMemories] = useState([]);

  const addMemory = (memory) => {
    setMemories(prev => [...prev, memory]);
  };

  const getMemoriesByType = (type) =>
    memories.filter(m => m.type === type);

  const getAllMemories = () => memories;

  return { memories, addMemory, getMemoriesByType, getAllMemories };
}
