import { Navigate } from 'react-router-dom';

export default function PrivateRoute({ children }) {
  const isAuthenticated = localStorage.getItem('auth_token') === 'promethios-access';

  return isAuthenticated ? children : <Navigate to="/" />;
}
