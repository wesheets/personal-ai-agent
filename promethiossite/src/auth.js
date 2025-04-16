export const login = (username, password) => {
  const validUsername = import.meta.env.VITE_OPERATOR_USERNAME;
  const validPassword = import.meta.env.VITE_OPERATOR_PASSWORD;

  const isValid =
    username === validUsername && password === validPassword;

  if (isValid) {
    localStorage.setItem('auth_token', 'promethios-access');
    return true;
  }

  return false;
};

export const logout = () => {
  localStorage.removeItem('auth_token');
};

export const isAuthenticated = () => {
  return localStorage.getItem('auth_token') === 'promethios-access';
};
