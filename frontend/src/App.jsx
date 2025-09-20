import React from 'react';
import { useAuth } from './AuthContext';
import LoginView from './components/LoginView';
import AppView from './components/AppView';
import './index.css';

function App() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <div id="app-container">
      {isAuthenticated ? (
        <AppView handleLogout={logout} />
      ) : (
        <LoginView />
      )}
    </div>
  );
}

export default App;
