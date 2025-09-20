import React, { useState } from 'react';
import { useAuth } from '../AuthContext';

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
        {loginError && <p id="login-error" className="error-message">{loginError}</p>}
        <p className="switch-view-link">
          Don't have an account? <a href="#" onClick={(e) => { e.preventDefault(); showSignUp(); }}>Sign Up</a>
        </p>
      </div>
    </div>
  );
}

export default LoginView;
