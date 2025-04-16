import { useState } from 'react';
import { FiSun, FiMoon } from 'react-icons/fi';

export default function ThemeToggle() {
  const [darkMode, setDarkMode] = useState(true);

  const toggle = () => {
    setDarkMode(!darkMode);
    // Placeholder toggle logic
    // You can later implement Tailwind dark mode switching or Chakra UI theme toggling
  };

  return (
    <button
      onClick={toggle}
      title="Toggle Theme"
      className="fixed bottom-5 right-5 p-3 rounded-full bg-gray-800 hover:bg-gray-700 text-white shadow-lg z-50"
    >
      {darkMode ? <FiSun /> : <FiMoon />}
    </button>
  );
}
