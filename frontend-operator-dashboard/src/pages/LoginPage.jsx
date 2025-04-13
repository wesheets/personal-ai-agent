// src/pages/LoginPage.jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { isAuthenticated, login } from '../hooks/useAuth'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  // Get environment variables with fallback to default values
  const validUsername = import.meta.env.VITE_OPERATOR_USERNAME || 'admin'
  const validPassword = import.meta.env.VITE_OPERATOR_PASSWORD || 'securekey'

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // Easter egg override
    if (password === 'I AM PROMETHIOS') {
      login()
      navigate('/dashboard')
      return
    }
    
    // Regular authentication
    if (email === validUsername && password === validPassword) {
      login()
      navigate('/dashboard')
    } else {
      setError('Access Denied')
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-black text-white">
      <img src="/promethioslogo.png" alt="Promethios Logo" className="w-72 mb-6 animate-pulse" />
      <form onSubmit={handleSubmit} className="bg-white text-black p-6 rounded-md w-96 space-y-4">
        <h2 className="text-xl font-semibold text-center">Login to Promethios</h2>
        {error && <p className="text-red-600 text-sm text-center">{error}</p>}
        <input
          type="text"
          placeholder="Username"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-2 border rounded"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-2 border rounded"
        />
        <button type="submit" className="w-full bg-black text-white p-2 rounded hover:bg-gray-800">
          Login
        </button>
      </form>
      <p className="text-xs mt-10 opacity-20">The fire was stolen for a reason.</p>
    </div>
  )
}
