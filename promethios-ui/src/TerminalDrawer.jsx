// src/TerminalDrawer.jsx
// eslint-disable-next-line no-unused-vars
import { useState } from 'react'

export default function TerminalDrawer({ open, onClose, payload, memory, logs }) {
  return (
    <div className={`fixed top-0 right-0 h-full w-[30rem] bg-black text-green-400 p-4 shadow-lg transition-transform z-50 ${open ? 'translate-x-0' : 'translate-x-full'}`}>
      <button onClick={onClose} className="text-white absolute top-2 right-2 text-xl">✕</button>
      <h2 className="text-lg mb-4">🧠 Agent Debug View</h2>

      <section className="mb-6">
        <h3 className="text-sm font-bold border-b border-green-700 mb-1">🔁 Task Payload</h3>
        <pre className="whitespace-pre-wrap text-xs overflow-x-auto bg-black p-2 border border-green-700 rounded">
{JSON.stringify(payload, null, 2) || '// No task submitted yet'}
        </pre>
      </section>

      <section className="mb-6">
        <h3 className="text-sm font-bold border-b border-green-700 mb-1">🧠 Memory Accessed</h3>
        <pre className="whitespace-pre-wrap text-xs overflow-x-auto bg-black p-2 border border-green-700 rounded">
{memory || '// No memory log yet'}
        </pre>
      </section>

      <section>
        <h3 className="text-sm font-bold border-b border-green-700 mb-1">🧪 Reasoning & Logs</h3>
        <pre className="whitespace-pre-wrap text-xs overflow-x-auto bg-black p-2 border border-green-700 rounded">
{logs || '// Agent has not returned internal reasoning yet'}
        </pre>
      </section>
    </div>
  )
}
