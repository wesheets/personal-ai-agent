import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import SplashScreen from './components/splash/SplashScreen'
import OperatorConsole from './components/OperatorConsole'
import './App.css'

function App() {
  // Check if user is authenticated
  const isAuthenticated = () => {
    return localStorage.getItem('authToken') ? true : false;
  }

  // MainDashboard component that renders the OperatorConsole
  const MainDashboard = () => {
    return <OperatorConsole />;
  }

  return (
    <Router>
      <Routes>
        <Route 
          path="/" 
          element={isAuthenticated() ? <Navigate to="/console" /> : <SplashScreen />} 
        />
        <Route 
          path="/console" 
          element={isAuthenticated() ? <MainDashboard /> : <Navigate to="/" />} 
        />
      </Routes>
    </Router>
  )
}

export default App
