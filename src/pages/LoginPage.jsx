// src/pages/LoginPage.jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { isAuthenticated, login } from '../hooks/useAuth'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = (e) => {
    e.preventDefault()
    if (email === 'admin@promethios.ai' && password === 'ignite') {
      login()
      navigate('/hal')
    } else {
      setError('Invalid login credentials')
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-black text-white">
      <img src="/promethioslogo.png" alt="Promethios Logo" className="w-72 mb-6 animate-pulse" />
      <form onSubmit={handleSubmit} className="bg-white text-black p-6 rounded-md w-96 space-y-4">
        <h2 className="text-xl font-semibold text-center">Login to Promethios</h2>
        {error && <p className="text-red-600 text-sm text-center">{error}</p>}
        <input
          type="email"
          placeholder="Email"
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
