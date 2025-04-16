import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Splash() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [override, setOverride] = useState('');
  const [error, setError] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();

    const isValid =
      (username === import.meta.env.VITE_ADMIN_USERNAME &&
        password === import.meta.env.VITE_ADMIN_PASSWORD) ||
      override === 'I AM PROMETHIOS';

    if (isValid) {
      localStorage.setItem('auth_token', 'promethios_token');
      navigate('/control');
    } else {
      setError('Access Denied');
    }
  };

  return (
    <div className="flex h-screen font-sans">
      {/* Left panel */}
      <div className="w-[460px] bg-black text-white p-12 flex flex-col justify-center space-y-6">
        <img src="/logo.png" alt="Promethios" className="w-[160px] mb-4" />
        <h1 className="text-2xl font-bold">Promethios Operator Dashboard</h1>
        <p className="text-sm text-gray-400">The fire has been lit. Operator input required.</p>

        <form className="flex flex-col space-y-4" onSubmit={handleLogin}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="p-2 bg-gray-800 border border-gray-700 rounded"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="p-2 bg-gray-800 border border-gray-700 rounded"
          />
          <input
            type="text"
            placeholder="Override (e.g. I AM PROMETHIOS)"
            value={override}
            onChange={(e) => setOverride(e.target.value)}
            className="p-2 bg-gray-800 border border-gray-700 rounded"
          />
          <button
            type="submit"
            className="bg-indigo-500 hover:bg-indigo-600 text-white p-2 rounded-md font-semibold"
          >
            Access
          </button>
          {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
        </form>
      </div>

      {/* Right panel */}
      <div className="flex-1 bg-gradient-to-br from-black to-gray-900 flex items-center justify-center text-white text-xl italic tracking-wide">
        “The forge awakens those who dare to shape the future.”
      </div>
    </div>
  );
}
