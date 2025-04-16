import { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    const root = window.document.documentElement;
    if (isDark) {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }, [isDark]);

  return (
    <button
      onClick={() => setIsDark(!isDark)}
      className="fixed top-4 right-4 bg-gray-800 text-white p-2 rounded-full shadow hover:bg-gray-700 transition z-50"
    >
      {isDark ? <Sun size={18} /> : <Moon size={18} />}
    </button>
  );
}
