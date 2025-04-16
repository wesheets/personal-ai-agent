import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Splash() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [override, setOverride] = useState('');
  const [error, setError] = useState(false);
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    if (
      (username === import.meta.env.VITE_OPERATOR_USERNAME &&
        password === import.meta.env.VITE_OPERATOR_PASSWORD) ||
      override === 'I AM PROMETHIOS'
    ) {
      localStorage.setItem('authenticated', 'true');
      navigate('/dashboard');
    } else {
      setError(true);
    }
  };

  return (
    <div className="flex h-screen bg-black text-white">
      {/* Left Panel */}
      <div className="w-[460px] flex flex-col justify-center items-center px-10">
        <img src="/logo.png" alt="Promethios Logo" className="w-[160px] mb-8" />
        <h1 className="text-2xl font-bold mb-2">Promethios Operator Dashboard</h1>
        <p className="text-sm text-gray-400 mb-6">
          The fire has been lit. Operator input required.
        </p>

        <form className="w-full space-y-4" onSubmit={handleLogin}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-2 rounded bg-gray-900 border border-gray-700 focus:outline-none"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 rounded bg-gray-900 border border-gray-700 focus:outline-none"
          />
          <input
            type="text"
            placeholder='Override (e.g. I AM PROMETHIOS)'
            value={override}
            onChange={(e) => setOverride(e.target.value)}
            className="w-full px-4 py-2 rounded bg-gray-900 border border-gray-700 focus:outline-none"
          />
          <button
            type="submit"
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 rounded mt-2"
          >
            Access
          </button>
          {error && (
            <p className="text-red-500 text-sm text-center mt-2">
              Access denied. 🔒 Invalid credentials.
            </p>
          )}
        </form>

        <p className="text-xs text-gray-600 mt-6">🔥 The fire is lit</p>
      </div>

      {/* Right Panel */}
      <div className="flex-1 bg-gradient-to-br from-black to-gray-900 opacity-30 hidden md:block"></div>
    </div>
  );
}
