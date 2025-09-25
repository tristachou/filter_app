import React, { useState } from 'react';

function MfaChallengeView({ onVerify, showLogin }) {
  const [mfaCode, setMfaCode] = useState('');
  const [verifyError, setVerifyError] = useState('');

  const handleVerify = async (e) => {
    e.preventDefault();
    setVerifyError('');
    try {
      await onVerify(mfaCode); // Pass only the MFA code
      // On successful verification, the App component will handle the rest.
    } catch (error) {
      setVerifyError(error.message || 'Invalid MFA code. Please try again.');
      console.error('MFA verification failed:', error);
    }
  };

  return (
    <div id="mfa-challenge-view" className="view">
      <div className="card login-card">
        <h2>Two-Factor Authentication</h2>
        <p className="subtitle">Please enter the code from your authenticator app.</p>
        <form id="mfa-form" onSubmit={handleVerify}>
          <input
            type="text"
            id="mfaCode"
            name="mfaCode"
            placeholder="6-digit code"
            value={mfaCode}
            onChange={(e) => setMfaCode(e.target.value)}
            required
            pattern="\d{6}"
            title="Please enter a 6-digit code"
          />
          <button type="submit" className="btn btn-primary">Verify</button>
        </form>
        {verifyError && <p id="mfa-error" className="error-message">{verifyError}</p>}
        <p className="switch-view-link">
          Want to try again? <a href="#" onClick={(e) => { e.preventDefault(); showLogin(); }}>Back to Login</a>
        </p>
      </div>
    </div>
  );
}

export default MfaChallengeView;
