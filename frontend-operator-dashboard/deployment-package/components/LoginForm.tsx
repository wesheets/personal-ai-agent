import React, { useState } from 'react';
import Typewriter from 'typewriter-effect';

interface LoginFormProps {
  onLogin: (username: string, password: string) => void;
  error: string | null;
}

const LoginForm: React.FC<LoginFormProps> = ({ onLogin, error }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [specialMessage, setSpecialMessage] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Check for easter egg
    if (username.toLowerCase() === 'i am promethios' && password === '') {
      setSpecialMessage('Welcome, Architect. System readiness: 91%');
      return;
    }

    onLogin(username, password);
  };

  return (
    <div className="mt-8 w-full max-w-md mx-auto">
      {specialMessage ? (
        <div className="text-green-400 text-center p-4 border border-green-800 bg-black bg-opacity-50 rounded">
          {specialMessage}
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-300">
              Operator Input
            </label>
            <div className="mt-1">
              <input
                id="username"
                name="username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="appearance-none block w-full px-3 py-2 border border-gray-700 rounded-md shadow-sm placeholder-gray-500 bg-gray-900 text-gray-100 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Enter passphrase to activate"
              />
            </div>
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-300">
              Password
            </label>
            <div className="mt-1">
              <input
                id="password"
                name="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="appearance-none block w-full px-3 py-2 border border-gray-700 rounded-md shadow-sm placeholder-gray-500 bg-gray-900 text-gray-100 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>

          {error && <div className="text-red-500 text-sm">{error}</div>}

          <div>
            <button
              type="submit"
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Access System
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default LoginForm;
