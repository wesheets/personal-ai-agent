import NavBar from './NavBar';
import AgentStatusBar from './AgentStatusBar';

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col">
      <NavBar />
      <main className="flex-1 overflow-y-auto p-4">{children}</main>
      <AgentStatusBar />
    </div>
  );
}
