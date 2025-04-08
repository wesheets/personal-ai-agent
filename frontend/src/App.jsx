import React from 'react';
import { Routes, Route } from 'react-router-dom';
import AgentRoute from './pages/AgentRoute';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/agent/:agentId" element={<AgentRoute />} />
        {/* Other routes will be here */}
      </Routes>
    </div>
  );
}

export default App;
