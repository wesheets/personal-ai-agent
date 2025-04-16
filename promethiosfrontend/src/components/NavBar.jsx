import { Link } from 'react-router-dom'
import ThemeToggle from './ThemeToggle'

export default function NavBar() {
  return (
    <nav className="bg-gray-800 border-b border-gray-700 p-4 flex items-center justify-between">
      <div className="flex items-center space-x-6">
        <Link to="/" className="text-pink-400 font-bold text-xl tracking-wide">
          🔮 Promethios
        </Link>
        <Link to="/dashboard" className="text-white hover:text-pink-400 transition">
          Dashboard
        </Link>
        <Link to="/college/ask" className="text-white hover:text-pink-400 transition">
          College Ask
        </Link>
        <Link to="/college/memory" className="text-white hover:text-pink-400 transition">
          College Memory
        </Link>
      </div>
      <ThemeToggle />
    </nav>
  )
}
