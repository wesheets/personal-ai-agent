import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AgentProvider } from './context/AgentContext';
import Layout from './components/Layout';

function App() {
  return (
    <AgentProvider>
      <Router>
        <Layout>
          <Routes>
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
