function MainConsolePanel() {
  return (
    <div className="h-full bg-gray-900 border-r border-gray-800 w-full p-4">
      <div className="border-b border-gray-800 pb-4 mb-4">
        <h2 className="text-lg font-semibold">Console</h2>
      </div>
      <div className="h-[calc(100%-3rem)] overflow-y-auto">
        <div className="bg-gray-800 rounded-lg p-4 mb-4">
          <p className="text-gray-400">Welcome to Promethios Console</p>
          <p className="text-gray-400 mt-2">This is the main console panel where conversation threads will appear.</p>
        </div>
        {/* Placeholder for future console content */}
        <div className="bg-gray-800/50 rounded-lg p-4 h-64 flex items-center justify-center">
          <p className="text-gray-500">Console content will be displayed here</p>
        </div>
      </div>
    </div>
  );
}

export default MainConsolePanel;
