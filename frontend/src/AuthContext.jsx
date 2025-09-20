import React, { createContext, useContext, useState, useEffect } from 'react';
import { signIn as cognitoSignIn } from './cognitoAuth';

// 1. Create the context
const AuthContext = createContext(null);

// 2. Create the provider component
export function AuthProvider({ children }) {
  const [tokens, setTokens] = useState(null);

  // Check for tokens in localStorage on initial render
  useEffect(() => {
    const storedTokens = localStorage.getItem('authTokens');
    if (storedTokens) {
      setTokens(JSON.parse(storedTokens));
    }
  }, []);

  const login = async (username, password) => {
    try {
      const authResult = await cognitoSignIn(username, password);
      setTokens(authResult);
      localStorage.setItem('authTokens', JSON.stringify(authResult));
    } catch (error) {
      console.error('Login failed:', error);
      // Re-throw to be caught by the UI
      throw error;
    }
  };

  const logout = () => {
    setTokens(null);
    localStorage.removeItem('authTokens');
  };

  const authValue = {
    tokens,
    isAuthenticated: !!tokens,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={authValue}>
      {children}
    </AuthContext.Provider>
  );
}

// 3. Create a custom hook for easy consumption
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
