import React from 'react';

// Note: The actual logic (state and handlers) will be passed down from App.jsx
// This component is primarily for rendering the UI (a "dumb" component).
function LoginView({ handleLogin, username, setUsername, password, setPassword, loginError }) {
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
      </div>
    </div>
  );
}

export default LoginView;
