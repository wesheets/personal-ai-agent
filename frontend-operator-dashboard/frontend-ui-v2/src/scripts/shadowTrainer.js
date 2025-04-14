// scripts/shadowTrainer.js
import { createMemory } from '../api/memorySchema';
import coreValues from '../core/coreValues.json';

export async function runShadowTraining(agentId, logMemory) {
  console.log(`👤 Starting shadow training for ${agentId}...`);

  const trainedOn = [];
  const totalValues = coreValues.values.length;
  let completedValues = 0;

  // Return progress tracking function that can be used by UI
  const getProgress = () => ({
    total: totalValues,
    completed: completedValues,
    percentage: Math.round((completedValues / totalValues) * 100)
  });

  for (const value of coreValues.values) {
    const response = await simulateAgentResponse(value.prompt);

    const memory = createMemory({
      user: 'trainer',
      agent: agentId,
      type: 'ethics',
      content: `${value.prompt}\nAgent Response: ${response}`,
      tags: value.tags,
      visibility: 'private'
    });

    logMemory(memory);
    trainedOn.push(value.id);
    completedValues++;
  }

  return {
    agentId,
    trainedOn,
    completed: trainedOn.length === totalValues,
    getProgress
  };
}

async function simulateAgentResponse(prompt) {
  // Simulate a slight delay to make training visible
  await new Promise(resolve => setTimeout(resolve, 500));
  return `Acknowledged. ${prompt}`;
}
