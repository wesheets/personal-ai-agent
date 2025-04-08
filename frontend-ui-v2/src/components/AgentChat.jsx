// src/components/AgentChat.jsx
import { useState, useRef, useEffect } from 'react'

export default function AgentChat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(true)
  const [loading, setLoading] = useState(false)
  const feedRef = useRef(null)

  useEffect(() => {
    feedRef.current?.scrollTo(0, feedRef.current.scrollHeight)
  }, [messages])

  const handleSubmit = async () => {
    if (!input.trim()) return
    setLoading(true)

    const newMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, newMessage])
    setInput('')

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

    setMessages(prev => [...prev, { role: 'system', content: '💾 Memory Logged' }])
    setLoading(false)
  }

  return (
    <div className="flex flex-col h-screen">
      <div ref={feedRef} className="flex-1 overflow-y-auto p-4">
        {messages.map((msg, i) => (
          <div key={i} className={`my-2 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
            <div className={`inline-block px-4 py-2 rounded-xl ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-black'}`}>
              <strong>{msg.role === 'user' ? 'You' : msg.role.toUpperCase()}:</strong> {msg.content}
            </div>
          </div>
        ))}
      </div>

      <div className="p-4 border-t flex items-center gap-2">
        <button onClick={() => setStreaming(!streaming)} className="text-sm px-2 py-1 border rounded">
          {streaming ? 'Streaming ON' : 'Streaming OFF'}
        </button>
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
    </div>
  )
}
