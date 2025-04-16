import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Splash from './Splash';
import ControlRoom from './ControlRoom';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Splash />} />
        <Route path="/control" element={<ControlRoom />} />
      </Routes>
    </Router>
  );
}

export default App;
