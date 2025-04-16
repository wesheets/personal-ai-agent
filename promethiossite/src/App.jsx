import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SplashPage from './SplashPage';
import ControlRoom from './ControlRoom';
import PrivateRoute from './PrivateRoute';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SplashPage />} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <ControlRoom />
            </PrivateRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
