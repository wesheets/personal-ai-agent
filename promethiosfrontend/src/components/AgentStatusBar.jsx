import { useEffect, useState } from 'react'

export default function AgentStatusBar({ agentState }) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (agentState) {
      setVisible(true)
      const timeout = setTimeout(() => setVisible(false), 5000)
      return () => clearTimeout(timeout)
    }
  }, [agentState])

  return (
    <div className={`fixed bottom-16 left-1/2 transform -translate-x-1/2 z-50`}>
      {visible && (
        <div className="px-4 py-2 rounded-full bg-blue-600 text-white animate-pulse shadow-lg">
          {agentState === 'thinking'
            ? 'HAL is thinking...'
            : agentState === 'responding'
            ? 'HAL is responding...'
            : 'Waiting for agent...'}
        </div>
      )}
    </div>
  )
}
