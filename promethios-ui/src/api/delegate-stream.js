// Mock implementation of the delegate-stream API endpoint
export async function delegateStream(req, res) {
  // This would normally connect to a backend service
  // For testing purposes, we'll create a simple mock that streams responses
  
  const encoder = new TextEncoder();
  const { task_name, task_goal, streaming } = req.body;
  
  // Set appropriate headers for streaming
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  
  // Mock response text to stream
  const responseText = `I'm HAL, your Promethios agent. I'll help you with: "${task_goal}".
  
This is a simulated streaming response to demonstrate the functionality.
The streaming parameter is set to: ${streaming ? 'enabled' : 'disabled'}.

I'm analyzing your request...
Processing...
Generating response...

Task complete! I've processed your request for "${task_name}".`;

  // If streaming is disabled, send the entire response at once
  if (!streaming) {
    res.write(encoder.encode(responseText));
    res.end();
    return;
  }
  
  // If streaming is enabled, send the response in chunks
  const words = responseText.split(' ');
  
  // Stream each word with a small delay
  for (let i = 0; i < words.length; i++) {
    const word = words[i] + (i < words.length - 1 ? ' ' : '');
    
    // Write the word to the response
    res.write(encoder.encode(word));
    
    // Flush the response to ensure it's sent immediately
    if (res.flush) {
      res.flush();
    }
    
    // Add a small delay between words (simulating streaming)
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  // End the response
  res.end();
}

// Export a default handler for API routes
export default async function handler(req, res) {
  if (req.method === 'POST') {
    await delegateStream(req, res);
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}
