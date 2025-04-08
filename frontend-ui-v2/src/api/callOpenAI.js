/**
 * API utility to call OpenAI's GPT-4 model
 * 
 * @param {string} prompt - The prompt to send to OpenAI
 * @param {string} agentId - The ID of the agent making the request (default: 'hal')
 * @returns {Promise<string>} - The natural language response from GPT-4
 */
export const callOpenAI = async (prompt, agentId = 'hal') => {
  try {
    // In a production environment, this would make an actual API call to OpenAI
    // For now, we'll simulate a response with a mock implementation
    
    console.log(`Calling OpenAI with prompt for ${agentId}:`, prompt);
    
    // Simulate API latency
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Get agent-specific responses based on agentId
    if (agentId === 'core-forge') {
      return getCoreForgeResponse(prompt);
    } else {
      return getHalResponse(prompt);
    }
  } catch (error) {
    console.error('Error calling OpenAI:', error);
    return "I'm sorry, I encountered an error processing your request. Please try again.";
  }
};

// HAL-specific responses
const getHalResponse = (prompt) => {
  const promptLower = prompt.toLowerCase();
  
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
const getCoreForgeResponse = (prompt) => {
  const promptLower = prompt.toLowerCase();
  
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
