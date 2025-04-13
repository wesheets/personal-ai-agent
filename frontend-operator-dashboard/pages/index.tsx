import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Check for easter egg
    if (username.toLowerCase() === 'i am promethios' && password === '') {
      // Special easter egg message
      localStorage.setItem('specialAccess', 'true');
      localStorage.setItem('authToken', 'architect-special-access');
      navigate('/dashboard');
      return;
    }
    
    // Check against environment variables
    const validUsername = import.meta.env.VITE_OPERATOR_USERNAME || 'admin';
    const validPassword = import.meta.env.VITE_OPERATOR_PASSWORD || 'securekey';
    
    if (username === validUsername && password === validPassword) {
      // Store session in localStorage
      localStorage.setItem('authToken', 'operator-authenticated');
      localStorage.setItem('username', username);
      
      // Route to dashboard
      navigate('/dashboard');
    } else {
      setError('Access Denied: Invalid operator credentials');
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-black text-white">
      <img src="/promethioslogo.png" alt="Promethios Logo" className="w-72 mb-6" />
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold mb-4">Promethios Operator Dashboard</h2>
        <p className="text-gray-400">The fire has been lit. Operator input required.</p>
      </div>
      
      <form onSubmit={handleSubmit} className="bg-gray-900 p-6 rounded-md w-96 space-y-4 border border-gray-700">
        <h2 className="text-xl font-semibold text-center text-gray-200">Operator Authentication</h2>
        {error && <p className="text-red-500 text-sm text-center">{error}</p>}
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-300 mb-1">
            Operator ID
          </label>
          <input
            id="username"
            type="text"
            placeholder="Enter operator ID"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full p-2 border border-gray-700 rounded bg-gray-800 text-white"
            required
          />
        </div>
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-1">
            Access Key
          </label>
          <input
            id="password"
            type="password"
            placeholder="Enter access key"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-2 border border-gray-700 rounded bg-gray-800 text-white"
            required
          />
        </div>
        <button 
          type="submit" 
          className="w-full bg-indigo-600 text-white p-2 rounded hover:bg-indigo-700 transition-colors"
        >
          Access System
        </button>
      </form>
      <p className="text-xs mt-10 opacity-20">The fire was stolen for a reason.</p>
    </div>
  );
}
