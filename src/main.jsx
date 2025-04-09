// src/main.jsx - Update to include API mocking
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { BrowserRouter } from 'react-router-dom'
import { ChakraProvider } from '@chakra-ui/react'
import { AuthProvider } from './context/AuthContext'
import { http, HttpResponse } from 'msw'

// Setup mock service worker for API mocking
if (import.meta.env.DEV) {
  const mockWorker = worker.use(
    // Mock the delegate-stream endpoint
    http.post('/api/delegate-stream', async ({ request }) => {
      const { task_name, task_goal, streaming } = await request.json()
      
      // Return a streaming response
      return new HttpResponse(
        new ReadableStream({
          start(controller) {
            const encoder = new TextEncoder()
            
            // Mock response text to stream
            const responseText = `I'm HAL, your Promethios agent. I'll help you with: "${task_goal}".
            
This is a simulated streaming response to demonstrate the functionality.
The streaming parameter is set to: ${streaming ? 'enabled' : 'disabled'}.

I'm analyzing your request...
Processing...
Generating response...

Task complete! I've processed your request for "${task_name}".`

            // If streaming is disabled, send the entire response at once
            if (!streaming) {
              controller.enqueue(encoder.encode(responseText))
              controller.close()
              return
            }
            
            // If streaming is enabled, send the response in chunks
            const words = responseText.split(' ')
            
            let i = 0
            const interval = setInterval(() => {
              if (i >= words.length) {
                clearInterval(interval)
                controller.close()
                return
              }
              
              const word = words[i] + (i < words.length - 1 ? ' ' : '')
              controller.enqueue(encoder.encode(word))
              i++
            }, 100)
            
            return () => {
              clearInterval(interval)
            }
          }
        }),
        {
          headers: {
            'Content-Type': 'text/event-stream',
          },
        }
      )
    })
  )
  
  mockWorker.start()
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <ChakraProvider>
        <AuthProvider>
          <App />
        </AuthProvider>
      </ChakraProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
