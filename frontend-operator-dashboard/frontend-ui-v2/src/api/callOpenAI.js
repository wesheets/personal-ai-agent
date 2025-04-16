// src/api/callOpenAI.js
export const callOpenAI = async (prompt, agentId = 'core-forge', history = [], threadId = null) => {
  try {
    console.log(`Calling backend API with prompt for ${agentId}:`, prompt);
    console.log(`Thread ID: ${threadId}, History items: ${history.length}`);

    // Make actual API call to our backend
    const response = await fetch('/api/delegate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        prompt,
        agent_id: agentId,
        history,
        threadId
      })
    });

    if (!response.ok) {
      throw new Error(`API call failed with status: ${response.status}`);
    }

    const data = await response.json();

    // Extract the message content from the response
    if (data && data.message) {
      // Remove the agent label prefix if present
      const messageContent = data.message.replace(/^\[\w+\]\s+/, '');
      return messageContent;
    }

    return "I'm sorry, I encountered an error processing your request. Please try again.";
  } catch (error) {
    console.error('Error calling OpenAI:', error);
    return "I'm sorry, I encountered an error processing your request. Please try again.";
  }
};
