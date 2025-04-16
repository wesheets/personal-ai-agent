import React from 'react';
import { Navigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  // Check if user is authenticated
  const isAuthenticated = localStorage.getItem('auth_token') === 'operator_authenticated';

  // Redirect to splash page if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <header className="mb-8">
        <div className="flex items-center justify-between">
          <img src="/promethioslogo.png" alt="Promethios logo" className="h-10" />
          <button
            onClick={() => {
              localStorage.removeItem('auth_token');
              window.location.href = '/';
            }}
            className="px-4 py-2 bg-red-800 hover:bg-red-700 rounded text-sm"
          >
            Logout
          </button>
        </div>
      </header>

      <main>
        <h1 className="text-3xl font-bold mb-6">Operator Dashboard</h1>
        <p className="text-xl mb-4">Welcome to the Promethios Operator Interface</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">System Status</h2>
            <p className="text-green-400">All systems operational</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
            <p className="text-gray-300">No recent activity to display</p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
