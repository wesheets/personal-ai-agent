import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAgentDebug } from './useAgentDebug'
import TerminalDrawer from './TerminalDrawer'
import { logout } from './hooks/useAuth'

export default function AgentChat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(true)
  const [loading, setLoading] = useState(false)
  // Track file uploads
  const [fileUpload, setFileUpload] = useState(null)
  // eslint-disable-next-line no-unused-vars
  const feedRef = useRef(null)
  const [debugOpen, setDebugOpen] = useState(false)
  const { payload, memory, logs, logPayload, logMemory, logThoughts } = useAgentDebug()
  const navigate = useNavigate()

  useEffect(() => {
    feedRef.current?.scrollTo(0, feedRef.current.scrollHeight)
  }, [messages])

  const handleSubmit = async () => {
    if (!input.trim()) return
    setLoading(true)

    const newMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, newMessage])
    setInput('')

    // Log the payload for debug drawer
    logPayload({ task_name: 'user', task_goal: input, streaming })

    const res = await fetch('/api/delegate-stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task_name: 'user', task_goal: input, streaming })
    })

    if (!res.ok || !res.body) return

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let agentMsg = ''
    setMessages(prev => [...prev, { role: 'hal', content: '' }])

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      agentMsg += decoder.decode(value)
      setMessages(prev => prev.map((m, i) => i === prev.length - 1 ? { ...m, content: agentMsg } : m))
    }

    // Log memory and thoughts for debug drawer
    logMemory('Memory accessed: User query about ' + input)
    logThoughts('Agent reasoning process: Analyzed query and generated response')

    setMessages(prev => [...prev, { role: 'system', content: '💾 Memory Logged' }])
    setLoading(false)
  }

  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      setFileUpload(file)
      console.log('File selected:', file.name)
    }
  }

  const handlePaste = (e) => {
    const items = e.clipboardData?.items
    if (items) {
      for (let i = 0; i < items.length; i++) {
        if (items[i].kind === 'file') {
          const file = items[i].getAsFile()
          setFileUpload(file)
          console.log('File pasted:', file.name)
          break
        }
      }
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const files = e.dataTransfer?.files
    if (files && files.length > 0) {
      setFileUpload(files[0])
      console.log('File dropped:', files[0].name)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
  }

  const handleLogout = () => {
    logout()
    navigate('/auth')
  }

  return (
    <div 
      className="flex flex-col h-screen"
      onPaste={handlePaste}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
    >
      <div className="p-2 flex justify-end">
        <button 
          onClick={handleLogout} 
          className="text-sm px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Logout
        </button>
      </div>
      
      <div ref={feedRef} className="flex-1 overflow-y-auto p-4">
        {messages.map((msg, i) => (
          <div key={i} className={`my-2 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
            <div className={`inline-block px-4 py-2 rounded-xl ${msg.role === 'user' ? 'bg-blue-600 text-white' : msg.role === 'system' ? 'bg-gray-500 text-white' : 'bg-gray-200 text-black'}`}>
              <strong>{msg.role === 'user' ? 'You' : msg.role.toUpperCase()}:</strong> {msg.content}
            </div>
          </div>
        ))}
      </div>

      <div className="p-4 border-t flex items-center gap-2">
        <button onClick={() => setDebugOpen(!debugOpen)} className="text-sm px-2 py-1 border rounded">
          &lt;/&gt;
        </button>
        <button onClick={() => setStreaming(!streaming)} className="text-sm px-2 py-1 border rounded">
          {streaming ? 'Streaming ON' : 'Streaming OFF'}
        </button>
        <label className="text-sm px-2 py-1 border rounded cursor-pointer">
          +
          <input 
            type="file" 
            className="hidden" 
            onChange={handleFileUpload}
          />
        </label>
        <textarea
          className="flex-1 border rounded p-2"
          rows={2}
          placeholder="Enter your task..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSubmit())}
        />
        <button onClick={handleSubmit} disabled={loading} className="bg-white text-black px-4 py-2 rounded">
          {loading ? 'Thinking...' : 'Send'}
        </button>
      </div>
      
      <TerminalDrawer 
        open={debugOpen} 
        onClose={() => setDebugOpen(false)} 
        payload={payload}
        memory={memory}
        logs={logs}
      />
    </div>
  )
}
