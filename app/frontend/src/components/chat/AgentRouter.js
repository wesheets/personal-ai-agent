/**
 * AgentRouter.js
 * 
 * Utility for routing messages to appropriate endpoints based on agent type.
 * Handles all POST calls with schema-wrapped payloads.
 */

/**
 * Routes a message to the appropriate endpoint based on agent type
 * 
 * @param {Object} message - The message object to send
 * @param {string} message.agent - Agent identifier (orchestrator, ash, sage, etc.)
 * @param {string} message.role - Message role (operator or agent)
 * @param {string} message.message - Message content
 * @param {string} message.project_id - Project identifier
 * @param {string} message.loop_id - Loop identifier
 * @returns {Promise} - Promise resolving to the agent response
 */
export const routeMessage = async (message) => {
  // Validate message has required fields
  if (!message.agent || !message.message || !message.project_id) {
    throw new Error('Message missing required fields');
  }

  // Determine endpoint based on agent
  let endpoint;
  switch (message.agent.toLowerCase()) {
    case 'orchestrator':
      endpoint = '/loop/plan';
      break;
    case 'sage':
      endpoint = '/reflect';
      break;
    default:
      endpoint = '/agent/run';
      break;
  }

  // Prepare payload with schema compliance
  const payload = {
    agent: message.agent,
    role: message.role || 'operator',
    loop_id: message.loop_id || `loop_${Date.now()}`,
    project_id: message.project_id,
    message: message.message,
    schema_compliant: true,
    timestamp: message.timestamp || new Date().toISOString()
  };

  try {
    // Make API request
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error (${response.status}): ${errorText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`Error routing message to ${endpoint}:`, error);
    throw error;
  }
};

/**
 * Writes a message to memory
 * 
 * @param {Object} message - The message to store
 * @param {Array} tags - Tags to associate with the message
 * @returns {Promise} - Promise resolving to the memory write response
 */
export const writeToMemory = async (message, tags = []) => {
  try {
    const response = await fetch('/memory/write', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content: message,
        tags: [`loop:${message.loop_id}`, `agent:${message.agent}`, 'thread:chat', ...tags],
        project_id: message.project_id,
        schema_compliant: true
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Memory API error (${response.status}): ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error writing to memory:', error);
    throw error;
  }
};

export default {
  routeMessage,
  writeToMemory
};
