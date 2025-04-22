import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function LoginGate() {
  const [code, setCode] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    if (code === "ignite") {
      localStorage.setItem("authToken", "true");
      navigate("/console");
    }
  };

  return (
    <form onSubmit={handleLogin} className="absolute bottom-6 right-6 z-10">
      <input
        type="password"
        placeholder="Access Code"
        className="px-3 py-1 rounded-md text-black"
        value={code}
        onChange={(e) => setCode(e.target.value)}
      />
      <button className="ml-2 bg-white text-black px-3 py-1 rounded-md">Enter</button>
    </form>
  );
}
