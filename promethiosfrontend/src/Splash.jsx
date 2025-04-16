import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import logo from "../assets/logo.png";

export default function Splash() {
  const navigate = useNavigate();
  const [typedText, setTypedText] = useState("");
  const message = "Waiting for Operator...";
  const speed = 50;

  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      setTypedText((prev) => prev + message[i]);
      i++;
      if (i >= message.length) clearInterval(interval);
    }, speed);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-screen w-screen bg-black text-white flex flex-col items-center justify-center animate-fade-in">
      <img src={logo} alt="Promethios Logo" className="w-28 mb-6 drop-shadow-xl animate-logo-glow" />
      <h1 className="text-4xl font-bold mb-4 tracking-wider">🔥 The Fire is Lit</h1>
      <p className="text-lg text-gray-400 h-8 mb-10 font-mono tracking-wide">{typedText}</p>
      <button
        onClick={() => navigate("/dashboard")}
        className="bg-white text-black px-6 py-3 rounded-xl hover:scale-105 hover:bg-gray-200 transition-all duration-200 font-semibold shadow-lg"
      >
        Enter Control Room
      </button>
    </div>
  );
}
