import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AgentProvider } from './context/AgentContext';
import Layout from './components/Layout';
import StudentAsk from './pages/college/StudentAsk';
import MemoryLog from './pages/college/MemoryLog';

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
