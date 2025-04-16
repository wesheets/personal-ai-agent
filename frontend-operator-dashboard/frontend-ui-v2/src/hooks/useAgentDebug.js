import { useState } from 'react';

export function useAgentDebug() {
  const [payload, setPayload] = useState(null);
  const [memory, setMemory] = useState('');
  const [logs, setLogs] = useState('');

  const logPayload = (taskPayload) => setPayload(taskPayload);
  const logMemory = (memoryText) =>
    setMemory((prev) => (prev ? `${prev}\n${memoryText}` : memoryText));
  const logThoughts = (reasoning) =>
    setLogs((prev) => (prev ? `${prev}\n${reasoning}` : reasoning));

  const resetDebug = () => {
    setPayload(null);
    setMemory('');
    setLogs('');
  };

  return {
    payload,
    memory,
    logs,
    logPayload,
    logMemory,
    logThoughts,
    resetDebug
  };
}
