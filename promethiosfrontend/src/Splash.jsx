import { useNavigate } from "react-router-dom";
import { useState } from "react";
import logo from "../assets/logo.png";

export default function Splash() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();

    const adminUser = import.meta.env.VITE_ADMIN_USERNAME;
    const adminPass = import.meta.env.VITE_ADMIN_PASSWORD;

    if (username === adminUser && password === adminPass) {
      setError("");
      navigate("/dashboard");
    } else {
      setError("Access denied. 🔒 Invalid credentials.");
    }
  };

  return (
    <div className="min-h-screen bg-black text-white grid place-items-center px-4">
      <div className="w-full max-w-md space-y-8 text-center animate-fade-in">
        <img
          src={logo}
          alt="Promethios Logo"
          className="w-60 md:w-68 lg:w-76 mx-auto mb-6 drop-shadow-xl animate-logo-glow"
        />

        <form
          onSubmit={handleLogin}
          className="bg-gray-900 border border-gray-700 p-6 rounded-xl shadow-lg space-y-4"
        >
          <h2 className="text-xl font-semibold tracking-wide mb-2">
            Welcome to Promethios OS
          </h2>

          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full p-2 rounded bg-black border border-gray-600 text-white placeholder-gray-400 focus:ring-2 focus:ring-teal-500 outline-none"
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-2 rounded bg-black border border-gray-600 text-white placeholder-gray-400 focus:ring-2 focus:ring-teal-500 outline-none"
          />

          {error && <p className="text-red-400 text-sm mt-1">{error}</p>}

          <button
            type="submit"
            className="w-full bg-teal-500 text-black font-semibold py-2 rounded hover:bg-teal-400 transition-all"
          >
            Enter Control Room
          </button>
        </form>

        <p className="text-sm text-gray-500 font-mono animate-pulse-slow">
          🔥 The Fire is Lit
        </p>
      </div>
    </div>
  );
}
