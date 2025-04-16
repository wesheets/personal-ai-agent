import { useEffect } from 'react';

export default function useAgentDebug(agentLogs, setAgentLogs, newEntry) {
  useEffect(() => {
    if (!newEntry) return;

    const timestamp = new Date().toISOString();
    const log = {
      ...newEntry,
      timestamp
    };

    setAgentLogs((prev) => [...prev, log]);

    console.debug('[Agent Debug]', log);
  }, [newEntry]);
}
