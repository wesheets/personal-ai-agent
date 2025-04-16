export async function callOrchestrator(prompt) {
  try {
    const res = await fetch('/api/orchestrator/respond', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    if (!res.ok) {
      throw new Error('Orchestrator failed to respond');
    }

    const data = await res.json();
    return data.response || '[No response received]';
  } catch (err) {
    console.error('ORCHESTRATOR ERROR:', err);
    return '[Error: Unable to reach ORCHESTRATOR]';
  }
}
