import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => {
    return localStorage.getItem('ff_token') || sessionStorage.getItem('ff_token') || null;
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function initAuth() {
      const storedToken = localStorage.getItem('ff_token') || sessionStorage.getItem('ff_token');
      const storedUser = localStorage.getItem('ff_user') || sessionStorage.getItem('ff_user');

      if (storedToken) {
        setToken(storedToken);
        if (storedUser) {
          try {
            setUser(JSON.parse(storedUser));
          } catch {
            // Invalid stored JSON, will re-fetch
          }
        }
        
        try {
          const freshUser = await authService.getCurrentUser();
          setUser(freshUser);
          if (localStorage.getItem('ff_token')) {
            localStorage.setItem('ff_user', JSON.stringify(freshUser));
          } else {
            sessionStorage.setItem('ff_user', JSON.stringify(freshUser));
          }
        } catch {
          // If API fails or backend is unreachable, keep existing user if cached, or handle gracefully
          if (!storedUser) {
            // Only clear if no fallback user is present
            setToken(null);
          }
        }
      }
      setIsLoading(false);
    }

    initAuth();
  }, []);

  const login = async (credentials) => {
    const data = await authService.login(credentials);
    const authToken = data.token || data.access_token;
    if (!authToken) {
      throw new Error('Authentication failed: No token received from server.');
    }
    const authUser = data.user || {
      name: data.name || data.full_name || credentials.email.split('@')[0],
      email: credentials.email,
    };

    setToken(authToken);
    setUser(authUser);

    const storage = credentials.rememberMe ? localStorage : sessionStorage;
    storage.setItem('ff_token', authToken);
    storage.setItem('ff_user', JSON.stringify(authUser));

    return authUser;
  };

  const register = async (userData) => {
    const data = await authService.register(userData);
    return data;
  };

  const logout = () => {
    authService.logout();
    setToken(null);
    setUser(null);
  };

  const value = {
    user,
    token,
    isAuthenticated: Boolean(token),
    isLoading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
