// src/useAgentDebug.js
import { useState } from 'react';

export function useAgentDebug() {
  const [payload, setPayload] = useState(null);
  const [memory, setMemory] = useState('');
  const [logs, setLogs] = useState('');
  const [debugOpen, setDebugOpen] = useState(false);

  const logPayload = (taskPayload) => setPayload(taskPayload);
  const logMemory = (memoryText) => setMemory(memoryText);
  const logThoughts = (reasoning) => setLogs(reasoning);

  const resetDebug = () => {
    setPayload(null);
    setMemory('');
    setLogs('');
  };

  return {
    payload,
    memory,
    logs,
    debugOpen,
    setDebugOpen,
    logPayload,
    logMemory,
    logThoughts,
    resetDebug
  };
}
