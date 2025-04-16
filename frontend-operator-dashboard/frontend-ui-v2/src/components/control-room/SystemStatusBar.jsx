import React, { useState, useEffect } from 'react';

const SystemStatusBar = () => {
  const [currentTime, setCurrentTime] = useState(new Date());

  // Mock values as specified in the requirements
  const systemStatus = 'Online';
  const activeAgents = ['HAL', 'ASH'];

  useEffect(() => {
    // Update the time every minute
    const intervalId = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);

    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <footer className="fixed bottom-0 w-full bg-gray-200 text-sm px-4 py-2 flex justify-between items-center border-t border-gray-300">
      <div className="flex items-center">
        <span className="mr-2">Status:</span>
        <span className="flex items-center">
          <span className="h-2 w-2 rounded-full bg-green-500 mr-1"></span>
          {systemStatus}
        </span>
      </div>

      <div className="flex items-center">
        <span className="mr-2">Agents Active:</span>
        <span>{activeAgents.join(', ')}</span>
      </div>

      <div className="flex items-center">
        <span className="mr-2">Last Ping:</span>
        <span>{formatTime(currentTime)}</span>
      </div>
    </footer>
  );
};

export default SystemStatusBar;
