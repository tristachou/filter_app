import React, { useState } from 'react';
import { signUp } from '../cognitoAuth';

function SignUpView({ onSignUpSuccess, showLogin }) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSignUp = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await signUp(username, password, email);
      console.log('Sign up success:', response);
      // On success, call the callback passed from App.jsx to switch views
      onSignUpSuccess(username);
    } catch (err) {
      // Special handling for email limit exception to allow admin confirmation
      if (err.name === 'LimitExceededException' || err.message.includes('Exceeded daily email limit')) {
        console.warn('Cognito email limit reached. Proceeding to confirmation view for manual admin confirmation.');
        alert('Cognito email limit reached. Proceeding to confirmation view for manual admin confirmation.'); // Display alert to the user
        onSignUpSuccess(username); // Proceed as if sign-up was successful
      } else {
        setError(err.message);
      }
    }
  };

  return (
    <div id="signup-view" className="view">
      <div className="card login-card">
        <h2>Create Account</h2>
        <p className="subtitle">Let's get you started.</p>
        <form id="signup-form" onSubmit={handleSignUp}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit" className="btn btn-primary">Sign Up</button>
        </form>
        {error && <p className="error-message">{error}</p>}
        <p className="switch-view-link">
          Already have an account? <a href="#" onClick={(e) => { e.preventDefault(); showLogin(); }}>Sign In</a>
        </p>
      </div>
    </div>
  );
}

export default SignUpView;
