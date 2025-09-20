import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import LoginView from './components/LoginView';
import AppView from './components/AppView';
import SignUpView from './components/SignUpView';
import ConfirmSignUpView from './components/ConfirmSignUpView';
import './index.css';

function App() {
  const { isAuthenticated, logout } = useAuth();
  const [viewMode, setViewMode] = useState('login'); // 'login', 'signup', or 'confirm'
  const [usernameToConfirm, setUsernameToConfirm] = useState('');

  // Handlers to switch between views
  const showSignUp = () => setViewMode('signup');
  const showLogin = () => setViewMode('login');
  
  const handleSignUpSuccess = (username) => {
    setUsernameToConfirm(username);
    setViewMode('confirm');
  };

  // If the user is authenticated, show the main app
  if (isAuthenticated) {
    return (
      <div id="app-container">
        <AppView handleLogout={logout} />
      </div>
    );
  }

  // If not authenticated, show the correct view based on viewMode
  let viewToShow;
  switch (viewMode) {
    case 'signup':
      viewToShow = <SignUpView onSignUpSuccess={handleSignUpSuccess} showLogin={showLogin} />;
      break;
    case 'confirm':
      viewToShow = <ConfirmSignUpView username={usernameToConfirm} showLogin={showLogin} />;
      break;
    default: // 'login'
      viewToShow = <LoginView showSignUp={showSignUp} />;
      break;
  }

  return (
    <div id="app-container">
      {viewToShow}
    </div>
  );
}

export default App;
