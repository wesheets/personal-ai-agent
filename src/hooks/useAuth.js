// src/hooks/useAuth.js
export const isAuthenticated = () => localStorage.getItem('isAuthenticated') === 'true'

export const login = () => localStorage.setItem('isAuthenticated', 'true')

export const logout = () => localStorage.removeItem('isAuthenticated')
