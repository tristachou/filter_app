import React, { useState } from 'react';
import { confirmSignUp } from '../cognitoAuth';

function ConfirmSignUpView({ username, showLogin }) {
  const [confirmationCode, setConfirmationCode] = useState('');
  const [error, setError] = useState('');

  const handleConfirmSignUp = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await confirmSignUp(username, confirmationCode);
      alert('Account confirmed successfully! You can now log in.');
      showLogin(); // Switch to the login view
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div id="confirm-view" className="view">
      <div className="card login-card">
        <h2>Confirm Your Account</h2>
        <p className="subtitle">A confirmation code has been sent to your email. Please enter it below.</p>
        <p>Confirming for: <strong>{username}</strong></p>
        <form id="confirm-form" onSubmit={handleConfirmSignUp}>
          <input
            type="text"
            placeholder="Confirmation Code"
            value={confirmationCode}
            onChange={(e) => setConfirmationCode(e.target.value)}
            required
          />
          <button type="submit" className="btn btn-primary">Confirm Account</button>
        </form>
        {error && <p className="error-message">{error}</p>}
        <p className="switch-view-link">
          <a href="#" onClick={(e) => { e.preventDefault(); showLogin(); }}>Back to Sign In</a>
        </p>
      </div>
    </div>
  );
}

export default ConfirmSignUpView;
