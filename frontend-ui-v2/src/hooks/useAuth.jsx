import { useState, createContext, useContext, useEffect } from 'react';
import { useLocation } from 'react-router-dom';

// Create auth context
const AuthContext = createContext(null);

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(localStorage.getItem('isAuthenticated') === 'true');
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user') || 'null'));
  const [loading, setLoading] = useState(true); // Add loading state
  const location = useLocation();

  // Initial auth state hydration
  useEffect(() => {
    // Initialize auth state from localStorage
    const storedAuthState = localStorage.getItem('isAuthenticated') === 'true';
    const storedUser = JSON.parse(localStorage.getItem('user') || 'null');

    setIsLoggedIn(storedAuthState);
    setUser(storedUser);
    setLoading(false); // Mark initial loading as complete
  }, []);

  // Effect to check authentication status on route change
  useEffect(() => {
    if (loading) return; // Skip if still in initial loading

    // Check localStorage on every navigation to ensure auth state is consistent
    const storedAuthState = localStorage.getItem('isAuthenticated') === 'true';
    if (storedAuthState !== isLoggedIn) {
      setIsLoggedIn(storedAuthState);
    }

    const storedUser = JSON.parse(localStorage.getItem('user') || 'null');
    if (JSON.stringify(storedUser) !== JSON.stringify(user)) {
      setUser(storedUser);
    }
  }, [location.pathname, isLoggedIn, user, loading]); // Re-run when route changes, auth state changes, or loading state changes

  // Login function
  const login = async (email, password) => {
    try {
      setLoading(true); // Set loading state during login

      // In a real app, this would make an API call
      // For now, we'll just simulate authentication with hardcoded credentials
      if (email === 'admin@promethios.ai' && password === 'ignite') {
        const userData = {
          email,
          name: 'Admin User',
          role: 'admin',
          lastLogin: new Date().toISOString()
        };

        // Store auth state in localStorage
        localStorage.setItem('isAuthenticated', 'true');
        localStorage.setItem('user', JSON.stringify(userData));

        // Update state
        setIsLoggedIn(true);
        setUser(userData);

        return true;
      } else {
        throw new Error('Invalid credentials');
      }
    } finally {
      setLoading(false); // Clear loading state after login attempt
    }
  };

  // Logout function
  const logout = () => {
    setLoading(true); // Set loading state during logout

    // Clear auth state from localStorage
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('user');
    setIsLoggedIn(false);
    setUser(null);
    
    // Use relative path for logout redirect
    window.location.href = '/auth';
    
    setLoading(false); // Clear loading state after logout
  };

  // Check if user is authenticated with localStorage as source of truth
  const isAuthenticated = () => {
    const authStatus = localStorage.getItem('isAuthenticated') === 'true';
    if (authStatus !== isLoggedIn) {
      setIsLoggedIn(authStatus);
    }
    return authStatus;
  };

  const value = {
    user,
    login,
    logout,
    isAuthenticated,
    loading // Expose loading state to consumers
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default useAuth;
