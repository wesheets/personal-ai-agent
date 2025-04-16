import { useState, useEffect } from 'react'

export default function MemoryToggle({ onToggle }) {
  const [enabled, setEnabled] = useState(() => {
    const saved = localStorage.getItem('log_interaction')
    return saved === 'false' ? false : true
  })

  useEffect(() => {
    localStorage.setItem('log_interaction', enabled.toString())
    if (onToggle) onToggle(enabled)
  }, [enabled, onToggle])

  return (
    <label className="flex items-center space-x-2 cursor-pointer">
      <input
        type="checkbox"
        checked={enabled}
        onChange={() => setEnabled(!enabled)}
        className="form-checkbox h-4 w-4 text-blue-500"
      />
      <span className="text-sm text-white">
        Log my conversation
      </span>
    </label>
  )
}
