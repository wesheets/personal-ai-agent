function FileTreePanel() {
  return (
    <div className="h-full bg-gray-900 w-full p-4">
      <div className="border-b border-gray-800 pb-4 mb-4">
        <h2 className="text-lg font-semibold">Files</h2>
      </div>
      <div className="h-[calc(100%-3rem)] overflow-y-auto">
        {/* Placeholder file tree structure */}
        <div className="text-sm">
          <div className="mb-2">
            <div className="flex items-center text-gray-300 hover:text-white cursor-pointer">
              <span className="mr-1">📁</span> project
            </div>
            <div className="pl-4 mt-1">
              <div className="flex items-center text-gray-300 hover:text-white cursor-pointer mb-1">
                <span className="mr-1">📁</span> src
              </div>
              <div className="pl-4 mb-1">
                <div className="flex items-center text-gray-400 hover:text-white cursor-pointer">
                  <span className="mr-1">📄</span> main.js
                </div>
              </div>
              <div className="flex items-center text-gray-300 hover:text-white cursor-pointer mb-1">
                <span className="mr-1">📄</span> index.html
              </div>
              <div className="flex items-center text-gray-300 hover:text-white cursor-pointer">
                <span className="mr-1">📄</span> package.json
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FileTreePanel;
