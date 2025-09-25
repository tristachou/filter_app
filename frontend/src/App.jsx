import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import LoginView from './components/LoginView';
import AppView from './components/AppView';
import SignUpView from './components/SignUpView';
import ConfirmSignUpView from './components/ConfirmSignUpView';
import MfaChallengeView from './components/MfaChallengeView'; // Import the new component
import './index.css';

function App() {
  const { isAuthenticated, logout, mfaRequired, mfaChallenge, verifyMfa } = useAuth();
  const [viewMode, setViewMode] = useState('login'); // 'login', 'signup', or 'confirm'
  const [usernameToConfirm, setUsernameToConfirm] = useState('');

  // Handlers to switch between views
  const showSignUp = () => {
    logout(); // Reset any pending auth state
    setViewMode('signup');
  }
  const showLogin = () => {
    logout(); // Reset any pending auth state
    setViewMode('login');
  }
  
  const handleSignUpSuccess = (username) => {
    setUsernameToConfirm(username);
    setViewMode('confirm');
  };

  // If the user is fully authenticated, show the main app
  if (isAuthenticated) {
    return (
      <div id="app-container">
        <AppView handleLogout={logout} />
      </div>
    );
  }

  // If MFA is required, show the MFA challenge view regardless of other view modes
  if (mfaRequired) {
    return (
      <div id="app-container">
        <MfaChallengeView 
          onVerify={verifyMfa}
          showLogin={showLogin}
        />
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
