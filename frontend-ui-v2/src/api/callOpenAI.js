/**
 * API utility to call OpenAI's GPT-4 model
 *
 * @param {string} prompt - The prompt to send to OpenAI
 * @param {string} agentId - The ID of the agent making the request (default: 'core-forge')
 * @param {Array} history - The conversation history
 * @param {string} threadId - Unique identifier for the conversation thread
 * @returns {Promise<string>} - The natural language response from GPT-4
 */
export const callOpenAI = async (prompt, agentId = 'core-forge', history = [], threadId = Date.now().toString()) => {
  try {
    // In a production environment, this would make an actual API call to OpenAI
    // For now, we'll simulate a response with a mock implementation
    
    console.log(`Calling OpenAI with prompt for ${agentId}:`, prompt);
    console.log(`Thread ID: ${threadId}, History items: ${history.length}`);
    
    // Simulate API latency
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // In production, this would be replaced with actual OpenAI API call:
    /*
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [{ role: 'system', content: 'You are an AI assistant' }, ...history, { role: 'user', content: prompt }],
        temperature: 0.7,
        max_tokens: 500
      })
    });
    
    const data = await response.json();
    return data.choices[0].message.content;
    */
    
    // Get agent-specific responses based on agentId
    if (agentId === 'core-forge') {
      return getCoreForgeResponse(prompt, history);
    } else {
      return getHalResponse(prompt, history);
    }
  } catch (error) {
    console.error('Error calling OpenAI:', error);
    return "I'm sorry, I encountered an error processing your request. Please try again.";
  }
};

// HAL-specific responses
const getHalResponse = (prompt, history = []) => {
  const promptLower = prompt.toLowerCase();
  
  // Check if we should reference previous messages
  if (history.length > 0 && (promptLower.includes('what did i') || promptLower.includes('previous') || promptLower.includes('earlier'))) {
    const previousUserMessage = history.filter(msg => msg.role === 'user').slice(-1)[0];
    if (previousUserMessage) {
      return `You previously said: "${previousUserMessage.content}"`;
    }
  }
  
  if (promptLower.includes('hello') || promptLower.includes('hi')) {
    return "Hello! I'm HAL, your personal AI assistant. How can I help you today?";
  } else if (promptLower.includes('help')) {
    return "I'm here to assist you with various tasks. You can ask me questions, request information, or have me perform tasks for you. What would you like help with?";
  } else if (promptLower.includes('weather')) {
    return "I don't have real-time access to weather data, but I can help you find weather information if you provide me with a location.";
  } else if (promptLower.includes('time')) {
    return `The current time is ${new Date().toLocaleTimeString()}.`;
  } else if (promptLower.match(/\d+\s*[+\-*/]\s*\d+/)) {
    // Simple math detection
    return "I detect a mathematical expression. I can help calculate that for you. Would you like me to solve it?";
  } else {
    return `I've processed your request: "${prompt}". As an AI assistant, I'm here to help you with information, answer questions, and assist with various tasks. How else can I assist you today?`;
  }
};

// Core.Forge-specific responses
const getCoreForgeResponse = (prompt, history = []) => {
  const promptLower = prompt.toLowerCase();
  
  // Check if we should reference previous messages
  if (history.length > 0 && (promptLower.includes('what did i') || promptLower.includes('previous') || promptLower.includes('earlier'))) {
    const previousUserMessage = history.filter(msg => msg.role === 'user').slice(-1)[0];
    if (previousUserMessage) {
      return `Previous user input: "${previousUserMessage.content}"`;
    }
  }
  
  if (promptLower.includes('hello') || promptLower.includes('hi')) {
    return "Greetings. Core.Forge online and ready to assist with your task.";
  } else if (promptLower.includes('help')) {
    return "Core.Forge capabilities include: task planning, code generation, data analysis, and structured output creation. Please specify your requirements for optimal results.";
  } else if (promptLower.includes('weather')) {
    return "Weather data access: unavailable. Core.Forge can assist with data processing tasks if weather information is provided.";
  } else if (promptLower.includes('time')) {
    return `Current system time: ${new Date().toLocaleTimeString()}`;
  } else if (promptLower.match(/\d+\s*[+\-*/]\s*\d+/)) {
    // Simple math detection with Core.Forge style
    const mathExpression = promptLower.match(/(\d+)\s*([+\-*/])\s*(\d+)/);
    if (mathExpression) {
      const [_, num1, operator, num2] = mathExpression;
      let result;
      switch(operator) {
        case '+': result = parseInt(num1) + parseInt(num2); break;
        case '-': result = parseInt(num1) - parseInt(num2); break;
        case '*': result = parseInt(num1) * parseInt(num2); break;
        case '/': result = parseInt(num1) / parseInt(num2); break;
      }
      return `Calculation complete: ${num1} ${operator} ${num2} = ${result}`;
    }
  }
  
  return `Task received: "${prompt}". Processing request. Core.Forge will execute this task with maximum efficiency.`;
};
