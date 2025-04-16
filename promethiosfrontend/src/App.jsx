import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AgentProvider } from './context/AgentContext';

import Splash from './Splash';
import ControlRoom from './ControlRoom';
import Layout from './components/Layout';

function App() {
  return (
    <AgentProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Splash />} />
            <Route path="/control" element={<ControlRoom />} />
          </Routes>
        </Layout>
      </Router>
    </AgentProvider>
  );
}

export default App;
