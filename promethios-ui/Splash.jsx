import { useNavigate } from 'react-router-dom';
import logo from './assets/promethios-logo.png'; // ⬅️ Replace with your actual logo path

export default function Splash() {
  const navigate = useNavigate();

  return (
    <div className="h-screen w-screen flex flex-col items-center justify-center bg-black text-white text-center">
      <img src={logo} alt="Promethios Logo" className="w-24 mb-6 opacity-90" />
      <h1 className="text-4xl font-bold mb-4 tracking-wider">🔥 The Fire is Lit</h1>
      <p className="text-lg text-gray-400 mb-8">Waiting for Operator...</p>
      <button
        onClick={() => navigate('/dashboard')}
        className="bg-white text-black px-6 py-3 rounded-xl hover:bg-gray-200 transition font-semibold"
      >
        Enter Control Room
      </button>
    </div>
  );
}
