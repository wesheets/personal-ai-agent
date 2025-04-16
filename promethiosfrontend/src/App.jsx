import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AgentProvider } from './context/AgentContext';
import Layout from './components/Layout';

// Try/catch dynamic imports for optional pages
let StudentAsk, MemoryLog;

try {
  StudentAsk = require('./pages/college/StudentAsk').default;
} catch {
  StudentAsk = () => <div>StudentAsk page coming soon!</div>;
}

try {
  MemoryLog = require('./pages/college/MemoryLog').default;
} catch {
  MemoryLog = () => <div>MemoryLog page coming soon!</div>;
}

function App() {
  return (
    <AgentProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/college/ask" element={<StudentAsk />} />
            <Route path="/college/memory" element={<MemoryLog />} />
            <Route
              path="/"
              element={<div className="text-center p-10">Welcome to Promethios</div>}
            />
          </Routes>
        </Layout>
      </Router>
    </AgentProvider>
  );
}

export default App;
