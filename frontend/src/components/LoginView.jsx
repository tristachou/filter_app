import React, { useState } from 'react';
import { useAuth } from '../AuthContext';

// --- Cognito Configuration --- //
// Note: The redirect URI must be one of the allowed callback URLs in your Cognito App Client settings
const COGNITO_DOMAIN = 'https://ap-southeast-2kdduaod7a.auth.ap-southeast-2.amazoncognito.com';
const CLIENT_ID = '4h9hjhn6bfujbskpocnd9mticd';
const REDIRECT_URI = 'http://filterapp.cab432.com/'; // Assuming this is your deployed frontend URL

function LoginView({ showSignUp }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const { login } = useAuth();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    try {
      await login(username, password);
      // On successful login, the App component will automatically re-render
      // to show the AppView, so no navigation logic is needed here.
    } catch (error) {
      setLoginError(error.message || 'Invalid credentials. Please try again.');
      console.error('Login failed:', error);
    }
  };

  const handleGoogleLogin = () => {
    const googleLoginUrl = `${COGNITO_DOMAIN}/oauth2/authorize?response_type=code&client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&identity_provider=Google`;
    window.location.href = googleLoginUrl;
  };

  return (
    <div id="login-view" className="view">
      <div className="card login-card">
        <h2>Welcome Back</h2>
        <p className="subtitle">Please sign in to continue.</p>
        <form id="login-form" onSubmit={handleLogin}>
          <input
            type="text"
            id="username"
            name="username"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            id="password"
            name="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit" className="btn btn-primary">Login</button>
        </form>
        
        <div className="divider">or</div>

        <button onClick={handleGoogleLogin} className="btn btn-google">
          <svg aria-hidden="true" width="18" height="18" viewBox="0 0 18 18" className="google-icon"><path fill="#4285F4" d="M17.64 9.20455c0-.63864-.05727-1.25182-.16818-1.84091H9.18v3.48182h4.79182c-.20864 1.125-.84409 2.07818-1.79591 2.72182v2.25818h2.90864c1.70182-1.56682 2.68364-3.87409 2.68364-6.62182z"></path><path fill="#34A853" d="M9.18 18c2.43 0 4.46727-.80591 5.95636-2.18045l-2.90864-2.25818c-.80591.54-1.84091.86182-3.04773.86182-2.34545 0-4.32864-1.58318-5.03591-3.71045H1.15773v2.33182C2.63864 15.96364 5.66182 18 9.18 18z"></path><path fill="#FBBC05" d="M4.14409 10.81c-.22273-.63591-.34909-1.32273-.34909-2.04545s.12636-1.40955.34909-2.04545V4.38727H1.15773C.42136 5.71636 0 7.29545 0 9.18s.42136 3.46364 1.15773 4.79273l2.98636-2.16273z"></path><path fill="#EA4335" d="M9.18 3.6c1.32273 0 2.50773.45591 3.44 1.34636l2.58182-2.58182C13.6436.82773 11.61.02182 9.18.02182 5.66182.02182 2.63864 2.05818 1.15773 4.40909l2.98636 2.33182C4.85136 4.82182 6.83455 3.6 9.18 3.6z"></path></svg>
          <span>Sign in with Google</span>
        </button>

        {loginError && <p id="login-error" className="error-message">{loginError}</p>}
        <p className="switch-view-link">
          Don't have an account? <a href="#" onClick={(e) => { e.preventDefault(); showSignUp(); }}>Sign Up</a>
        </p>
      </div>
    </div>
  );
}

export default LoginView;
